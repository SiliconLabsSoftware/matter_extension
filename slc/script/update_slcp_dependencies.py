#!/usr/bin/env python3
"""Sync .slcp sdk / sdk_extension headers from dependency_versions.yaml.

Example:
  python3 slc/script/update_slcp_dependencies.py \\
    --simplicity-sdk 2026.12.0 \\
    --matter 2.10.0

  python3 slc/script/update_slcp_dependencies.py --check
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SHARED_DIR = _REPO_ROOT / "packages" / "_shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from matter_version import resolve_matter_line_version  # noqa: E402

sys.path.insert(0, str(_REPO_ROOT / "slc"))

SECTION_START = re.compile(
    r"(?m)^(component:|provides:|requires:|config_file:|template_contribution:"
    r"|readme:|ui_hints:|other_file:|post_build:|filter:|tag:|define:"
    r"|toolchain_settings:|configuration:)"
)
SDK_SECTION = re.compile(r"(?ms)^sdk:\n(?:  [^\n]+\n)+")
SDK_EXTENSION_SECTION = re.compile(
    r"(?ms)^sdk_extension:\n(?:  - id: [^\n]+\n    version: \"[^\"]+\"\n    vendor: silabs\n)+"
)

# SLC extension ids listed in .slcp headers (not every Conan dep in dependency_versions.yaml).
THREAD_SLCP_EXTENSIONS = ("thread", "multiprotocol", "zigbee")
WIFI_SOC_SLCP_EXTENSIONS = ("wifi", "platform_siwx91x", "bluetooth_le_siwx91x")
WIFI_NCP_SLCP_EXTENSIONS = (
    "wifi",
    "platform_siwx91x",
    "platform_nwp_siwx91x",
    "bluetooth_le_siwx91x",
)


def line_version_from_conan_range(range_str: str) -> str:
    """Extract SLC line version from a Conan range string."""
    match = re.search(r">=\s*(\d+\.\d+\.\d+)", str(range_str))
    if match:
        return match.group(1)
    stripped = str(range_str).strip().strip("[]")
    if re.fullmatch(r"\d+\.\d+\.\d+", stripped):
        return stripped
    raise ValueError(f"Cannot parse Conan range: {range_str!r}")


def grouped_line_versions(deps_file: Path) -> dict[str, dict[str, str]]:
    import yaml

    with deps_file.open("r", encoding="utf-8") as f:
        grouped = yaml.safe_load(f) or {}

    result: dict[str, dict[str, str]] = {}
    for group in ("thread", "wifi"):
        entries = grouped.get(group) or {}
        result[group] = {
            name: line_version_from_conan_range(version)
            for name, version in entries.items()
        }
    return result


def detect_app_type(slcp_path: Path) -> str:
    posix = slcp_path.as_posix().lower()
    name = slcp_path.name.lower()
    if "/bootloaders/" in posix:
        return "bootloader"
    if "/openthread_border_router_doc/" in posix:
        return "doc"
    if "/thread/" in posix:
        return "thread"
    if "/wifi/" in posix or posix.endswith("/wifi"):
        if "ncp" in name:
            return "wifi_ncp"
        return "wifi_soc"
    if "ncp" in name:
        return "wifi_ncp"
    return "other"


def extension_version(ext_id: str, versions: dict[str, dict[str, str]]) -> str:
    if ext_id in versions.get("thread", {}):
        return versions["thread"][ext_id]
    if ext_id in versions.get("wifi", {}):
        return versions["wifi"][ext_id]
    if ext_id == "platform_siwx91x":
        return versions["wifi"]["wifi"]
    raise KeyError(f"No version mapping for sdk_extension id {ext_id!r}")


def build_extensions(
    app_type: str,
    *,
    matter_version: str,
    versions: dict[str, dict[str, str]],
) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = [("matter", matter_version)]

    if app_type == "thread":
        for ext_id in THREAD_SLCP_EXTENSIONS:
            entries.append((ext_id, extension_version(ext_id, versions)))
    elif app_type == "wifi_soc":
        for ext_id in WIFI_SOC_SLCP_EXTENSIONS:
            entries.append((ext_id, extension_version(ext_id, versions)))
    elif app_type == "wifi_ncp":
        for ext_id in WIFI_NCP_SLCP_EXTENSIONS:
            entries.append((ext_id, extension_version(ext_id, versions)))
  # bootloader: matter only

    return entries


def format_sdk_block(simplicity_version: str) -> str:
    return (
        "sdk:\n"
        "  id: simplicity_sdk\n"
        f'  version: "{simplicity_version}"\n'
        "  vendor: silabs\n"
    )


def format_sdk_extension_block(extensions: list[tuple[str, str]]) -> str:
    lines = ["sdk_extension:"]
    for ext_id, version in extensions:
        lines.append(f"  - id: {ext_id}")
        lines.append(f'    version: "{version}"')
        lines.append("    vendor: silabs")
    return "\n".join(lines) + "\n"


def strip_sdk_sections(text: str) -> str:
    text = SDK_EXTENSION_SECTION.sub("", text)
    text = SDK_SECTION.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def insert_headers(
    text: str,
    *,
    sdk_block: str | None,
    extension_block: str,
) -> str:
    match = SECTION_START.search(text)
    header = ""
    if sdk_block:
        header += sdk_block
    header += extension_block
    if not match:
        return text.rstrip() + "\n\n" + header
    pos = match.start()
    prefix = text[:pos].rstrip() + "\n\n"
    suffix = text[pos:]
    if not suffix.startswith("\n"):
        header = header.rstrip() + "\n\n"
    return prefix + header + suffix


def update_slcp(
    path: Path,
    *,
    simplicity_version: str | None,
    matter_version: str,
    versions: dict[str, dict[str, str]],
) -> bool:
    app_type = detect_app_type(path)
    if app_type in ("doc", "other"):
        return False

    extensions = build_extensions(app_type, matter_version=matter_version, versions=versions)
    extension_block = format_sdk_extension_block(extensions)
    sdk_block = format_sdk_block(simplicity_version) if simplicity_version and app_type != "bootloader" else None

    text = path.read_text(encoding="utf-8")
    stripped = strip_sdk_sections(text)
    updated = insert_headers(stripped, sdk_block=sdk_block, extension_block=extension_block)
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update .slcp sdk/sdk_extension headers from dependency_versions.yaml"
    )
    parser.add_argument(
        "--simplicity-sdk",
        help="simplicity_sdk version for sdk: block (e.g. 2026.12.0)",
    )
    parser.add_argument(
        "--matter",
        help="matter extension line version (default: matter.slce)",
    )
    parser.add_argument(
        "--deps-file",
        type=Path,
        default=_REPO_ROOT / "slc" / "script" / "dependency_versions.yaml",
        help="Stack dependency versions YAML",
    )
    parser.add_argument(
        "--apps-root",
        type=Path,
        default=_REPO_ROOT / "slc" / "apps",
        help="Root directory to search for .slcp files",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report files that would change; exit 1 if any drift",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print files that would change without writing",
    )
    args = parser.parse_args()

    if not args.simplicity_sdk and not args.check:
        print("ERROR: --simplicity-sdk is required when updating files", file=sys.stderr)
        return 1

    matter_version = args.matter or resolve_matter_line_version(_REPO_ROOT)
    if not args.deps_file.is_file():
        print(f"ERROR: dependency file not found: {args.deps_file}", file=sys.stderr)
        return 1

    versions = grouped_line_versions(args.deps_file)
    changed: list[Path] = []
    for slcp in sorted(args.apps_root.rglob("*.slcp")):
        text = slcp.read_text(encoding="utf-8")
        app_type = detect_app_type(slcp)
        if app_type in ("doc", "other"):
            continue

        extensions = build_extensions(app_type, matter_version=matter_version, versions=versions)
        extension_block = format_sdk_extension_block(extensions)
        sdk_block = (
            format_sdk_block(args.simplicity_sdk)
            if args.simplicity_sdk and app_type != "bootloader"
            else None
        )
        stripped = strip_sdk_sections(text)
        updated = insert_headers(stripped, sdk_block=sdk_block, extension_block=extension_block)
        if updated == text:
            continue
        changed.append(slcp)
        if args.dry_run or args.check:
            print(slcp.relative_to(_REPO_ROOT))
        elif not args.check:
            slcp.write_text(updated, encoding="utf-8")

    if args.check and changed:
        print(f"{len(changed)} .slcp file(s) out of date", file=sys.stderr)
        return 1
    if not args.check and not args.dry_run:
        print(f"Updated {len(changed)} .slcp file(s)")
        if args.simplicity_sdk:
            print(f"  simplicity_sdk: {args.simplicity_sdk}")
        print(f"  matter: {matter_version}")
    elif args.dry_run:
        print(f"Would update {len(changed)} .slcp file(s)")
    else:
        print(f"OK: {len(changed)} .slcp file(s) would need updates" if changed else "OK: all .slcp headers current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
