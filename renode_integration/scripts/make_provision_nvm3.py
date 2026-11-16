#!/usr/bin/env python3
"""
@file make_provision_nvm3.py
@brief Write NVM3 key 0x87228 = 1 (provision-required) for Matter self-provisioning.

Matches the ``nvm3 set --object 0x87228:01`` step from Matter self-provisioning docs.
"""

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

import common

PROVISION_REQUIRED_KEY = "0x87228"
PROVISION_REQUIRED_OBJECT = f"{PROVISION_REQUIRED_KEY}:01"


def board_device(board):
    """Resolve a board's part from the SDK's board component metadata."""
    board = board.lower()
    if not re.fullmatch(r"brd[0-9]+[a-z]", board):
        raise ValueError(f"invalid board name: {board}, expected e.g. brd4187c")
    component = (
        Path(common.REPO_ROOT) / "third_party/simplicity_sdk/boards/hardware/board/component" / f"{board}.slcc"
    )
    if not component.is_file():
        raise ValueError(f"board component not found: {component}; check --board and the Simplicity SDK submodule")
    devices = re.findall(r"^\s*- board:device:([a-zA-Z0-9]+)\s*$", component.read_text(encoding="utf-8"), re.MULTILINE)
    if len(devices) != 1:
        raise ValueError(f"expected one device in board component: {component}")
    return devices[0].upper()


def nvm3_region(map_path):
    text = Path(map_path).read_text(encoding="utf-8", errors="replace")
    base = re.search(r"^\s+(0x[0-9a-fA-F]+)\s+__nvm3Base\s*=", text, re.MULTILINE)
    size = re.search(r"^\.nvm\s+0x[0-9a-fA-F]+\s+(0x[0-9a-fA-F]+)", text, re.MULTILINE)
    if base is None or size is None:
        common.die(f"could not find __nvm3Base and the .nvm section in {map_path}")
    return base.group(1), size.group(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", required=True, type=Path, help="linker map of the Matter app")
    parser.add_argument(
        "--board",
        required=True,
        help="SDK board name, e.g. brd4187c (requires the Simplicity SDK submodule)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(common.RENODE_INTEGRATION_DIR) / "out" / "nvm3-provision.hex",
        help="Intel HEX output (default: out/nvm3-provision.hex)",
    )
    args = parser.parse_args()
    try:
        device = board_device(args.board)
    except ValueError as exc:
        parser.error(str(exc))
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
                device,
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
