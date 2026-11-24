#!/usr/bin/env python3
"""
@file fetch_bundle.py
@brief Pull the published common bundle and this host's runtime from GHCR.

Uses ORAS to download versioned artifacts tagged in sim-manifest.json into
renode_integration/out/bundle. For a PR, each bundle's -pr-N tag is preferred
over the base tag. Skips runtime fetch if no artifact exists for the host.
"""

import argparse
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


def pull_first(oras, package, tags, bundle, kind):
    """Pull the first tag that exists on GHCR, returns it or None."""
    for tag in tags:
        exists = subprocess.run(
            [oras, "manifest", "fetch", f"{package}:{tag}"],
            capture_output=True,
        )
        if exists.returncode == 0:
            print(f"Fetching {package}:{tag} -> {bundle}")
            pull_bundle(oras, package, tag, bundle, kind)
            return tag
    return None


def main():
    parser = argparse.ArgumentParser(
        description="pull required common, runtime, and provisioning bundle"
    )
    parser.add_argument(
        "-p", "--pr",
        type=str,
        default=None,
        help="prefer bundles built for this PR number, falling back to the published ones "
        "(defaults to the PR of a GHA pull_request run).",
    )
    parser.add_argument(
        "--require-provision",
        action="store_true",
        help="fail if the provisioning artifact is missing.",
    )
    args = parser.parse_args()

    oras = common.require_cmd("oras")
    host = common.detect_host()
    package = common.manifest_lookup("ghcr.package")
    bundle = common.bundle_dir()
    os.makedirs(bundle, exist_ok=True)

    common_tags = common.fetch_tags("common", pr_num=args.pr)
    common_tag = pull_first(oras, package, common_tags, bundle, "common")
    if common_tag is None:
        common.die(f"no common artifact found, tried: {', '.join(common_tags)}")

    runtime_tags = common.fetch_tags("runtime", host, pr_num=args.pr)
    runtime_tag = pull_first(oras, package, runtime_tags, bundle, "runtime")
    if runtime_tag is None:
        print(f"warning: no runtime artifact for {host}, build Renode and run harness/generate_checkpoint.py")
    elif common_tag != common_tags[-1] and runtime_tag == runtime_tags[-1]:
        print(f"warning: {runtime_tag} checkpoint was not built against {common_tag}")

    provision_tags = common.fetch_tags("provision", pr_num=args.pr)
    if pull_first(oras, package, provision_tags, bundle, "provision") is None:
        message = f"no provisioning artifact found, tried: {', '.join(provision_tags)}"
        if args.require_provision:
            common.die(message)
        print(f"warning: {message}")

    print(f"Bundle fetched to {bundle}")


if __name__ == "__main__":
    main()
