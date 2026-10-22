#!/usr/bin/env python3
"""Build Thread and BLE RCP binaries for the Renode Matter simulation."""

import argparse
import os
import shutil
import subprocess

import common

INTEGRATION_DIR = common.RENODE_INTEGRATION_DIR
DEFAULT_SDK = os.path.join(common.REPO_ROOT, "third_party", "simplicity_sdk")


def build_rcp(sdk_path, slcp_rel, board, output_path, configuration):
    board_lower = board.lower()
    slcp = os.path.join(sdk_path, slcp_rel)
    if not os.path.isfile(slcp):
        raise FileNotFoundError(f"SLCP not found: {slcp}")

    gen_dir = os.path.join(INTEGRATION_DIR, "out", "rcp-build", board_lower, os.path.basename(slcp_rel).replace(".slcp", ""))
    if os.path.isdir(gen_dir):
        shutil.rmtree(gen_dir)

    command = [
        "slc",
        "generate",
        "--sdk-package-path",
        sdk_path,
        slcp,
        "-d",
        gen_dir,
        "--with",
        board_lower,
    ]
    for override in configuration:
        command.extend(["--configuration", override])
    subprocess.run(command, check=True)

    makefile = next(
        (name for name in os.listdir(gen_dir) if name.endswith(".Makefile")),
        None,
    )
    if makefile is None:
        raise FileNotFoundError(f"No Makefile found in {gen_dir}")

    subprocess.run(["make", "-f", makefile, "all"], cwd=gen_dir, check=True)

    elf_name = makefile.replace(".Makefile", ".out")
    elf_path = os.path.join(gen_dir, "build", "debug", elf_name)
    if not os.path.isfile(elf_path):
        raise FileNotFoundError(f"ELF not found after build: {elf_path}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    shutil.copy2(elf_path, output_path)
    print(f"Built {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Build RCP binaries for Renode Matter sim")
    parser.add_argument("--sdk", default=DEFAULT_SDK, help="Path to Simplicity SDK")
    parser.add_argument("--output-dir", default=os.path.join(INTEGRATION_DIR, "out", "rcp"))
    args = parser.parse_args()

    manifest = common.load_manifest()
    for entry in manifest["rcps"]:
        output = os.path.join(args.output_dir, entry["output"])
        build_rcp(args.sdk, entry["slcp"], entry["board"], output, entry.get("configuration", []))


if __name__ == "__main__":
    main()
