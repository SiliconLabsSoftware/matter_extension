#!/usr/bin/env python3
"""Build matter-tools.ext2 on Ubuntu arm64.

otbr-agent and ot-ctl come from the upstream ot-br-posix build. BlueZ, D-Bus, their
configs, chip-tool, and shared libraries come from the Ubuntu packages.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import common

GUEST_BINS = ("btattach", "btmgmt", "dbus-daemon", "dbus-send", "dbus-monitor")
PROVISION_SRC = Path(common.REPO_ROOT) / "third_party" / "matter_support" / "provision"
PROVISION_REQUIREMENTS = PROVISION_SRC / "requirements.txt"
STDLIB_IGNORE = shutil.ignore_patterns(
    "__pycache__", "test", "tests", "idlelib", "tkinter", "turtledemo", "ensurepip", "lib2to3"
)
PROVISION_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "test", "temp", "latest.json")
APT_PACKAGES = (
    "sudo",
    "git",
    "ca-certificates",
    "python3",
    "python3-pip",
    "e2fsprogs",
    "bluez",
    "dbus",
)


def apt_install(packages):
    prefix = [] if os.geteuid() == 0 else ["sudo"]
    env = os.environ.copy()
    env["DEBIAN_FRONTEND"] = "noninteractive"
    subprocess.run([*prefix, "apt-get", "update", "-q"], env=env, check=True)
    subprocess.run(
        [*prefix, "apt-get", "install", "-y", "-q", "--no-install-recommends", *packages],
        env=env,
        check=True,
    )


def first_file(*paths):
    for path in paths:
        if os.path.isfile(path):
            return path
    common.die("none of these exist: " + " ".join(paths))


def install_file(src, dest, mode):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    os.chmod(dest, mode)


def ubuntu_version_id():
    values = {}
    with open("/etc/os-release", encoding="utf-8") as handle:
        for line in handle:
            if "=" not in line:
                continue
            key, value = line.strip().split("=", 1)
            values[key] = value.strip('"')
    return values.get("VERSION_ID", "")


def dir_size_mb(path):
    total = 0
    for root, _, names in os.walk(path):
        for name in names:
            total += os.path.getsize(os.path.join(root, name))
    return (total + 1024 * 1024 - 1) // (1024 * 1024) + 64


def linked_libs(binary):
    result = subprocess.run(["ldd", str(binary)], capture_output=True, text=True, check=True)
    libs = []
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) >= 3 and fields[1] == "=>" and fields[2].startswith("/"):
            libs.append(fields[2])
    return libs


def find_ot_ctl(build_dir):
    for root, _, names in os.walk(build_dir):
        if "ot-ctl" not in names:
            continue
        path = os.path.join(root, "ot-ctl")
        if os.access(path, os.X_OK):
            return path
    common.die(f"ot-ctl not found under {build_dir}")


def ubuntu_python3():
    """python3 from apt."""
    binary = Path("/usr/bin/python3")
    if not binary.is_file():
        common.die("apt python3 not found at /usr/bin/python3")
    binary = Path(os.path.realpath(binary))

    stdlib = Path(
        subprocess.run(
            [str(binary), "-c", "import sysconfig; print(sysconfig.get_path('stdlib'))"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )
    if not stdlib.is_dir():
        common.die(f"python stdlib not found at {stdlib}")

    py_version = subprocess.run(
        [str(binary), "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return binary, py_version, stdlib


def stage_provision_tooling(staging: Path) -> None:
    if not PROVISION_SRC.is_dir():
        common.die(f"provision tool not found at {PROVISION_SRC}")

    python_bin, py_version, stdlib = ubuntu_python3()
    install_file(python_bin, staging / "guest-bin" / "python3", 0o755)
    stdlib_dest = staging / "usr" / "lib" / stdlib.name
    shutil.copytree(stdlib, stdlib_dest, ignore=STDLIB_IGNORE, symlinks=False)
    if not (stdlib_dest / "encodings").is_dir():
        common.die(f"incomplete python stdlib staged at {stdlib_dest}")

    stdlib_zip = Path(f"/usr/lib/python{py_version.replace('.', '')}.zip")
    if stdlib_zip.is_file():
        install_file(stdlib_zip, staging / "usr" / "lib" / stdlib_zip.name, 0o644)

    dest = staging / "opt" / "provision"
    shutil.copytree(PROVISION_SRC, dest / "tool", ignore=PROVISION_IGNORE)
    if not PROVISION_REQUIREMENTS.is_file():
        common.die(f"provision requirements not found at {PROVISION_REQUIREMENTS}")
    subprocess.run(
        [
            str(python_bin),
            "-m",
            "pip",
            "install",
            "-q",
            "--no-cache-dir",
            "--only-binary=:all:",
            "--target",
            str(dest / "site-packages"),
            "-r",
            str(PROVISION_REQUIREMENTS),
        ],
        check=True,
    )

    lib_dir = staging / "usr" / "lib" / "aarch64-linux-gnu"
    lib_dir.mkdir(parents=True, exist_ok=True)
    binaries = [staging / "guest-bin" / "python3"]
    for root in (staging / "usr" / "lib", staging / "opt" / "provision" / "site-packages"):
        if root.is_dir():
            binaries.extend(root.rglob("*.so"))
    libs = set()
    for binary in binaries:
        if binary.is_file():
            libs.update(linked_libs(binary))
    for lib in sorted(libs):
        target = lib_dir / Path(lib).name
        if not target.exists():
            shutil.copy2(lib, target)


def build(chip_tool):
    apt_install(APT_PACKAGES)
    pinned = str(common.manifest_lookup("tools_image.ubuntu_version"))
    actual = ubuntu_version_id()
    if actual != pinned:
        print(f"warning: building on Ubuntu {actual}, manifest pins {pinned}")

    work = Path(tempfile.mkdtemp())
    try:
        otbr_src = work / "ot-br-posix"
        otbr_build = work / "otbr-build"
        staging = work / "staging"
        subprocess.run(["git", "init", "-q", str(otbr_src)], check=True)
        subprocess.run(
            ["git", "-C", str(otbr_src), "remote", "add", "origin", common.manifest_lookup("ot_br_posix.repo")],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(otbr_src), "fetch", "-q", "--depth", "1", "origin", common.manifest_lookup("ot_br_posix.commit")],
            check=True,
        )
        subprocess.run(["git", "-C", str(otbr_src), "checkout", "-q", "FETCH_HEAD"], check=True)

        env = os.environ.copy()
        env["PLATFORM"] = "ubuntu"
        subprocess.run(["./script/bootstrap"], cwd=otbr_src, env=env, check=True)
        env["OTBR_BUILD_DIR"] = str(otbr_build)
        env["OTBR_TARGET"] = "otbr-agent"
        cmake_args = list(common.manifest_lookup("ot_br_posix.cmake_args"))
        cmake_args.append("-DProtobuf_PROTOC_EXECUTABLE=/usr/bin/protoc")
        subprocess.run(["./script/cmake-build", *cmake_args], cwd=otbr_src, env=env, check=True)

        guest_bin = staging / "guest-bin"
        lib_dir = staging / "usr" / "lib" / "aarch64-linux-gnu"
        guest_bin.mkdir(parents=True)
        lib_dir.mkdir(parents=True)
        (staging / "lib").mkdir()
        install_file(otbr_build / "src" / "agent" / "otbr-agent", guest_bin / "otbr-agent", 0o755)
        install_file(find_ot_ctl(otbr_build), guest_bin / "ot-ctl", 0o755)
        install_file(chip_tool, guest_bin / "chip-tool", 0o755)
        for name in GUEST_BINS:
            install_file(shutil.which(name), guest_bin / name, 0o755)
        bluetoothd = first_file("/usr/libexec/bluetooth/bluetoothd", "/usr/lib/bluetooth/bluetoothd")
        install_file(bluetoothd, guest_bin / "bluetoothd", 0o755)

        install_file(Path("/usr/share/dbus-1/system.conf"), staging / "usr/share/dbus-1/system.conf", 0o644)
        bluetooth_conf = first_file(
            "/usr/share/dbus-1/system.d/bluetooth.conf",
            "/etc/dbus-1/system.d/bluetooth.conf",
        )
        install_file(bluetooth_conf, staging / "etc/dbus-1/system.d/bluetooth.conf", 0o644)
        install_file(
            otbr_build / "src/agent/otbr-agent.conf",
            staging / "etc/dbus-1/system.d/otbr-agent.conf",
            0o644,
        )

        stage_provision_tooling(staging)

        libs = set()
        for path in staging.rglob("*"):
            if path.is_file() and (path.parent.name == "guest-bin" or path.suffix == ".so"):
                libs.update(linked_libs(path))
        for lib in sorted(libs):
            target = lib_dir / os.path.basename(lib)
            if not target.exists():
                shutil.copy2(lib, target)
        shutil.copy2("/lib/ld-linux-aarch64.so.1", staging / "lib" / "ld-linux-aarch64.so.1")

        out_dir = Path(common.RENODE_INTEGRATION_DIR) / "out" / "guest-rootfs"
        output = out_dir / "matter-tools.ext2"
        out_dir.mkdir(parents=True, exist_ok=True)
        output.unlink(missing_ok=True)
        size_mb = dir_size_mb(staging)
        subprocess.run(
            ["mkfs.ext2", "-q", "-d", str(staging), "-L", "matter-tools", str(output), f"{size_mb}M"],
            check=True,
        )
        print(f"Built {output} ({size_mb}M)")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    chip_tool = os.environ.get("CHIP_TOOL", "")
    if not chip_tool or not os.path.isfile(chip_tool):
        common.die("set CHIP_TOOL to a linux-arm64 chip-tool binary (e.g. from linux-arm64-chip-tool-ipv6only-clang)")

    native = os.uname().sysname == "Linux" and os.uname().machine == "aarch64" and shutil.which("apt-get")
    if not native:
        common.die(
            "matter-tools.ext2 is built in CI (ubuntu-24.04-arm). "
            "Run scripts/fetch_bundle.py to pull the common bundle locally."
        )
    build(chip_tool)


if __name__ == "__main__":
    main()
