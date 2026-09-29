#!/usr/bin/env python3
"""Load the booted-Linux checkpoint and confirm the hub console responds."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from generate_checkpoint import DEFAULT_BUNDLE
from matter_sim import MatterSim

LOAD_TIMEOUT_S = 180


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
    checkpoint = (args.checkpoint or (bundle_dir / "linux-booted-thread.save")).resolve()
    if not checkpoint.is_file():
        raise FileNotFoundError(checkpoint)

    started = time.monotonic()
    sim = MatterSim(bundle_dir)
    try:
        sim.execute(f"EmulationManager Load @{checkpoint}")
        sim.execute("start")
        remaining = LOAD_TIMEOUT_S - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError(f"checkpoint load did not complete within {LOAD_TIMEOUT_S}s")
        console = sim.hub_console(timeout_s=remaining)
        console.write_line("")
        console.wait_for(r"#\s*$", timeout_s=remaining)
        print(f"Checkpoint loaded: {checkpoint}")
        return 0
    finally:
        sim.close()


if __name__ == "__main__":
    sys.exit(main())
