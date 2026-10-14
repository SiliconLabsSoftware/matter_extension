#!/usr/bin/env python3
"""Generate a Renode checkpoint with Linux booted and Thread network formed."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from matter_sim import DEFAULT_BUNDLE, DEFAULT_UART_TIMEOUT_S, MatterSim, login_root, resolve_renode

import test_lib


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Matter Renode checkpoint")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="checkpoint path (default: <bundle>/linux-booted-thread.save)",
    )
    args = parser.parse_args()

    bundle_dir = DEFAULT_BUNDLE.resolve()
    checkpoint = args.output or (bundle_dir / "linux-booted-thread.save")
    resc = bundle_dir / "resc" / "matter-sim-full.resc"
    if not resc.is_file():
        raise FileNotFoundError(f"{resc} not found, assemble the bundle or run scripts/fetch_bundle.py")
    renode_bin = resolve_renode(bundle_dir)

    print(f"Starting Renode: {renode_bin}")
    sim = MatterSim(bundle_dir)
    try:
        sim.load("matter-sim-full.resc")
        hub = sim.hub_uart()
        test_lib.wait_for(hub, r"matter-services: READY", timeout=DEFAULT_UART_TIMEOUT_S)
        login_root(hub)
        test_lib.write_line(hub, "matter-thread-init")
        test_lib.wait_for(hub, r"matter-thread-init: READY", timeout=180)
        sim.save(checkpoint)
        print(f"Saved checkpoint: {checkpoint}")

        return 0
    finally:
        sim.close()


if __name__ == "__main__":
    sys.exit(main())
