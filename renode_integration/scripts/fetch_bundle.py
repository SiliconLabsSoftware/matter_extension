#!/usr/bin/env python3
"""Pull the published common bundle and this host's runtime from GHCR."""

import os
import shutil
import subprocess
import tarfile
import tempfile

import common


def extract_bundle(archive_path, bundle):
    bundle_root = os.path.realpath(bundle)
    with tarfile.open(archive_path, "r") as archive:
        for member in archive:
            path = os.path.realpath(os.path.join(bundle, member.name))
            if os.path.commonpath((bundle_root, path)) != bundle_root or path == bundle_root:
                common.die(f"invalid path in bundle archive: {member.name}")
            if member.isdir():
                os.makedirs(path, exist_ok=True)
            elif member.isfile():
                os.makedirs(os.path.dirname(path), exist_ok=True)
                source = archive.extractfile(member)
                if source is None:
                    common.die(f"cannot read bundle file: {member.name}")
                with source, open(path, "wb") as target:
                    shutil.copyfileobj(source, target)
            else:
                common.die(f"unsupported entry in bundle archive: {member.name}")
            os.chmod(path, member.mode & 0o777)


def pull_bundle(oras, package, tag, bundle, kind):
    with tempfile.TemporaryDirectory() as download_dir:
        subprocess.run([oras, "pull", f"{package}:{tag}", "-o", download_dir], check=True)
        archive_path = os.path.join(download_dir, f"{kind}.tar")
        extract_bundle(archive_path, bundle)


def main():
    oras = common.require_cmd("oras")
    host = common.detect_host()
    package = common.manifest_lookup("ghcr.package")
    bundle = common.bundle_dir()
    os.makedirs(bundle, exist_ok=True)

    common_tag = common.artifact_tag("common")
    print(f"Fetching {package}:{common_tag} -> {bundle}")
    pull_bundle(oras, package, common_tag, bundle, "common")

    runtime_tag = common.artifact_tag("runtime", host)
    fetched = subprocess.run(
        [oras, "manifest", "fetch", f"{package}:{runtime_tag}"],
        capture_output=True,
    )
    if fetched.returncode == 0:
        print(f"Fetching {package}:{runtime_tag} -> {bundle}")
        pull_bundle(oras, package, runtime_tag, bundle, "runtime")
    else:
        print(f"warning: no runtime artifact for {host}, build Renode and run harness/generate_checkpoint.py")

    print(f"Bundle fetched to {bundle}")


if __name__ == "__main__":
    main()
