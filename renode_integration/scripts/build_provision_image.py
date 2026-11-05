#!/usr/bin/env python3
"""Build matter-provision.ext2 from third_party/matter_support/provision.

The image contains provision.py, requirements.txt wheels, and an arm64 Python
runtime so matter_support updates stay self-contained. matter-tools.ext2 is
unchanged. Build on Linux aarch64 (same as matter-tools.ext2).
"""

import os
import shutil
import subprocess
import tempfile
import sys
from pathlib import Path

import common

_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "test", "temp", "latest.json")


def stage_python_runtime(staging):
    req = (
        Path(common.REPO_ROOT)
        / "third_party"
        / "matter_support"
        / "provision"
        / "requirements.txt"
    )
    if not req.is_file():
        common.die(f"missing {req} (init third_party/matter_support)")

    guest_bin = staging / "guest-bin"
    lib_dir = staging / "usr" / "lib" / "aarch64-linux-gnu"
    guest_bin.mkdir(parents=True)
    lib_dir.mkdir(parents=True)
    (staging / "lib").mkdir(exist_ok=True)

    python = Path(common.first_file("/usr/bin/python3.12", "/usr/bin/python3"))
    common.install_file(python, guest_bin / "python3", 0o755)
    stdlib = Path("/usr/lib/python3.12")
    if not stdlib.is_dir():
        common.die(f"python stdlib not found at {stdlib}")
    shutil.copytree(
        stdlib,
        staging / "lib" / stdlib.name,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "test", "tests"),
        dirs_exist_ok=True,
    )
    site = staging / "opt" / "provision" / "site-packages"
    site.mkdir(parents=True)
    subprocess.run(
        [str(python), "-m", "pip", "install", "--target", str(site), "-r", str(req)],
        check=True,
    )
    shutil.copy2(req, staging / "requirements.txt")

    binaries = [p for p in guest_bin.iterdir() if p.is_file()]
    dynload = staging / "lib" / "python3.12" / "lib-dynload"
    if dynload.is_dir():
        binaries.extend(p for p in dynload.iterdir() if p.suffix == ".so")
    binaries.extend(site.rglob("*.so"))
    common.copy_dynamic_libs_for_binaries(
        binaries,
        lib_dir,
        staging / "lib" / "ld-linux-aarch64.so.1",
    )


def build_provision_ext2(output: Path) -> None:
    src = Path(common.REPO_ROOT) / "third_party" / "matter_support" / "provision"
    if not (src / "provision.py").is_file():
        common.die(f"provision.py not found at {src} (init third_party/matter_support)")

    native = os.uname().sysname == "Linux" and os.uname().machine == "aarch64"
    if not native:
        common.die(
            "matter-provision.ext2 must be built on Linux aarch64 (hub matches arm64 Python). "
            "Use an arm64 host."
        )
    if not shutil.which("pip3") and not shutil.which("pip"):
        sys.exit("ERROR: pip/pip3 not installed, cannot build the image")

    work = Path(tempfile.mkdtemp())
    try:
        staging = work / "staging"
        shutil.copytree(src, staging / "tool", ignore=_IGNORE)
        stage_python_runtime(staging)

        common.make_ext2_from_staging(staging, output, "matter-provision", extra_mb=8, min_mb=64)
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    out_dir = Path(common.RENODE_INTEGRATION_DIR) / "out" / "guest-rootfs"
    output = out_dir / "matter-provision.ext2"
    build_provision_ext2(output)


if __name__ == "__main__":
    main()
