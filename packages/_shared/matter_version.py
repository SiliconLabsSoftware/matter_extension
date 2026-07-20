"""Matter SLC line version vs Conan package version helpers."""

from __future__ import annotations

import os
import re
from pathlib import Path

import yaml

_LINE_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
_MATTER_PACKAGE_VERSION_FILE = Path("slc") / "script" / "matter_package_version"


def _slce_candidates(repo_root: Path) -> list[Path]:
    recipe_root = Path(__file__).resolve().parent
    return [
        repo_root / "matter.slce",
        recipe_root.parent / "matter.slce",
        recipe_root / "matter.slce",
    ]


def _read_slce_version(slce_path: Path) -> str:
    with slce_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    version = str(data.get("version", "")).strip()
    if not version:
        raise RuntimeError(f"Version field missing or empty in {slce_path}")
    return version


def resolve_matter_line_version(repo_root: Path) -> str:
    """SLC line version from matter.slce (e.g. 2.10.0)."""
    for slce_path in _slce_candidates(repo_root):
        if not slce_path.is_file():
            continue
        version = _read_slce_version(slce_path)
        if not _LINE_VERSION_RE.match(version):
            raise RuntimeError(
                f"matter.slce version must be X.Y.Z line version, got {version!r} in {slce_path}"
            )
        return version
    raise FileNotFoundError(f"matter.slce not found under {repo_root}")


def resolve_matter_conan_version(repo_root: Path) -> str:
    """Concrete Conan ref used for export-pkg (e.g. 2.10.0-alpha.2)."""
    env_version = os.environ.get("MATTER_PACKAGE_VERSION", "").strip()
    if env_version:
        return env_version

    version_file = repo_root / _MATTER_PACKAGE_VERSION_FILE
    if version_file.is_file():
        version = version_file.read_text(encoding="utf-8").strip()
        if version:
            return version

    raise FileNotFoundError(
        "Matter Conan version not found. Set MATTER_PACKAGE_VERSION or create "
        f"{_MATTER_PACKAGE_VERSION_FILE}"
    )


def _line_version_bounds(line_version: str) -> tuple[str, str]:
    if not _LINE_VERSION_RE.match(line_version):
        raise ValueError(f"Expected X.Y.Z line version, got {line_version!r}")
    major, minor, patch = line_version.split(".")
    upper = f"{major}.{minor}.{int(patch) + 1}"
    return line_version, upper


def matter_slt_range(line_version: str) -> str:
    """SLT pkg.slt version range (WiFi-style, no brackets)."""
    lower, upper = _line_version_bounds(line_version)
    return f">={lower} <{upper}"


def matter_conan_range(line_version: str) -> str:
    """Conan requires() version range."""
    lower, upper = _line_version_bounds(line_version)
    return f"[>={lower} <{upper},include_prerelease]"
