#!/usr/bin/env python3
"""SSH wrapper to run chip-tool and ot-ctl on a Silicon Labs Matter Hub."""

from __future__ import annotations

import argparse
import json
import random
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Sequence

HUB_USER = "ubuntu"
CHIP_TOOL = "/home/ubuntu/connectedhomeip/out/standalone/chip-tool"
LAST_NODE_ID_REMOTE = "/tmp/last-node-id"

# Non-interactive SSH: key auth only
SSH_OPTS = (
    "-o",
    "BatchMode=yes",
    "-o",
    "ConnectTimeout=10",
    "-o",
    "StrictHostKeyChecking=accept-new",
)

COMMISSION_TIMEOUT_S = 180
DEFAULT_PIN = "20202021"
DEFAULT_DISCRIMINATOR = "3840"

HUB_SCRIPT = "python3 .cursor/skills/chip-tool/scripts/hub.py"

# Shown when config is missing or SSH key auth fails
HUB_SETUP_STEPS = f"""\
One-time setup (user runs in a terminal, agent must not):
  1. ssh ubuntu@HOST
  2. Install your SSH public key on the hub (same HOST):
       Linux/macOS: ssh-copy-id ubuntu@HOST
       Windows (OpenSSH): ssh-copy-id ubuntu@HOST if available, else append your
       public key to ~ubuntu/.ssh/authorized_keys on the Pi
  3. {HUB_SCRIPT} discover --host HOST
     (on Windows, use python instead of python3 if needed)
Replace HOST with the Matter Hub IP.
"""


def print_user_setup(reason: str) -> None:
    """Emit a one-line reason plus the full user setup instructions."""
    print(f"{reason}\n{HUB_SETUP_STEPS}", file=sys.stderr)


def config_path() -> Path:
    return Path.home() / ".silabs" / "matter-hub.json"


def load_saved_host() -> Optional[str]:
    path = config_path()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    host = data.get("host")
    return str(host).strip() if host else None


def save_host(host: str) -> None:
    """Persist hub address. Only ``discover --host`` should call this."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"host": host}, indent=2) + "\n", encoding="utf-8")


def ssh_base(host: str) -> List[str]:
    return ["ssh", *SSH_OPTS, f"{HUB_USER}@{host}", "--"]


def run_ssh(
    host: str,
    remote_argv: Sequence[str],
    *,
    timeout: Optional[float] = None,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    cmd = ssh_base(host) + list(remote_argv)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=check,
    )


def print_proc(proc: subprocess.CompletedProcess[str]) -> int:
    if proc.stdout:
        sys.stdout.write(proc.stdout)
        if not proc.stdout.endswith("\n"):
            sys.stdout.write("\n")
    if proc.stderr:
        sys.stderr.write(proc.stderr)
        if not proc.stderr.endswith("\n"):
            sys.stderr.write("\n")
    return proc.returncode


def auth_failed(proc: subprocess.CompletedProcess[str]) -> bool:
    combined = (proc.stderr or "") + (proc.stdout or "")
    return proc.returncode != 0 and (
        "Permission denied" in combined
        or "Host key verification failed" in combined
        or "Authentication failed" in combined
    )


def ssh_conn_failed(proc: subprocess.CompletedProcess[str]) -> bool:
    """Check if SSH failed due to connection issues (timeout, refused, bad host)."""
    stderr = proc.stderr or ""
    return proc.returncode != 0 and (
        "Connection timed out" in stderr
        or "Connection refused" in stderr
        or "Could not resolve hostname" in stderr
        or "No route to host" in stderr
        or "Network is unreachable" in stderr
    )


def require_host() -> str:
    """Load host from JSON. Exit with setup help if config is missing."""
    host = load_saved_host()
    if not host:
        print_user_setup("No Matter Hub host in ~/.silabs/matter-hub.json.")
        sys.exit(1)
    return host


def cmd_discover(args: argparse.Namespace) -> int:
    """User setup: ``--host`` writes JSON. Without ``--host``, print saved host."""
    if args.host:
        host = args.host.strip()
        proc = run_ssh(host, ["test", "-x", CHIP_TOOL])
        if auth_failed(proc):
            print_user_setup("SSH key auth failed.")
            return 1
        if ssh_conn_failed(proc):
            print(f"SSH connection to {host} failed.", file=sys.stderr)
            return print_proc(proc) or 1
        if proc.returncode != 0:
            print(f"{host} is not a Matter Hub (chip-tool missing).", file=sys.stderr)
            return 1
        save_host(host)
        print(host)
        return 0

    saved = load_saved_host()
    if saved:
        print(saved)
        return 0
    print_user_setup("No Matter Hub host in ~/.silabs/matter-hub.json.")
    return 1


def cmd_check(args: argparse.Namespace) -> int:
    """Agent entry: confirm key auth, chip-tool, and passwordless ``ot-ctl``."""
    host = require_host()
    proc = run_ssh(host, ["test", "-x", CHIP_TOOL])
    if auth_failed(proc):
        print_user_setup("SSH key auth failed.")
        return 1
    if ssh_conn_failed(proc):
        print(f"SSH connection to {host} failed.", file=sys.stderr)
        return print_proc(proc) or 1
    if proc.returncode != 0:
        print(f"chip-tool not found at {CHIP_TOOL}", file=sys.stderr)
        return 1

    proc = run_ssh(host, ["sudo", "-n", "ot-ctl", "state"])
    if proc.returncode != 0:
        print("sudo -n ot-ctl state failed. Passwordless sudo for ot-ctl is required.", file=sys.stderr)
        return print_proc(proc) or 1

    print(f"host={host}")
    return print_proc(proc)


def cmd_dataset(args: argparse.Namespace) -> int:
    host = require_host()
    proc = run_ssh(host, ["sudo", "-n", "ot-ctl", "dataset", "active", "-x"])
    if auth_failed(proc):
        print_user_setup("SSH key auth failed.")
        return 1
    if proc.returncode != 0:
        return print_proc(proc)
    lines = (proc.stdout or "").strip().splitlines()
    if not lines:
        return 0
    first = lines[0].strip()
    if first.startswith("Error"):
        print("No Thread dataset. Run dataset or start-thread first.", file=sys.stderr)
        return 1
    print(first)
    return 0


START_THREAD_SCRIPT = """
set -e
sudo -n ot-ctl factoryreset
sleep 3
sudo -n ot-ctl srp server disable
sudo -n ot-ctl thread stop
sudo -n ot-ctl ifconfig down
sudo -n ot-ctl dataset init new
sudo -n ot-ctl dataset commit active
sudo -n ot-ctl srp server enable
sudo -n ot-ctl ifconfig up
sudo -n ot-ctl thread start
sleep 7
sudo -n ot-ctl dataset active -x
"""


def cmd_start_thread(args: argparse.Namespace) -> int:
    host = require_host()
    proc = run_ssh(
        host,
        [f"sh -c {shlex.quote(START_THREAD_SCRIPT.strip())}"],
        timeout=120,
    )
    if auth_failed(proc):
        print_user_setup("SSH key auth failed.")
        return 1
    return print_proc(proc)


def read_dataset(host: str, explicit: Optional[str]) -> Optional[str]:
    if explicit:
        return explicit.strip().removeprefix("hex:")
    proc = run_ssh(host, ["sudo", "-n", "ot-ctl", "dataset", "active", "-x"])
    if proc.returncode != 0:
        return None
    lines = (proc.stdout or "").strip().splitlines()
    if not lines:
        return None
    first = lines[0].strip()
    if first.startswith("Error"):
        return None
    return first


def write_last_node_id(host: str, node_id: int) -> None:
    """Remember commissioned node id on the hub for ``show-node-id`` / later ``run``."""
    remote = f"echo {node_id} > {LAST_NODE_ID_REMOTE}"
    run_ssh(host, [f"sh -c {shlex.quote(remote)}"])


def cmd_show_node_id(args: argparse.Namespace) -> int:
    host = require_host()
    proc = run_ssh(host, ["cat", LAST_NODE_ID_REMOTE])
    if ssh_conn_failed(proc):
        print(f"SSH connection to {host} failed.", file=sys.stderr)
        return print_proc(proc) or 1
    if proc.returncode != 0:
        print("No last node id on hub.", file=sys.stderr)
        return 1
    print((proc.stdout or "").strip())
    return 0


def chip_tool_argv(extra: Sequence[str]) -> List[str]:
    """Build remote argv for a single chip-tool invocation."""
    quoted_args = [shlex.quote(arg) for arg in [CHIP_TOOL, *extra]]
    return [f"sh -c {shlex.quote(' '.join(quoted_args))}"]


def cmd_commission_thread(args: argparse.Namespace) -> int:
    host = require_host()
    dataset = read_dataset(host, args.dataset)
    if not dataset:
        print("No Thread dataset. Run dataset or start-thread first.", file=sys.stderr)
        return 1

    node_id = args.node_id if args.node_id is not None else random.randint(1, 100000)
    pin = args.pin or DEFAULT_PIN
    discriminator = args.discriminator or DEFAULT_DISCRIMINATOR

    proc = run_ssh(
        host,
        chip_tool_argv(
            [
                "pairing",
                "ble-thread",
                str(node_id),
                f"hex:{dataset}",
                pin,
                discriminator,
            ]
        ),
        timeout=COMMISSION_TIMEOUT_S,
    )
    if auth_failed(proc):
        print_user_setup("SSH key auth failed.")
        return 1
    code = print_proc(proc)
    if code == 0:
        write_last_node_id(host, node_id)
        print(f"node_id={node_id}", file=sys.stderr)
    return code


def cmd_run(args: argparse.Namespace) -> int:
    host = require_host()
    if not args.chip_tool_args:
        print("No chip-tool arguments. Example: run onoff on 1 1", file=sys.stderr)
        return 1
    proc = run_ssh(host, chip_tool_argv(args.chip_tool_args), timeout=COMMISSION_TIMEOUT_S)
    if auth_failed(proc):
        print_user_setup("SSH key auth failed.")
        return 1
    return print_proc(proc)


def cmd_logs(args: argparse.Namespace) -> int:
    host = require_host()
    proc = run_ssh(
        host,
        ["journalctl", "-u", "otbr-agent", "--no-pager", "-n", str(args.lines)],
    )
    if auth_failed(proc):
        print_user_setup("SSH key auth failed.")
        return 1
    return print_proc(proc)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Matter Hub chip-tool over SSH")

    sub = parser.add_subparsers(dest="command", required=True)

    discover_p = sub.add_parser(
        "discover",
        help="Write hub host to ~/.silabs/matter-hub.json (user setup)",
    )
    discover_p.add_argument(
        "--host",
        help="Hub IP or hostname. Required to create or update config",
    )
    discover_p.set_defaults(func=cmd_discover)

    sub.add_parser("check", help="Verify SSH, chip-tool, and ot-ctl").set_defaults(
        func=cmd_check
    )

    sub.add_parser("dataset", help="Print active Thread dataset hex").set_defaults(
        func=cmd_dataset
    )

    sub.add_parser(
        "start-thread",
        help="Factory-reset OTBR and start new Thread network",
    ).set_defaults(func=cmd_start_thread)

    commission = sub.add_parser("commission-thread", help="BLE-Thread commissioning")
    commission.add_argument("--node-id", type=int, default=None)
    commission.add_argument("--pin", default=None)
    commission.add_argument("--discriminator", default=None)
    commission.add_argument("--dataset", default=None, help="Hex dataset (no hex: prefix)")
    commission.set_defaults(func=cmd_commission_thread)

    sub.add_parser("show-node-id", help="Print last commissioned node id from hub").set_defaults(
        func=cmd_show_node_id
    )

    run_p = sub.add_parser("run", help="Run chip-tool with arguments")
    run_p.add_argument("chip_tool_args", nargs=argparse.REMAINDER)
    run_p.set_defaults(func=cmd_run)

    logs_p = sub.add_parser("logs", help="OTBR agent journal")
    logs_p.add_argument("--lines", type=int, default=200)
    logs_p.set_defaults(func=cmd_logs)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
