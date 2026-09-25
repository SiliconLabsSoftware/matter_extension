"""Socket-based harness for driving Renode Matter simulation."""

from __future__ import annotations

import os
import re
import socket
import subprocess
import time
from contextlib import closing
from pathlib import Path
from typing import Optional


class RenodeHarness:
    def __init__(
        self,
        renode_bin: Path,
        resc: Path,
        bundle_dir: Path,
        monitor_port: int = 3333,
        hub_console_port: int = 4540,
    ):
        self.renode_bin = renode_bin
        self.resc = resc
        self.bundle_dir = bundle_dir
        self.monitor_port = monitor_port
        self.hub_console_port = hub_console_port
        self.process: Optional[subprocess.Popen] = None

    def start(self, extra_env: dict | None = None) -> None:
        env = os.environ.copy()
        env.update(extra_env or {})
        cmd = [
            str(self.renode_bin),
            "--disable-gui",
            "--hide-log",
            "-P",
            str(self.monitor_port),
            str(self.resc),
        ]
        self.process = subprocess.Popen(
            cmd,
            cwd=str(self.bundle_dir),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def stop(self) -> None:
        if self.process is None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=10)
        self.process = None

    def _wait_for_port(self, port: int, timeout_s: float = 300.0) -> None:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            try:
                with closing(socket.create_connection(("127.0.0.1", port), timeout=1)):
                    return
            except OSError:
                if self.process and self.process.poll() is not None:
                    raise RuntimeError(f"Renode exited early with code {self.process.returncode}")
                time.sleep(0.5)
        raise TimeoutError(f"port {port} not ready within {timeout_s}s")

    def monitor_command(self, command: str, timeout_s: float = 120.0) -> str:
        self._wait_for_port(self.monitor_port, timeout_s)
        with closing(socket.create_connection(("127.0.0.1", self.monitor_port), timeout=timeout_s)) as sock:
            sock.settimeout(timeout_s)
            self._read_until_prompt(sock)
            sock.sendall((command + "\n").encode())
            return self._read_until_prompt(sock)

    def _read_until_prompt(self, sock: socket.socket) -> str:
        chunks = []
        while True:
            try:
                data = sock.recv(4096)
            except socket.timeout:
                combined = "".join(chunks)
                if not _MONITOR_PROMPT.search(combined):
                    raise TimeoutError("monitor prompt not received before timeout")
                break
            if not data:
                break
            chunks.append(data.decode(errors="replace"))
            if _MONITOR_PROMPT.search("".join(chunks)):
                break
        return "".join(chunks)

    def hub_console_session(self, timeout_s: float = 600.0):
        self._wait_for_port(self.hub_console_port, timeout_s)
        sock = socket.create_connection(("127.0.0.1", self.hub_console_port), timeout=timeout_s)
        sock.settimeout(1.0)
        return _ConsoleSession(sock, timeout_s)


_MONITOR_PROMPT = re.compile(r"\([^)\r\n]+\)\s*$")


class _ConsoleSession:
    def __init__(self, sock: socket.socket, timeout_s: float):
        self.sock = sock
        self.timeout_s = timeout_s
        self.buffer = ""

    def close(self) -> None:
        self.sock.close()

    def _read_more(self) -> None:
        try:
            data = self.sock.recv(4096)
        except socket.timeout:
            return
        if not data:
            return
        self.buffer += data.decode(errors="replace")

    def wait_for_line(self, pattern: str, timeout_s: Optional[float] = None) -> str:
        regex = re.compile(pattern)
        deadline = time.time() + (timeout_s or self.timeout_s)
        while time.time() < deadline:
            match = regex.search(self.buffer)
            if match:
                matched = self.buffer[: match.end()]
                self.buffer = self.buffer[match.end() :]
                return matched
            self._read_more()
            time.sleep(0.1)
        raise TimeoutError(f"timed out waiting for /{pattern}/ in console output")

    def send_line(self, text: str) -> None:
        self.sock.sendall((text + "\n").encode())

    def login_root(self) -> None:
        self.wait_for_line(r"buildroot login:", timeout_s=300)
        self.send_line("root")
        self.wait_for_line(r"#\s*$", timeout_s=30)

    def run_and_wait(self, command: str, ready_pattern: str, timeout_s: Optional[float] = None) -> str:
        self.send_line(command)
        return self.wait_for_line(ready_pattern, timeout_s=timeout_s)

    def save_checkpoint(self, harness: RenodeHarness, path: Path) -> None:
        harness.monitor_command("pause")
        harness.monitor_command(f'Save @{path}')
        harness.monitor_command("start")
