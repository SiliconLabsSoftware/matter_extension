#!/usr/bin/env python3
"""Commission a Matter device in Renode and send a simple on/off toggle."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from matter_sim import DEFAULT_BUNDLE, DEFAULT_UART_TIMEOUT_S, MatterSim, run_shell

import test_lib

NODE_ID = 101
ENDPOINT = 1
PASSCODE = "20202021"
DISCRIMINATOR = "3840"
COMMISSION_TIMEOUT_S = 1200
TOGGLE_TIMEOUT_S = 300


def main() -> int:
    parser = argparse.ArgumentParser(description="Matter Renode commissioning smoke test")
    parser.add_argument("--matter-elf", type=Path, required=True)
    args = parser.parse_args()

    bundle_dir = DEFAULT_BUNDLE.resolve()
    matter_elf = args.matter_elf.resolve()
    if not matter_elf.is_file():
        raise FileNotFoundError(matter_elf)

    sim = MatterSim(bundle_dir)
    try:
        shutil.copyfile(matter_elf, bundle_dir / "matter.out")
        sim.load("matter-sim.resc")
        sim.soc_uart()
        hub = sim.hub_uart()
        test_lib.write_line(hub, "")
        test_lib.wait_for(hub, r"#\s*$", timeout=DEFAULT_UART_TIMEOUT_S)

        pair_cmd = (
            f'chip-tool pairing ble-thread {NODE_ID} '
            f'"hex:$(cat /tmp/thread-dataset.hex)" {PASSCODE} {DISCRIMINATOR}'
        )
        print(f"Running: {pair_cmd}")
        pair_rc, _pair_out = run_shell(hub, pair_cmd, timeout_s=COMMISSION_TIMEOUT_S)
        if pair_rc != 0:
            print(f"commissioning failed with exit code {pair_rc}", file=sys.stderr)
            return pair_rc

        toggle_cmd = f"chip-tool onoff toggle {NODE_ID} {ENDPOINT}"
        print(f"Running: {toggle_cmd}")
        toggle_rc, _toggle_out = run_shell(hub, toggle_cmd, timeout_s=TOGGLE_TIMEOUT_S)
        if toggle_rc != 0:
            print(f"toggle failed with exit code {toggle_rc}", file=sys.stderr)
            return toggle_rc

        print("Commissioning and onoff toggle succeeded")
        return 0
    finally:
        sim.close()


if __name__ == "__main__":
    sys.exit(main())
