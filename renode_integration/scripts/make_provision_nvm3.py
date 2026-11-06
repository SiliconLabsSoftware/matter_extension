#!/usr/bin/env python3
"""
Writes NVM3 key 0x87228 = 1 (provision-required), matching the ``nvm3 set
--object 0x87228:01`` step from Matter self-provisioning docs.
"""

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

import common

PROVISION_REQUIRED_KEY = "0x87228"
PROVISION_REQUIRED_OBJECT = f"{PROVISION_REQUIRED_KEY}:01"
DEFAULT_DEVICE = "EFR32MG24B220F1536IM48"


def nvm3_region(map_path):
    text = Path(map_path).read_text(encoding="utf-8", errors="replace")
    base = re.search(r"^\s+(0x[0-9a-fA-F]+)\s+__nvm3Base\s*=", text, re.MULTILINE)
    size = re.search(r"^\.nvm\s+0x[0-9a-fA-F]+\s+(0x[0-9a-fA-F]+)", text, re.MULTILINE)
    if base is None or size is None:
        common.die(f"could not find __nvm3Base and the .nvm section in {map_path}")
    return base.group(1), size.group(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--map", required=True, type=Path, help="linker map of the Matter app")
    parser.add_argument(
        "--device",
        default=DEFAULT_DEVICE,
        help=f"part number for commander nvm3 initfile flash layout (default: {DEFAULT_DEVICE})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(common.RENODE_INTEGRATION_DIR) / "out" / "nvm3-provision.hex",
        help="Intel HEX output (default: out/nvm3-provision.hex)",
    )
    args = parser.parse_args()
    if not args.map.is_file():
        common.die(f"map not found: {args.map}")

    commander = common.require_cmd("commander")
    address, size = nvm3_region(args.map)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as work:
        blank = Path(work) / "nvm3-blank.s37"
        flagged = Path(work) / "nvm3-provision.s37"
        subprocess.run(
            [
                commander,
                "nvm3",
                "initfile",
                "--device",
                args.device,
                "--address",
                address,
                "--size",
                size,
                "--outfile",
                str(blank),
            ],
            check=True,
        )
        subprocess.run(
            [commander, "nvm3", "set", str(blank), "--object", PROVISION_REQUIRED_OBJECT, "--outfile", str(flagged)],
            check=True,
        )
        subprocess.run([commander, "convert", str(flagged), "--outfile", str(args.output)], check=True)

    print(f"Built {args.output} (NVM3 {address} +{size}, key {PROVISION_REQUIRED_KEY}=1)")


if __name__ == "__main__":
    main()
