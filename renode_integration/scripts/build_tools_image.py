#!/usr/bin/env python3
"""
@file build_tools_image.py
@brief Build matter-tools.ext2 on Ubuntu arm64 for the simulated Matter hub.

otbr-agent and ot-ctl come from the upstream ot-br-posix build. BlueZ, D-Bus, their
configs, chip-tool, and shared libraries come from Ubuntu packages.
Intended to run on ubuntu-24.04-arm in CI, use fetch_bundle.py on other hosts.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import common

GUEST_BINS = ("btattach", "btmgmt", "dbus-daemon", "dbus-send", "dbus-monitor")
APT_PACKAGES = (
    "sudo",
    "git",
    "ca-certificates",
    "python3",
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


def ubuntu_version_id():
    values = {}
    with open("/etc/os-release", encoding="utf-8") as handle:
        for line in handle:
            if "=" not in line:
                continue
            key, value = line.strip().split("=", 1)
            values[key] = value.strip('"')
    return values.get("VERSION_ID", "")


def find_ot_ctl(build_dir):
    for root, _, names in os.walk(build_dir):
        if "ot-ctl" not in names:
            continue
        path = os.path.join(root, "ot-ctl")
        if os.access(path, os.X_OK):
            return path
    common.die(f"ot-ctl not found under {build_dir}")


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
        common.install_file(otbr_build / "src" / "agent" / "otbr-agent", guest_bin / "otbr-agent", 0o755)
        common.install_file(find_ot_ctl(otbr_build), guest_bin / "ot-ctl", 0o755)
        common.install_file(chip_tool, guest_bin / "chip-tool", 0o755)
        for name in GUEST_BINS:
            common.install_file(shutil.which(name), guest_bin / name, 0o755)
        bluetoothd = common.first_file("/usr/libexec/bluetooth/bluetoothd", "/usr/lib/bluetooth/bluetoothd")
        common.install_file(bluetoothd, guest_bin / "bluetoothd", 0o755)

        common.install_file(Path("/usr/share/dbus-1/system.conf"), staging / "usr/share/dbus-1/system.conf", 0o644)
        bluetooth_conf = common.first_file(
            "/usr/share/dbus-1/system.d/bluetooth.conf",
            "/etc/dbus-1/system.d/bluetooth.conf",
        )
        common.install_file(bluetooth_conf, staging / "etc/dbus-1/system.d/bluetooth.conf", 0o644)
        common.install_file(
            otbr_build / "src/agent/otbr-agent.conf",
            staging / "etc/dbus-1/system.d/otbr-agent.conf",
            0o644,
        )

        common.copy_dynamic_libs_for_binaries(
            guest_bin.iterdir(),
            lib_dir,
            staging / "lib" / "ld-linux-aarch64.so.1",
        )

        out_dir = Path(common.RENODE_INTEGRATION_DIR) / "out" / "guest-rootfs"
        output = out_dir / "matter-tools.ext2"
        common.make_ext2_from_staging(staging, output, "matter-tools", extra_mb=64)
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
