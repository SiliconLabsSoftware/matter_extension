#!/usr/bin/env python3
"""
@file assemble_bundle.py
@brief Copy built artifacts into the published bundle layout.

Collects guest rootfs/tools images and DTB, RCP ELFs, and (when built)
the host-specific portable Renode tree and its test_lib into renode_integration/out/bundle.
"""

import argparse
import glob
import os
import shutil

import common


def copy_tree(src, dest):
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(src, dest)


def copy_if_exists(src, dest_dir):
    if os.path.isfile(src):
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy2(src, os.path.join(dest_dir, os.path.basename(src)))


def assemble_provision_bundle(bundle):
    src = os.path.join(
        common.RENODE_INTEGRATION_DIR,
        "out",
        "guest-rootfs",
        "matter-provision.ext2",
    )
    if not os.path.isfile(src):
        common.die(f"provision image not found at {src}")
    dest = os.path.join(bundle, "guest-rootfs")
    os.makedirs(dest, exist_ok=True)
    shutil.copy2(src, os.path.join(dest, "matter-provision.ext2"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--provision",
        action="store_true",
        help="assemble only the provisioning image",
    )
    args = parser.parse_args(argv)

    bundle = common.bundle_dir()
    os.makedirs(bundle, exist_ok=True)
    if args.provision:
        assemble_provision_bundle(bundle)
        print(f"Assembled provision bundle at {bundle}")
        return

    guest_out = os.path.join(common.RENODE_INTEGRATION_DIR, "out", "guest-rootfs")
    guest_dest = os.path.join(bundle, "guest-rootfs")
    for name in ("matter-rootfs.ext2", "matter-tools.ext2", "zynqmp-matter-linux.dtb", "matter-provision.ext2"):
        copy_if_exists(os.path.join(guest_out, name), guest_dest)

    rcp_out = os.path.join(common.RENODE_INTEGRATION_DIR, "out", "rcp")
    if os.path.isdir(rcp_out):
        rcp_dest = os.path.join(bundle, "rcp")
        os.makedirs(rcp_dest, exist_ok=True)
        for elf in glob.glob(os.path.join(rcp_out, "*.out")):
            shutil.copy2(elf, os.path.join(rcp_dest, os.path.basename(elf)))

    out = os.path.join(common.RENODE_INTEGRATION_DIR, "out")
    built = os.path.join(out, "renode", common.detect_host())
    if os.path.isfile(os.path.join(built, "renode")):
        copy_tree(built, os.path.join(bundle, "renode"))
        copy_tree(os.path.join(out, "test_lib"), os.path.join(bundle, "test_lib"))

    print(f"Assembled bundle at {bundle}")


if __name__ == "__main__":
    main()
