"""
@file matter_sim.py
@brief pyrenode3 harness for the Matter Renode simulation.

Configures PYRENODE_PATH from the assembled bundle, drives Renode monitor/resc scripts,
and exposes UART testers for the simulated Matter hub and SoC.
"""

from __future__ import annotations

import os
import re
import socket
from contextlib import ExitStack
from pathlib import Path

DEFAULT_BUNDLE = Path(__file__).resolve().parent.parent / "out" / "bundle"
DEFAULT_UART_TIMEOUT_S = 600


def resolve_renode(bundle_dir: Path) -> Path:
    """Return the Renode binary from the assembled bundle."""
    candidate = bundle_dir.resolve() / "renode" / "renode"
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(
        f"renode binary not found at {candidate}, run scripts/fetch_bundle.py or scripts/assemble_bundle.py"
    )


def configure_renode_env(bundle_dir: Path) -> None:
    """Point pyrenode3 and test_lib at the portable Renode tree under ``bundle_dir/renode``."""
    bundle_dir = bundle_dir.resolve()
    renode_root = bundle_dir / "renode"
    os.environ["PYRENODE_PATH"] = str(resolve_renode(bundle_dir))
    os.environ["RENODE_BASE_PATH"] = str(renode_root) + os.sep


def _bootstrap_default_renode_env() -> None:
    if os.environ.get("PYRENODE_PATH"):
        return
    renode_bin = DEFAULT_BUNDLE / "renode" / "renode"
    if renode_bin.is_file():
        configure_renode_env(DEFAULT_BUNDLE)


_bootstrap_default_renode_env()

import test_lib


def _register_uart_tester(
    emulation: object,
    machine_name: str,
    uart_peripheral: object,
    timeout_s: float,
) -> object:
    """Attach a TerminalTester and register it with test_lib for I/O and CLI logging."""
    from pyrenode3.wrappers import TerminalTester

    machine = emulation.get_mach(machine_name)
    if machine is None:
        raise RuntimeError(f"{machine_name} machine not found")
    tester = TerminalTester(uart_peripheral, timeout_s)
    test_lib._machine_name_to_machine_mapping[machine_name] = machine
    test_lib._tester_to_machine_mapping[tester] = machine
    test_lib._tester_to_uart_mapping[tester] = uart_peripheral.internal
    test_lib.enable_cli_logging(tester, True)
    return tester


def _unregister_uart_tester(tester: object, machine_name: str) -> None:
    test_lib.enable_cli_logging(tester, False)
    test_lib._tester_to_machine_mapping.pop(tester, None)
    test_lib._tester_to_uart_mapping.pop(tester, None)
    test_lib._machine_name_to_machine_mapping.pop(machine_name, None)


def login_root(tester: object, timeout_s: float = DEFAULT_UART_TIMEOUT_S) -> None:
    """Log in to the Buildroot console as root."""
    test_lib.wait_for(tester, r"buildroot login:", timeout=timeout_s)
    test_lib.write_line(tester, "root")
    test_lib.wait_for(tester, r"#\s*$", timeout=timeout_s)


def run_shell(tester: object, cmd: str, timeout_s: float = DEFAULT_UART_TIMEOUT_S) -> tuple[int, str]:
    """Run a shell command on the guest and return its exit code and UART transcript."""
    tester.ClearReport()
    test_lib.write_line(tester, f'{cmd}; echo "__RC=$?"')
    matched = test_lib.wait_for(tester, r"^__RC=(\d+)\r?$", timeout=timeout_s, endline=True)
    report = str(tester.GetReport())
    line_match = re.search(r"__RC=(\d+)", matched) if matched else None
    if line_match is not None:
        return int(line_match.group(1)), report
    raise RuntimeError(f"missing command exit status in console response\n{report[-2000:]}")


class MatterSim:
    """In-process Renode session, optionally exposing TCP consoles for manual use."""

    def __init__(self, bundle_dir: Path, *, socket_consoles: bool = True) -> None:
        self.bundle_dir = bundle_dir.resolve()
        self._socket_consoles = socket_consoles
        configure_renode_env(self.bundle_dir)
        from pyrenode3.wrappers import Emulation, Monitor

        self._emulation = Emulation()
        self._monitor = Monitor()
        test_lib._e = self._emulation
        test_lib._m = self._monitor
        self._uart_testers: list[tuple[object, str]] = []
        self._console_ports: set[int] = set()

    def load(self, resc: str, variables: dict[str, str] | None = None) -> None:
        """Set monitor variables, then include ``resc/<resc>`` from the bundle."""
        for key, value in (variables or {}).items():
            test_lib.execute_monitor_command(f"${key} = @{value}")
        resc_path = self.bundle_dir / "resc" / resc
        test_lib.execute_monitor_command(f"include @{resc_path}")

    def load_thread_checkpoint(
        self,
        *,
        checkpoint: Path | None = None,
        hub_console_port: int = 4540,
    ) -> None:
        """Load the Thread hub checkpoint and optionally expose its TCP console."""
        ckpt = (checkpoint or self.bundle_dir / "linux-booted-thread.save").resolve()
        if not ckpt.is_file():
            raise FileNotFoundError(f"checkpoint not found: {ckpt}")
        test_lib.execute_monitor_command(f"EmulationManager Load @{ckpt}")
        test_lib.execute_monitor_command(f"path add @{self.bundle_dir / 'renode'}")
        test_lib.execute_monitor_command("logLevel 3")
        test_lib.execute_monitor_command('mach set "matter_hub"')
        if self._socket_consoles:
            test_lib.execute_monitor_command(
                f'emulation CreateServerSocketTerminal {hub_console_port} "matter_hub_console" false'
            )
            self._console_ports.add(hub_console_port)
            test_lib.execute_monitor_command("connector Connect sysbus.uart1 matter_hub_console")
        test_lib.execute_monitor_command('mach set "matter_hub"')
        test_lib.execute_monitor_command("start")

    def attach_matter_soc(
        self,
        board: str,
        elf_path: Path | str,
        *,
        machine_name: str = "matter_soc",
        cli_port: int = 3452,
        uart: str = "eusart0",
        extra_hex: Path | str | None = None,
    ) -> None:
        """Add a Matter SoC after the hub checkpoint is loaded."""
        board_name = board.removesuffix(".repl")
        repl = f"platforms/boards/silabs/{board_name}.repl"
        if not (Path(test_lib.renode_base_path()) / repl).is_file():
            raise FileNotFoundError(f"board REPL not found: {repl}")

        elf = Path(elf_path).resolve()
        cli_name = f"matter_cli_{machine_name}"
        hex_path = Path(extra_hex).resolve() if extra_hex is not None else None

        steps = [
            f'mach create "{machine_name}"',
            "using sysbus",
            f"machine LoadPlatformDescription @{repl}",
            f"sysbus LoadELF @{elf}",
            *( [f"sysbus LoadHEX @{hex_path}"] if hex_path else [] ),
            'cpu VectorTableOffset `sysbus GetSymbolAddress "__Vectors"`',
            "cpu PerformanceInMips 50",
            "connector Connect sysbus.radio wireless",
            "connector Connect sysbus.radio ble",
        ]
        if self._socket_consoles:
            steps.extend([
                f'emulation CreateServerSocketTerminal {cli_port} "{cli_name}" false',
                f"connector Connect sysbus.{uart} {cli_name}",
            ])
        for cmd in steps:
            test_lib.execute_monitor_command(cmd)
            if cmd.startswith("emulation CreateServerSocketTerminal "):
                self._console_ports.add(cli_port)

    def pause(self) -> None:
        """Pause all machines while attaching devices and UART testers."""
        test_lib.execute_monitor_command("pause")

    def start(self) -> None:
        """Start or resume all machines."""
        test_lib.execute_monitor_command("start")

    def attach_provision_image(self, image_path: Path | None = None) -> None:
        """Load a provisioning disk into the restored hub's provision_virtio device.

        The checkpoint must already contain the provisioning virtio device and
        guest DTB node. Mount the disk with mount_provision after attachment.
        """
        image = (image_path or self.bundle_dir / "guest-rootfs" / "matter-provision.ext2").resolve()
        if not image.is_file():
            raise FileNotFoundError(f"provisioning image not found: {image}")
        test_lib.execute_monitor_command('mach set "matter_hub"')
        test_lib.execute_monitor_command(f"provision_virtio LoadImage @{image}")

    def mount_provision(self, tester: object, timeout_s: float = DEFAULT_UART_TIMEOUT_S) -> None:
        """Mount the provisioning disk on the hub after attach_provision_image()."""
        rc, report = run_shell(tester, "matter-provision-mount", timeout_s)
        if rc != 0:
            raise RuntimeError(f"matter-provision-mount failed (rc={rc})\n{report[-2000:]}")

    def hub_uart(self, timeout_s: float = DEFAULT_UART_TIMEOUT_S) -> object:
        """Attach a tester to matter_hub uart1.

        ``EmulationManager Load`` replaces the emulation, so this always
        resolves the machine and UART again.
        """
        machine = self._emulation.get_mach("matter_hub")
        if machine is None:
            raise RuntimeError("matter_hub machine not found")
        tester = _register_uart_tester(self._emulation, "matter_hub", machine.sysbus.uart1, timeout_s)
        self._uart_testers.append((tester, "matter_hub"))
        return tester

    def soc_uart(
        self,
        timeout_s: float = DEFAULT_UART_TIMEOUT_S,
        *,
        machine_name: str = "matter_soc",
    ) -> object:
        """Attach a tester to a Matter SoC eusart0 (default ``matter_soc``)."""
        machine = self._emulation.get_mach(machine_name)
        if machine is None:
            raise RuntimeError(f"{machine_name} machine not found")
        tester = _register_uart_tester(
            self._emulation, machine_name, machine.sysbus.eusart0, timeout_s
        )
        self._uart_testers.append((tester, machine_name))
        return tester

    def save(self, path: Path) -> None:
        """Pause the emulation and write a checkpoint."""
        destination = path.resolve()
        test_lib.execute_monitor_command("pause")
        test_lib.execute_monitor_command(f"Save @{destination}")
        if not destination.is_file() or destination.stat().st_size == 0:
            raise RuntimeError(f"checkpoint file was not created: {destination}")

    def close(self) -> None:
        """Drop the current emulation."""
        for tester, machine_name in self._uart_testers:
            _unregister_uart_tester(tester, machine_name)
        self._uart_testers.clear()
        with ExitStack() as consoles:
            for port in self._console_ports:
                try:
                    consoles.enter_context(socket.create_connection(("127.0.0.1", port), timeout=1))
                except OSError:
                    pass
            self._emulation.clear()
        self._console_ports.clear()
