#!/usr/bin/env python3
"""Build the pinned Renode fork for this host."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import common


def version_gt(left, right):
    def parts(value):
        return tuple(int(piece) for piece in value.split("."))

    return parts(left) > parts(right)


def renode_version(renode_bin):
    result = subprocess.run([renode_bin, "-v"], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.splitlines()[0]
    return "unknown"


def verify_macos_libs(renode_dir, deployment_target):
    print("Verifying macOS native libraries...")
    for lib in renode_dir.rglob("*.dylib"):
        if not lib.is_file():
            continue
        described = subprocess.run(["file", str(lib)], capture_output=True, text=True, check=True)
        if "x86_64" in described.stdout:
            common.die(f"x86_64 library found (Rosetta dependency): {lib}")
        if shutil.which("vtool") is None:
            continue
        shown = subprocess.run(["vtool", "-show-build", str(lib)], capture_output=True, text=True)
        minos = ""
        for line in shown.stdout.splitlines():
            fields = line.split()
            if "minos" in fields:
                minos = fields[fields.index("minos") + 1]
                break
        if minos and version_gt(minos, deployment_target):
            common.die(f"library {lib} requires macOS {minos}")


def main():
    host = common.detect_host()
    out_dir = Path(common.RENODE_INTEGRATION_DIR) / "out" / "renode" / host
    src_dir = Path(common.RENODE_INTEGRATION_DIR) / "renode-src"
    commit = common.manifest_lookup("renode.commit")
    repo_url = common.manifest_lookup("renode.repo")
    Path(common.CACHE_DIR).mkdir(parents=True, exist_ok=True)

    if not (src_dir / ".git").is_dir():
        subprocess.run(["git", "clone", repo_url, str(src_dir)], check=True)
    fetched = subprocess.run(["git", "-C", str(src_dir), "fetch", "origin", commit, "--depth", "1"])
    if fetched.returncode != 0:
        subprocess.run(["git", "-C", str(src_dir), "fetch", "--unshallow"], check=False)
    subprocess.run(["git", "-C", str(src_dir), "checkout", commit], check=True)

    build_args = ["-p"]
    env = os.environ.copy()
    if host == "osx-arm64":
        env["MACOSX_DEPLOYMENT_TARGET"] = str(common.manifest_lookup("macos.deployment_target"))
        build_args = ["-p", "--host-arch", "arm64"]

    print(f"Building Renode for {host} at {commit}...")
    subprocess.run(["./build.sh", *build_args], cwd=src_dir, env=env, check=True)

    matches = list(src_dir.glob("renode-portable-*")) + list(src_dir.glob("*/renode-portable-*"))
    built = next((path for path in matches if path.is_dir()), None)
    if built is None:
        common.die("renode-portable directory not found after build")

    shutil.rmtree(out_dir, ignore_errors=True)
    shutil.copytree(built, out_dir, symlinks=True)
    for link in out_dir.rglob("libgdiplus.dylib"):
        if link.is_symlink():
            link.unlink()

    renode_bin = out_dir / "renode"
    if not os.access(renode_bin, os.X_OK):
        common.die(f"renode binary not found at {renode_bin}")

    manifest = {
        "host": host,
        "renode_commit": commit,
        "renode_version": renode_version(str(renode_bin)),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if host == "osx-arm64":
        verify_macos_libs(out_dir, str(common.manifest_lookup("macos.deployment_target")))

    print(f"Built Renode: {renode_bin}")


if __name__ == "__main__":
    main()
