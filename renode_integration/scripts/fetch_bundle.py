#!/usr/bin/env python3
"""Pull the published common bundle and this host's runtime from GHCR."""

import os
import subprocess

import common


def main():
    oras = common.require_cmd("oras")
    version = common.bundle_version()
    host = common.detect_host()
    package = common.manifest_lookup("ghcr.package")
    bundle = common.bundle_dir()
    os.makedirs(bundle, exist_ok=True)

    common_tag = f"{version}-common"
    print(f"Fetching {package}:{common_tag} -> {bundle}")
    subprocess.run([oras, "pull", f"{package}:{common_tag}", "-o", bundle], check=True)

    runtime_tag = f"{version}-runtime-{host}"
    fetched = subprocess.run(
        [oras, "manifest", "fetch", f"{package}:{runtime_tag}"],
        capture_output=True,
    )
    if fetched.returncode == 0:
        print(f"Fetching {package}:{runtime_tag} -> {bundle}")
        subprocess.run([oras, "pull", f"{package}:{runtime_tag}", "-o", bundle], check=True)
    else:
        print(f"warning: no runtime artifact for {host}, build Renode and run harness/generate_checkpoint.py")

    print(f"Bundle fetched to {bundle}")


if __name__ == "__main__":
    main()
