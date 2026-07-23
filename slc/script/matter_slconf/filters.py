"""SDK path filtering rules for Matter app slconf generation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional
import re

SLC_SDK_PATH_DENYLIST = frozenset({
    "matter_app",
    "cmake",
    "ninja",
    "gcc-arm-none-eabi",
    "llvm-arm-toolchain-for-embedded",
    "commander",
    "slc-cli",
    "slc_cli",
    "slc_cli_base",
    "python",
    "java21",
    "zap",
})

WIFI_SOC_EXCLUDE_PACKAGES = frozenset({
    "nwp_firmware_siwx91x",
    "openthread",
    "openthread_stack",
    "multiprotocol",
    "common_15_4",
    "rail_library",
})

THREAD_EXCLUDE_PACKAGES = frozenset({
    "wifi",
    "platform_siwx91x",
    "platform_nwp_siwx91x",
    "bluetooth_le_siwx91x",
    "netstack_silabs_lwip",
    "nwp_firmware_siwx91x",
})

WIFI_NCP_ONLY_PACKAGES = frozenset({
    "nwp_firmware_siwx91x",
})


def path_is_slc_extension_root(package_path: str) -> bool:
    root = Path(package_path)
    if not root.is_dir():
        return False
    if (root / "simplicity_sdk.slcs").is_file():
        return True
    return any(root.glob("*.slce"))


def parse_slconf_path_comment_package(line: str) -> Optional[str]:
    match = re.search(r"#\s*([^/\s]+)/", line)
    if not match:
        return None
    return match.group(1)


def detect_app_stack_type(app_dir: Path, slcp_name: str = "") -> str:
    posix = app_dir.as_posix().lower()
    slcp_lower = slcp_name.lower()
    if "/thread/" in posix or posix.endswith("/thread"):
        return "thread"
    if "/wifi/" in posix or posix.endswith("/wifi"):
        if "ncp" in slcp_lower:
            return "wifi_ncp"
        return "wifi_soc"
    if "ncp" in slcp_lower:
        return "wifi_ncp"
    return "unified"


def exclude_packages_for_app_type(app_type: str) -> frozenset[str]:
    if app_type == "thread":
        return THREAD_EXCLUDE_PACKAGES
    if app_type == "wifi_soc":
        return WIFI_SOC_EXCLUDE_PACKAGES | WIFI_NCP_ONLY_PACKAGES
    if app_type == "wifi_ncp":
        return WIFI_SOC_EXCLUDE_PACKAGES - WIFI_NCP_ONLY_PACKAGES
    return frozenset()


def filter_slc_sdk_paths(
    paths: list[str],
    *,
    app_type: str = "unified",
    raw_slconf_lines: Optional[dict[str, str]] = None,
) -> list[str]:
    excluded = SLC_SDK_PATH_DENYLIST | exclude_packages_for_app_type(app_type)
    filtered: list[str] = []
    seen: set[str] = set()

    for path in paths:
        if not path or path in seen or not os.path.isdir(path):
            continue
        pkg_name = None
        if raw_slconf_lines and path in raw_slconf_lines:
            pkg_name = parse_slconf_path_comment_package(raw_slconf_lines[path])
        if pkg_name and pkg_name in excluded:
            continue
        if not path_is_slc_extension_root(path):
            continue
        seen.add(path)
        filtered.append(path)

    return filtered
