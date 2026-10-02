#!/usr/bin/env python3
"""Generate a Renode checkpoint with Linux booted and Thread network formed."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from matter_sim import MatterSim, resolve_renode

SCRIPT_DIR = Path(__file__).resolve().parent
INTEGRATION_DIR = SCRIPT_DIR.parent
DEFAULT_BUNDLE = INTEGRATION_DIR / "out" / "bundle"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Matter Renode checkpoint")
    parser.add_argument("--bundle-dir", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="checkpoint path (default: <bundle>/linux-booted-thread.save)",
    )
    args = parser.parse_args()

    bundle_dir = args.bundle_dir.resolve()
    checkpoint = args.output or (bundle_dir / "linux-booted-thread.save")
    resc = bundle_dir / "resc" / "matter-sim-full.resc"
    if not resc.is_file():
        raise FileNotFoundError(f"{resc} not found, assemble the bundle or run scripts/fetch_bundle.py")
    renode_bin = resolve_renode(bundle_dir)

    print(f"Starting Renode: {renode_bin}")
    sim = MatterSim(bundle_dir)
    try:
        sim.load("matter-sim-full.resc")
        console = sim.hub_console()
        console.wait_for(r"matter-services: READY")
        console.login_root()
        console.write_line("matter-thread-init")
        console.wait_for(r"matter-thread-init: READY", timeout_s=180)
        sim.save(checkpoint)
        print(f"Saved checkpoint: {checkpoint}")

        return 0
    finally:
        sim.close()


if __name__ == "__main__":
    sys.exit(main())
