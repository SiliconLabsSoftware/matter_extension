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

def first_file(*paths):
    for path in paths:
        if os.path.isfile(path):
            return path
    common.die("none of these exist: " + " ".join(paths))


def install_file(src, dest, mode):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    os.chmod(dest, mode)


def linked_libs(binary):
    result = subprocess.run(["ldd", str(binary)], capture_output=True, text=True, check=True)
    libs = []
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[1] == "=>" and fields[2].startswith("/"):
            libs.append(fields[2])
    return libs


def dir_size_mb(path):
    total = 0
    for root, _, names in os.walk(path):
        for name in names:
            total += os.path.getsize(os.path.join(root, name))
    return max(64, (total + 1024 * 1024 - 1) // (1024 * 1024) + 8)


def support_revision():
    support = os.path.join(common.REPO_ROOT, "third_party", "matter_support")
    result = subprocess.run(
        ["git", "-C", support, "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "unknown\n"
    return result.stdout.strip() + "\n"


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

    python = Path(first_file("/usr/bin/python3.12", "/usr/bin/python3"))
    install_file(python, guest_bin / "python3", 0o755)
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

    libs = set()
    for binary in guest_bin.iterdir():
        if binary.is_file():
            libs.update(linked_libs(binary))
    dynload = staging / "lib" / "python3.12" / "lib-dynload"
    if dynload.is_dir():
        for binary in dynload.iterdir():
            if binary.suffix == ".so":
                libs.update(linked_libs(binary))
    for lib in sorted(libs):
        shutil.copy2(lib, lib_dir / os.path.basename(lib))
    shutil.copy2("/lib/ld-linux-aarch64.so.1", staging / "lib" / "ld-linux-aarch64.so.1")


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
        (staging / "MATTER_SUPPORT_REVISION").write_text(support_revision(), encoding="utf-8")
        stage_python_runtime(staging)

        output.parent.mkdir(parents=True, exist_ok=True)
        output.unlink(missing_ok=True)
        size_mb = dir_size_mb(staging)
        subprocess.run(
            [
                common.find_mkfs_ext2(),
                "-q",
                "-d",
                str(staging),
                "-L",
                "matter-provision",
                str(output),
                f"{size_mb}M",
            ],
            check=True,
        )
        print(f"Built {output} ({size_mb}M)")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    out_dir = Path(common.RENODE_INTEGRATION_DIR) / "out" / "guest-rootfs"
    output = out_dir / "matter-provision.ext2"
    build_provision_ext2(output)


if __name__ == "__main__":
    main()
