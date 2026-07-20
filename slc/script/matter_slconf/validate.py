"""Validate .slcp sdk/sdk_extension versions against installed package metadata."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import yaml

from .filters import path_is_slc_extension_root
from .slconf_io import parse_pkg_slconf_sdk_paths

_LINE_VERSION_RE = re.compile(r"^(\d+\.\d+\.\d+)")


def _slc_line_version(version: str) -> str:
    match = _LINE_VERSION_RE.match(version.strip())
    return match.group(1) if match else version.strip()


def _versions_compatible(requested: str, installed: str) -> bool:
    return _slc_line_version(requested) == _slc_line_version(installed)


def _read_slce_version(package_path: Path) -> Optional[str]:
    for slce in package_path.glob("*.slce"):
        data = yaml.safe_load(slce.read_text(encoding="utf-8")) or {}
        version = data.get("version")
        if version is not None:
            return str(version)
    slcs = package_path / "simplicity_sdk.slcs"
    if slcs.is_file():
        data = yaml.safe_load(slcs.read_text(encoding="utf-8")) or {}
        return str(data.get("sdk_version") or data.get("version") or "")
    return None


def _extension_id_for_path(package_path: Path) -> Optional[str]:
    for slce in package_path.glob("*.slce"):
        data = yaml.safe_load(slce.read_text(encoding="utf-8")) or {}
        ext_id = data.get("id")
        if ext_id:
            return str(ext_id)
    slcs = package_path / "simplicity_sdk.slcs"
    if slcs.is_file():
        data = yaml.safe_load(slcs.read_text(encoding="utf-8")) or {}
        return str(data.get("id") or "simplicity_sdk")
    return None


def _load_slcp_sdk_blocks(slcp_path: Path) -> tuple[Optional[dict], list[dict]]:
    data = yaml.safe_load(slcp_path.read_text(encoding="utf-8")) or {}
    sdk = data.get("sdk")
    extensions = data.get("sdk_extension") or []
    if not isinstance(extensions, list):
        extensions = []
    return sdk, extensions


def validate_slcp_against_slconf(slcp_path: Path, slconf_path: Path) -> list[str]:
    """Return a list of validation error messages (empty if ok)."""
    errors: list[str] = []
    sdk, extensions = _load_slcp_sdk_blocks(slcp_path)
    available: dict[str, str] = {}

    for path_str in parse_pkg_slconf_sdk_paths(slconf_path):
        pkg_path = Path(path_str)
        if not path_is_slc_extension_root(path_str):
            continue
        ext_id = _extension_id_for_path(pkg_path)
        version = _read_slce_version(pkg_path)
        if ext_id and version:
            available[ext_id] = version

    if sdk:
        sdk_id = str(sdk.get("id", ""))
        sdk_version = str(sdk.get("version", ""))
        installed = available.get(sdk_id)
        if installed and not _versions_compatible(sdk_version, installed):
            errors.append(
                f"sdk {sdk_id}: slcp requests {sdk_version}, package has {installed}"
            )
        elif sdk_id and sdk_id not in available:
            errors.append(f"sdk {sdk_id} not found on sdk-package-path")

    for ext in extensions:
        ext_id = str(ext.get("id", ""))
        ext_version = str(ext.get("version", ""))
        installed = available.get(ext_id)
        if not installed:
            errors.append(f"extension {ext_id} not found on sdk-package-path")
        elif not _versions_compatible(ext_version, installed):
            errors.append(
                f"extension {ext_id}: slcp requests {ext_version}, package has {installed}"
            )

    return errors
