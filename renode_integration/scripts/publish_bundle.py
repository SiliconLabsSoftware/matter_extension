#!/usr/bin/env python3
"""Package a common or runtime bundle and push it to GHCR with ORAS."""

import os
import shutil
import subprocess
import sys
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
        directories = ()
        filenames = (os.path.join("guest-rootfs", "matter-provision.ext2"),)
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
    full_paths = bundle_contents(bundle, kind)
    path = archive_path(kind)
    staging = os.path.dirname(path)
    shutil.rmtree(staging, ignore_errors=True)
    os.makedirs(staging)

    with tarfile.open(path, "w", dereference=True) as archive:
        for full_path in full_paths:
            arcname = os.path.relpath(full_path, bundle)
            archive.add(full_path, arcname=arcname)
    print(f"Prepared {path}")

def get_target_tags(kind: str) -> list[str]:
    ACTIVE_BRANCHES = {"main", "release_2.10-1.6.1"}
    event_name = os.environ.get("GITHUB_EVENT_NAME","")
    active_branch = os.environ.get("GITHUB_BASE_REF") if event_name == "pull_request" else os.environ.get("GITHUB_REF_NAME")

    if active_branch not in ACTIVE_BRANCHES:
        print(f"Skipping registration: '{active_branch}' is not an active branch.")
        return []

    base_tag = common.artifact_tag(kind)

    if event_name == "pull_request":
        pr_num = os.environ.get("GITHUB_PR_NUMBER")
        if kind == "provision" and pr_num:
            return [f"{base_tag}-pr-{pr_num}"]
        print(f"Skipping PR tag publication for bundle kind: '{kind}'")
        return []

    return [base_tag]


def push(kind):
    path = archive_path(kind)
    if not os.path.isfile(path):
        common.die(f"bundle archive missing {path}; run prepare first")
    
    tags_to_push = get_target_tags(kind)
    if not tags_to_push:
        return
    
    oras = common.require_cmd("oras")
    package = common.manifest_lookup("ghcr.package")
    
    for tag in tags_to_push:
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


def main():
    usage = "usage: publish_bundle.py [prepare|push] common|runtime|provision"
    if len(sys.argv) == 2:
        action, kind = "both", sys.argv[1]
    elif len(sys.argv) == 3:
        action, kind = sys.argv[1:]
    else:
        common.die(usage)
    if action not in ("both", "prepare", "push") or kind not in ("common", "runtime", "provision"):
        common.die(usage)
    if action in ("both", "prepare"):
        prepare(kind)
    if action in ("both", "push"):
        push(kind)


if __name__ == "__main__":
    main()
