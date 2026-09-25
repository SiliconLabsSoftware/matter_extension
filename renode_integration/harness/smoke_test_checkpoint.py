#!/usr/bin/env python3
"""Load the booted-Linux checkpoint and confirm emulation starts."""

from __future__ import annotations

import argparse
import re
import select
import subprocess
import sys
import time
from pathlib import Path

from generate_checkpoint import DEFAULT_BUNDLE, resolve_renode


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test a Matter Renode checkpoint load")
    parser.add_argument("--bundle-dir", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="checkpoint path (default: <bundle>/linux-booted-thread.save)",
    )
    args = parser.parse_args()

    bundle_dir = args.bundle_dir.resolve()
    checkpoint = args.checkpoint or (bundle_dir / "linux-booted-thread.save")
    if not checkpoint.is_file():
        raise FileNotFoundError(checkpoint)
    renode_bin = resolve_renode(bundle_dir)

    proc = subprocess.Popen(
        [
            str(renode_bin),
            "--disable-gui",
            "--console",
            "-e",
            f"EmulationManager Load @{checkpoint}; start",
        ],
        cwd=bundle_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        deadline = time.time() + 180
        output_lines = []
        while time.time() < deadline:
            if proc.poll() is not None:
                output = "".join(output_lines)
                raise RuntimeError(f"Renode exited with code {proc.returncode}\n{output}")
            timeout = max(0, deadline - time.time())
            ready, _, _ = select.select([proc.stdout], [], [], min(timeout, 0.1))
            if ready:
                line = proc.stdout.readline()
                if line:
                    output_lines.append(line)
                    if re.search(r"Starting emulation", line):
                        print(f"Checkpoint loaded: {checkpoint}")
                        return 0
        raise TimeoutError("checkpoint load did not complete within 180s")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


if __name__ == "__main__":
    sys.exit(main())
