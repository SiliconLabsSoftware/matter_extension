#!/usr/bin/env python3
"""Push a common or runtime bundle directory to GHCR with ORAS."""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

import common

SOURCE_ANNOTATION = "https://github.com/SiliconLabsSoftware/matter_extension"


def copy_tree(src, dest):
    if not os.path.isdir(src):
        common.die(f"missing {src}")
    shutil.copytree(src, dest)


def file_manifest(staging, version, kind):
    files = {}
    for root, _, names in os.walk(staging):
        for name in names:
            if name == "manifest.json":
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, staging)
            with open(full, "rb") as handle:
                digest = hashlib.sha256(handle.read()).hexdigest()
            files[rel] = {"sha256": digest, "size": os.path.getsize(full)}
    return {
        "version": version,
        "kind": kind,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "files": files,
    }


def stage(kind, bundle, staging):
    if kind == "common":
        for item in ("guest-rootfs", "rcp", "resc"):
            copy_tree(os.path.join(bundle, item), os.path.join(staging, item))
        return
    if kind == "runtime":
        copy_tree(os.path.join(bundle, "renode"), os.path.join(staging, "renode"))
        for name in ("linux-booted-thread.save", "runtime-manifest.json"):
            src = os.path.join(bundle, name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(staging, name))
        return
    common.die(f"unknown kind: {kind}")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("common", "runtime"):
        common.die("usage: publish_bundle.py common|runtime")
    kind = sys.argv[1]
    oras = common.require_cmd("oras")
    version = common.bundle_version()
    package = common.manifest_lookup("ghcr.package")
    if kind == "runtime":
        tag = f"{version}-runtime-{common.detect_host()}"
    else:
        tag = f"{version}-{kind}"

    staging = os.path.join(common.RENODE_INTEGRATION_DIR, "out", "publish", kind)
    shutil.rmtree(staging, ignore_errors=True)
    os.makedirs(staging)
    stage(kind, common.bundle_dir(), staging)

    manifest_path = os.path.join(staging, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(file_manifest(staging, version, kind), handle, indent=2)
        handle.write("\n")

    push_args = []
    for root, _, names in os.walk(staging):
        for name in names:
            full = os.path.join(root, name)
            rel = os.path.relpath(full, staging).replace(os.sep, "/")
            push_args.append(f"{rel}:application/octet-stream")

    print(f"Publishing {package}:{tag}")
    subprocess.run(
        [
            oras,
            "push",
            f"{package}:{tag}",
            "--annotation",
            f"org.opencontainers.image.source={SOURCE_ANNOTATION}",
            *push_args,
        ],
        cwd=staging,
        check=True,
    )
    print(f"Published {package}:{tag}")


if __name__ == "__main__":
    main()
