"""pyrenode3 harness for the Matter Renode simulation."""

from __future__ import annotations

import os
import re
from pathlib import Path

DEFAULT_BUNDLE = Path(__file__).resolve().parent.parent / "out" / "bundle"


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


class MatterSim:
    """In-process Renode session for one bundle directory."""

    def __init__(self, bundle_dir: Path) -> None:
        self.bundle_dir = bundle_dir.resolve()
        configure_renode_env(self.bundle_dir)
        from pyrenode3.wrappers import Emulation, Monitor

        self._emulation = Emulation()
        self._monitor = Monitor()
        test_lib._e = self._emulation
        test_lib._m = self._monitor
        self._consoles: list[tuple[Console, str]] = []

    def load(self, resc: str, variables: dict[str, str] | None = None) -> None:
        """Set monitor variables, then include ``resc/<resc>`` from the bundle."""
        for key, value in (variables or {}).items():
            self.execute(f"${key} = @{value}")
        resc_path = self.bundle_dir / "resc" / resc
        self.execute(f"include @{resc_path}")

    def execute(self, cmd: str) -> str:
        """Run a monitor command and return its output.

        Raises:
            RuntimeError: The monitor reported an error.
        """
        output = test_lib.execute_monitor_command(cmd)
        return "" if output is None else str(output)

    def hub_console(self, timeout_s: float = 600) -> Console:
        """Attach a tester to matter_hub uart1.

        ``EmulationManager Load`` replaces the emulation, so this always
        resolves the machine and UART again.
        """
        machine = self._emulation.get_mach("matter_hub")
        if machine is None:
            raise RuntimeError("matter_hub machine not found")
        tester = _register_uart_tester(self._emulation, "matter_hub", machine.sysbus.uart1, timeout_s)
        console = Console(tester, timeout_s)
        self._consoles.append((console, "matter_hub"))
        return console

    def soc_console(self, timeout_s: float = 600) -> Console:
        """Attach a tester to matter_soc eusart0.

        The resc script also connects this UART to a socket. The tester records
        the lighting app console from the moment it is attached.
        """
        machine = self._emulation.get_mach("matter_soc")
        if machine is None:
            raise RuntimeError("matter_soc machine not found")
        tester = _register_uart_tester(self._emulation, "matter_soc", machine.sysbus.eusart0, timeout_s)
        console = Console(tester, timeout_s)
        self._consoles.append((console, "matter_soc"))
        return console

    def save(self, path: Path) -> None:
        """Pause the emulation and write a checkpoint."""
        destination = path.resolve()
        self.execute("pause")
        self.execute(f"Save @{destination}")
        if not destination.is_file() or destination.stat().st_size == 0:
            raise RuntimeError(f"checkpoint file was not created: {destination}")

    def close(self) -> None:
        """Drop the current emulation."""
        for console, machine_name in self._consoles:
            _unregister_uart_tester(console._tester, machine_name)
        self._consoles.clear()
        self._emulation.clear()


class Console:
    """UART session backed by Renode's TerminalTester and test_lib I/O helpers."""

    def __init__(self, tester: object, timeout_s: float) -> None:
        self._tester = tester
        self._timeout_s = timeout_s

    def wait_for(self, pattern: str, timeout_s: float | None = None) -> str:
        """Wait until ``pattern`` matches UART text, including a partial line.

        Raises:
            RuntimeError: The pattern was not seen before the timeout.
        """
        limit = self._timeout_s if timeout_s is None else timeout_s
        return test_lib.wait_for(self._tester, pattern, timeout=limit)

    def write_line(self, text: str) -> None:
        """Send ``text`` and a carriage return to the UART."""
        test_lib.write_line(self._tester, text)

    def login_root(self) -> None:
        """Log in to the Buildroot console as root."""
        self.wait_for(r"buildroot login:")
        self.write_line("root")
        self.wait_for(r"#\s*$")

    def get_report(self) -> str:
        """Return the full UART transcript from the tester."""
        return str(self._tester.GetReport())

    def run(self, cmd: str, timeout_s: float | None = None) -> tuple[int, str]:
        """Run a shell command on the guest and return its exit code and UART transcript."""
        self.write_line(f'{cmd}; echo "__RC=$?"')
        matched = self.wait_for(r"__RC=(\d+)", timeout_s=timeout_s)
        report = self.get_report()
        line_match = re.search(r"__RC=(\d+)", matched) if matched else None
        if line_match is not None:
            return int(line_match.group(1)), report
        rc_matches = re.findall(r"__RC=(\d+)", report)
        if not rc_matches:
            raise RuntimeError(f"could not parse exit code from console output\n{report[-2000:]}")
        return int(rc_matches[-1]), report
