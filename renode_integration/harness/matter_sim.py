"""
@file matter_sim.py
@brief pyrenode3 harness for the Matter Renode simulation.

Configures PYRENODE_PATH from the assembled bundle, builds the hub topology, drives Renode
monitor/resc scripts, and exposes UART testers for the simulated Matter hub and SoC.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

DEFAULT_BUNDLE = Path(__file__).resolve().parent.parent / "out" / "bundle"
DEFAULT_UART_TIMEOUT_S = 600
HUB_CONSOLE_PORT = 4540

# ZynqMP guest boot firmware (ATF, U-Boot, Linux) for the matter_hub machine
_FW = "https://dl.antmicro.com/projects/renode"
ATF_ELF = f"{_FW}/zynq-us_plus--bl31.elf-s_770984-aad9c28d989600caa8fd436bca66eb500e0606dd"
UBOOT_BIN = f"{_FW}/zynq-us_plus--u-boot.bin-s_1351888-8291c2fd5e7fed3bda101e4c0694991fb40af277"
UBOOT_ELF = f"{_FW}/zynq-us_plus--u-boot.elf-s_1418000-23d4b0115d096ce9ed85c7e146f687a528382326"
LINUX_BIN = f"{_FW}/Image-s_22458880-2573cb5cd76576081947b8ec1aebcf631b6d4bb6"
LINUX_ELF = f"{_FW}/vmlinux-s_28175880-4d25e9de8b56d28e76e3a58e1a45089ac08c4cd5"
LINUX_BOOTARGS = "earlycon console=ttyPS1,115200n8 root=/dev/ram0 rw initrd=0x20000000,64M maxcpus=1 idle=halt"


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


def _rcp_commands(name: str, elf: Path, uart_hub: str, medium: str) -> list[str]:
    return [
        f'mach create "{name}"',
        "using sysbus",
        "machine LoadPlatformDescription @platforms/boards/silabs/brd4186c.repl",
        f"sysbus LoadELF @{elf}",
        'cpu VectorTableOffset `sysbus GetSymbolAddress "__Vectors"`',
        "cpu PerformanceInMips 50",
        f"connector Connect sysbus.usart0 {uart_hub}",
        f"connector Connect sysbus.radio {medium}",
        "logLevel 3",
        "mach clear",
    ]


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

    def load(self, resc: str, variables: dict[str, str] | None = None) -> None:
        """Set monitor variables, then include ``resc/<resc>`` from the bundle."""
        for key, value in (variables or {}).items():
            test_lib.execute_monitor_command(f"${key} = @{value}")
        resc_path = self.bundle_dir / "resc" / resc
        test_lib.execute_monitor_command(f"include @{resc_path}")

    def boot(self) -> None:
        """Create the hub and RCP machines and cold-boot the hub Linux guest."""
        guest = self.bundle_dir / "guest-rootfs"
        rcp = self.bundle_dir / "rcp"
        commands = [
            "emulation SetGlobalSerialExecution true",
            'emulation CreateIEEE802_15_4Medium "wireless"',
            'emulation CreateBLEMedium "ble"',
            'emulation CreateSwitch "backbone"',
            'emulation SetGlobalQuantum "0.000020"',
            'emulation CreateUARTHub "spinel"',
            'emulation CreateUARTHub "hci"',
            # matter_hub: uart0 -> spinel (Thread RCP), uart2 -> hci (BLE RCP), uart1 -> console
            'mach create "matter_hub"',
            "machine RealTimeClockMode HostTimeUTC",
            "using sysbus.cluster0",
            "using sysbus.cluster1",
            "machine LoadPlatformDescription @platforms/boards/silabs/matter_hub.repl",
            "machine SetSerialExecution true",
            f'emulation CreateServerSocketTerminal {HUB_CONSOLE_PORT} "matter_hub_console" false',
            "connector Connect sysbus.uart1 matter_hub_console",
            # Pace UART TX at the 8N1 wire rate so the EFR32 USART RX buffer is not overrun
            "sysbus.uart0 CharacterTransmitDelayMicroseconds 22",
            "sysbus.uart2 CharacterTransmitDelayMicroseconds 87",
            "connector Connect sysbus.uart0 spinel",
            "connector Connect sysbus.uart2 hci",
            "connector Connect gem3 backbone",
            "mach clear",
            *_rcp_commands("thread_rcp", rcp / "ot-rcp.out", "spinel", "wireless"),
            *_rcp_commands("ble_rcp", rcp / "bt_rcp_freertos.out", "hci", "ble"),
            'mach set "matter_hub"',
            "apu0 PC 0x1000000",
            "cluster0 ForEach IsHalted true",
            "apu0 IsHalted false",
            "cluster1 ForEach IsHalted true",
            f"sysbus LoadELF @{ATF_ELF} cpu=apu0",
            f'sysbus LoadFdt @{guest / "zynqmp-matter-linux.dtb"} 0x100000 "{LINUX_BOOTARGS}" false',
            f"sysbus LoadBinary @{UBOOT_BIN} 0x8000000",
            f"sysbus LoadBinary @{LINUX_BIN} 0x10000000",
            f"sysbus LoadBinary @{guest / 'matter-rootfs.ext2'} 0x20000000",
            f"matter_virtio LoadImage @{guest / 'matter-tools.ext2'}",
            f"sysbus LoadSymbolsFrom @{UBOOT_ELF}",
            f"sysbus LoadSymbolsFrom @{LINUX_ELF}",
            "start",
        ]
        for command in commands:
            test_lib.execute_monitor_command(command)

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
        self._emulation.clear()
