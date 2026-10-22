#!/usr/bin/env python3
"""Load the booted-Linux checkpoint and confirm the hub console responds."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from matter_sim import DEFAULT_BUNDLE, MatterSim

import test_lib

LOAD_TIMEOUT_S = 180


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test a Matter Renode checkpoint load")
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="checkpoint path (default: <bundle>/linux-booted-thread.save)",
    )
    args = parser.parse_args()

    bundle_dir = DEFAULT_BUNDLE.resolve()
    checkpoint = (args.checkpoint or (bundle_dir / "linux-booted-thread.save")).resolve()
    if not checkpoint.is_file():
        raise FileNotFoundError(checkpoint)

    started = time.monotonic()
    sim = MatterSim(bundle_dir)
    try:
        test_lib.execute_monitor_command(f"EmulationManager Load @{checkpoint}")
        test_lib.execute_monitor_command("start")
        remaining = LOAD_TIMEOUT_S - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError(f"checkpoint load did not complete within {LOAD_TIMEOUT_S}s")
        hub = sim.hub_uart(timeout_s=remaining)
        test_lib.write_line(hub, "")
        test_lib.wait_for(hub, r"#\s*$", timeout=remaining)
        print(f"Checkpoint loaded: {checkpoint}")
        return 0
    finally:
        sim.close()


if __name__ == "__main__":
    sys.exit(main())
