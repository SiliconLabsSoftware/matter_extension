#!/usr/bin/env python3
"""Commission a Matter device in Renode and send a simple on/off toggle."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from generate_checkpoint import DEFAULT_BUNDLE
from matter_sim import MatterSim

NODE_ID = 101
ENDPOINT = 1
PASSCODE = "20202021"
DISCRIMINATOR = "3840"
COMMISSION_TIMEOUT_S = 1200
TOGGLE_TIMEOUT_S = 300


def write_log(log_dir: Path, name: str, text: str) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / name).write_text(text, encoding="utf-8")


def report_failure(label: str, rc: int, soc_text: str) -> None:
    print(f"{label} failed with exit code {rc}", file=sys.stderr)
    tail = "\n".join(soc_text.splitlines()[-40:])
    if tail:
        print("matter_soc console (last 40 lines):", file=sys.stderr)
        print(tail, file=sys.stderr)
    else:
        print("matter_soc console was empty", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Matter Renode commissioning smoke test")
    parser.add_argument("--bundle-dir", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--matter-elf", type=Path, required=True)
    parser.add_argument("--log-dir", type=Path, default=Path("renode-commissioning-logs"))
    args = parser.parse_args()

    bundle_dir = args.bundle_dir.resolve()
    matter_elf = args.matter_elf.resolve()
    log_dir = args.log_dir.resolve()
    if not matter_elf.is_file():
        raise FileNotFoundError(matter_elf)

    sim = MatterSim(bundle_dir)
    console = None
    soc = None
    try:
        shutil.copyfile(matter_elf, bundle_dir / "matter.out")
        sim.load("matter-sim.resc")
        soc = sim.soc_console()
        console = sim.hub_console()
        console.write_line("")
        console.wait_for(r"#\s*$")

        pair_cmd = (
            f'chip-tool pairing ble-thread {NODE_ID} '
            f'"hex:$(cat /tmp/thread-dataset.hex)" {PASSCODE} {DISCRIMINATOR}'
        )
        print(f"Running: {pair_cmd}")
        pair_rc, pair_out = console.run(pair_cmd, timeout_s=COMMISSION_TIMEOUT_S)
        write_log(log_dir, "commission.log", pair_out)
        if pair_rc != 0:
            report_failure("commissioning", pair_rc, soc.get_report())
            return pair_rc

        toggle_cmd = f"chip-tool onoff toggle {NODE_ID} {ENDPOINT}"
        print(f"Running: {toggle_cmd}")
        toggle_rc, toggle_out = console.run(toggle_cmd, timeout_s=TOGGLE_TIMEOUT_S)
        write_log(log_dir, "toggle.log", toggle_out)
        if toggle_rc != 0:
            report_failure("toggle", toggle_rc, soc.get_report())
            return toggle_rc

        print("Commissioning and onoff toggle succeeded")
        return 0
    finally:
        if soc is not None:
            write_log(log_dir, "soc-console.log", soc.get_report())
        if console is not None:
            write_log(log_dir, "hub-console.log", console.get_report())
        sim.close()


if __name__ == "__main__":
    sys.exit(main())
