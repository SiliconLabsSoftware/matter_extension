"""pyrenode3 harness for the Matter Renode simulation."""

from __future__ import annotations

import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
INTEGRATION_DIR = SCRIPT_DIR.parent


def resolve_renode(bundle_dir: Path) -> Path:
    """Return the Renode binary for this host.

    ``RENODE`` overrides discovery. Otherwise look in the bundle, then in the
    per-host build output.
    """
    override = os.environ.get("RENODE")
    if override:
        return Path(override)
    host = os.environ.get("HOST")
    if not host:
        uname = os.uname()
        if uname.sysname == "Darwin" and uname.machine == "arm64":
            host = "osx-arm64"
        elif uname.sysname == "Linux" and uname.machine in ("x86_64", "amd64"):
            host = "linux-x64"
        else:
            host = f"{uname.sysname.lower()}-{uname.machine}"
    candidate = bundle_dir / "renode" / "renode"
    if candidate.exists():
        return candidate
    built = INTEGRATION_DIR / "out" / "renode" / host / "renode"
    if built.exists():
        return built
    raise FileNotFoundError("renode binary not found, run scripts/build_renode.py or set RENODE=")


class MatterSim:
    """In-process Renode session for one bundle directory."""

    def __init__(self, bundle_dir: Path) -> None:
        self.bundle_dir = bundle_dir.resolve()
        # pyrenode3 reads PYRENODE_PATH at import time.
        os.environ["PYRENODE_PATH"] = str(resolve_renode(self.bundle_dir))
        from pyrenode3.wrappers import Emulation, Monitor, TerminalTester

        self._terminal_tester = TerminalTester
        self._emulation = Emulation()
        self._monitor = Monitor()

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
        contents, error = self._monitor.execute(cmd)
        output = "" if contents is None else str(contents)
        error_text = "" if error is None else str(error)
        if error_text.strip():
            raise RuntimeError(f"monitor command failed: {cmd}\n{error_text}\n{output}")
        return output

    def hub_console(self, timeout_s: float = 600) -> Console:
        """Attach a tester to matter_hub uart1.

        ``EmulationManager Load`` replaces the emulation, so this always
        resolves the machine and UART again.
        """
        machine = self._emulation.get_mach("matter_hub")
        if machine is None:
            raise RuntimeError("matter_hub machine not found")
        tester = self._terminal_tester(machine.sysbus.uart1, timeout_s)
        return Console(tester, timeout_s)

    def save(self, path: Path) -> None:
        """Pause the emulation and write a checkpoint."""
        destination = path.resolve()
        self.execute("pause")
        self.execute(f"Save @{destination}")
        if not destination.is_file() or destination.stat().st_size == 0:
            raise RuntimeError(f"checkpoint file was not created: {destination}")

    def close(self) -> None:
        """Drop the current emulation."""
        self._emulation.clear()


class Console:
    """UART session backed by Renode's TerminalTester."""

    def __init__(self, tester: object, timeout_s: float) -> None:
        self._tester = tester
        self._timeout_s = timeout_s

    def wait_for(self, pattern: str, timeout_s: float | None = None) -> str:
        """Wait until ``pattern`` matches UART text, including a partial line.

        Raises:
            TimeoutError: The pattern was not seen before the timeout.
        """
        from pyrenode3.wrappers import TerminalTester

        limit = self._timeout_s if timeout_s is None else timeout_s
        result = self._tester.WaitFor(pattern, TerminalTester.to_interval(limit), True, True)
        if result is None:
            report = str(self._tester.GetReport())
            raise TimeoutError(f"timed out waiting for /{pattern}/\n{report[-2000:]}")
        line = result.Line
        return "" if line is None else str(line)

    def write_line(self, text: str) -> None:
        """Send ``text`` and a carriage return to the UART."""
        self._tester.WriteLine(text)

    def login_root(self) -> None:
        """Log in to the Buildroot console as root."""
        self.wait_for(r"buildroot login:")
        self.write_line("root")
        self.wait_for(r"#\s*$")
