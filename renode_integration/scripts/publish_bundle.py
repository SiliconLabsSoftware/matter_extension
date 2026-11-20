#!/usr/bin/env python3
"""
@file publish_bundle.py
@brief Package a common or runtime bundle and push it to GHCR with ORAS.

Usage:
  publish_bundle.py --bundle common|runtime|provision
  publish_bundle.py --bundle common|runtime|provision --action prepare|push
"""

import argparse
import os
import shutil
import subprocess
import tarfile

import common

SOURCE_ANNOTATION = "https://github.com/SiliconLabsSoftware/matter_extension"


def bundle_contents(bundle, kind):
    if kind == "common":
        directories = ("guest-rootfs", "rcp", "resc", "test_lib")
        filenames = ()
    elif kind == "runtime":
        directories = ("renode",)
        filenames = ("linux-booted-thread.save",)
    elif kind == "provision":
        directories = ("guest-rootfs",)
        filenames = ()
    else:
        common.die(f"unknown kind: {kind}")
    for name in directories:
        if not os.path.isdir(os.path.join(bundle, name)):
            common.die(f"bundle missing {name}")
    for name in filenames:
        path = os.path.join(bundle, name)
        if not os.path.isfile(path) or os.path.getsize(path) == 0:
            common.die(f"bundle missing {name}")
    if kind == "runtime" and not os.access(os.path.join(bundle, "renode", "renode"), os.X_OK):
        common.die("runtime bundle contains a non-executable Renode launcher")
    return directories + filenames


def archive_path(kind):
    return os.path.join(common.RENODE_INTEGRATION_DIR, "out", "publish", kind, f"{kind}.tar")


def prepare(kind):
    bundle = common.bundle_dir()
    names = bundle_contents(bundle, kind)
    path = archive_path(kind)
    staging = os.path.dirname(path)
    shutil.rmtree(staging, ignore_errors=True)
    os.makedirs(staging)

    with tarfile.open(path, "w", dereference=True) as archive:
        for name in names:
            archive.add(os.path.join(bundle, name), arcname=name)
    print(f"Prepared {path}")


def push(kind):
    path = archive_path(kind)
    if not os.path.isfile(path):
        common.die(f"bundle archive missing {path}; run prepare first")
    oras = common.require_cmd("oras")
    package = common.manifest_lookup("ghcr.package")
    tag = common.resolve_provision_tag(is_publish=True) if kind == "provision" else common.artifact_tag(kind)
    if tag is None:
        print("Skipping publish: no OCI tag for this branch/event context")
        return

    print(f"Publishing {package}:{tag}")
    subprocess.run(
        [
            oras,
            "push",
            f"{package}:{tag}",
            "--annotation",
            f"org.opencontainers.image.source={SOURCE_ANNOTATION}",
            f"{os.path.basename(path)}:application/vnd.oci.image.layer.v1.tar",
        ],
        cwd=os.path.dirname(path),
        check=True,
    )
    print(f"Published {package}:{tag}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Package a common, runtime, or provision bundle and push it to GHCR with ORAS.",
    )
    parser.add_argument(
        "--bundle",
        required=True,
        choices=("common", "runtime", "provision"),
        help="bundle to package and publish",
    )
    parser.add_argument(
        "--action",
        choices=("prepare", "push"),
        default="both",
        help="prepare archive and/or push to GHCR (default: both)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    action, kind = args.action, args.bundle
    if action in ("both", "prepare"):
        prepare(kind)
    if action in ("both", "push"):
        push(kind)


if __name__ == "__main__":
    main()
