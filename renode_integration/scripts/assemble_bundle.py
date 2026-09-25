#!/usr/bin/env python3
"""Copy built artifacts into the published bundle layout."""

import glob
import os
import shutil

import common


def copy_if_exists(src, dest_dir):
    if os.path.isfile(src):
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy2(src, os.path.join(dest_dir, os.path.basename(src)))


def main():
    bundle = common.bundle_dir()
    guest_out = os.path.join(common.RENODE_INTEGRATION_DIR, "out", "guest-rootfs")
    guest_dest = os.path.join(bundle, "guest-rootfs")
    for name in ("matter-rootfs.ext2", "matter-tools.ext2", "zynqmp-matter-linux.dtb"):
        copy_if_exists(os.path.join(guest_out, name), guest_dest)

    rcp_out = os.path.join(common.RENODE_INTEGRATION_DIR, "out", "rcp")
    if os.path.isdir(rcp_out):
        rcp_dest = os.path.join(bundle, "rcp")
        os.makedirs(rcp_dest, exist_ok=True)
        for elf in glob.glob(os.path.join(rcp_out, "*.out")):
            shutil.copy2(elf, os.path.join(rcp_dest, os.path.basename(elf)))

    resc_dest = os.path.join(bundle, "resc")
    os.makedirs(resc_dest, exist_ok=True)
    for resc in glob.glob(os.path.join(common.RENODE_INTEGRATION_DIR, "resc", "*.resc")):
        shutil.copy2(resc, os.path.join(resc_dest, os.path.basename(resc)))

    host = common.detect_host()
    built = os.path.join(common.RENODE_INTEGRATION_DIR, "out", "renode", host)
    renode_dest = os.path.join(bundle, "renode")
    if os.path.isfile(os.path.join(built, "renode")):
        shutil.rmtree(renode_dest, ignore_errors=True)
        shutil.copytree(built, renode_dest)

    checkpoint = os.path.join(bundle, "linux-booted-thread.save")
    cached = os.path.join(common.RENODE_INTEGRATION_DIR, "out", "linux-booted-thread.save")
    if not os.path.isfile(checkpoint) and os.path.isfile(cached):
        shutil.copy2(cached, checkpoint)

    os.makedirs(renode_dest, exist_ok=True)
    print(f"Assembled bundle at {bundle}")


if __name__ == "__main__":
    main()
