#!/usr/bin/env python3
"""Build the pinned Renode fork for this host."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import common


def version_gt(left, right):
    def parts(value):
        return tuple(int(piece) for piece in value.split("."))

    left_parts = parts(left)
    right_parts = parts(right)
    width = max(len(left_parts), len(right_parts))
    left_parts += (0,) * (width - len(left_parts))
    right_parts += (0,) * (width - len(right_parts))
    return left_parts > right_parts


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


def portable_artifact(src_dir):
    packages = src_dir / "output" / "packages"
    found = sorted(packages.glob("*portable*.tar.gz")) + sorted(packages.glob("*portable*.dmg"))
    if len(found) != 1:
        names = " ".join(path.name for path in found) or "(none)"
        common.die(f"expected one portable package in {packages}, found: {names}")
    return found[0]


def install_portable(artifact, out_dir):
    with tempfile.TemporaryDirectory() as tmp:
        staging = Path(tmp)
        if artifact.name.endswith(".tar.gz"):
            subprocess.run(["tar", "-xzf", str(artifact), "-C", str(staging)], check=True)
            roots = [path for path in staging.iterdir() if path.is_dir()]
            if len(roots) != 1:
                common.die(f"unexpected layout in {artifact.name}")
            tree = roots[0]
        else:
            mount = staging / "mnt"
            mount.mkdir()
            subprocess.run(
                ["hdiutil", "attach", "-nobrowse", "-readonly", "-mountpoint", str(mount), str(artifact)],
                check=True,
            )
            try:
                macos_dirs = list(mount.glob("*.app/Contents/MacOS"))
                if len(macos_dirs) != 1:
                    common.die(f"unexpected layout in {artifact.name}")
                tree = staging / "renode"
                shutil.copytree(macos_dirs[0], tree, symlinks=True)
            finally:
                subprocess.run(["hdiutil", "detach", str(mount)], check=False)
        if not (tree / "renode").is_file():
            common.die(f"renode binary not found in {artifact.name}")
        shutil.rmtree(out_dir, ignore_errors=True)
        shutil.copytree(tree, out_dir, symlinks=True)


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

    build_args = ["-t"]
    env = os.environ.copy()
    if host == "osx-arm64":
        env["MACOSX_DEPLOYMENT_TARGET"] = str(common.manifest_lookup("macos.deployment_target"))
        build_args = ["-t", "--host-arch", "arm64"]

    print(f"Building Renode for {host} at {commit}...")
    subprocess.run(["./build.sh", *build_args], cwd=src_dir, env=env, check=True)
    install_portable(portable_artifact(src_dir), out_dir)
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
