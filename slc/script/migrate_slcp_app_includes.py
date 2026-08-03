#!/usr/bin/env python3
"""Rewrite .slcp include blocks from matter_sdk paths to in-package path: include.

Only touches include entries whose path ends with:
  .../third_party/matter_sdk/examples/<app>/silabs/include

Leaves other include blocks (customer, *-common, etc.) unchanged.

Usage (repo root):
  python3 slc/script/migrate_slcp_app_includes.py
  python3 slc/script/migrate_slcp_app_includes.py --dry-run
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_SDK_SILABS_INCLUDE = re.compile(
    r"^(?P<list_indent>\s+)- path: "
    r"(?:\.\./)+third_party/matter_sdk/examples/[^/\s]+/silabs/include\s*$"
)

_IN_PACKAGE_INCLUDE = re.compile(r"^(?P<list_indent>\s+)- path: include\s*$")

_DIRECTORY_INCLUDE = re.compile(r"^\s+directory: include\s*$")


def _repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def _strip_in_package_directory_lines(text: str) -> tuple[str, int]:
    """Remove directory: include after an in-package include entry."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    changes = 0
    in_in_package_entry = False
    in_package_list_indent: str | None = None
    for line in lines:
        stripped = line.rstrip("\n")
        m = _IN_PACKAGE_INCLUDE.match(stripped)
        if m:
            in_in_package_entry = True
            in_package_list_indent = m.group("list_indent")
            out.append(line)
            continue
        if in_in_package_entry and _DIRECTORY_INCLUDE.match(stripped):
            changes += 1
            in_in_package_entry = False
            in_package_list_indent = None
            continue
        if (
            in_in_package_entry
            and in_package_list_indent is not None
            and re.match(rf"^{re.escape(in_package_list_indent)}- path:", stripped)
        ):
            in_in_package_entry = False
            in_package_list_indent = None
        out.append(line)
    return "".join(out), changes


def migrate_file(path: Path, dry_run: bool) -> int:
    original = path.read_text(encoding="utf-8")
    migrated, sdk_changes = _migrate_sdk_include_paths(original)
    updated, dir_changes = _strip_in_package_directory_lines(migrated)
    changes = sdk_changes + dir_changes
    if changes and not dry_run and updated != original:
        path.write_text(updated, encoding="utf-8")
    return changes


def _migrate_sdk_include_paths(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    changes = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        match = _SDK_SILABS_INCLUDE.match(line.rstrip("\n"))
        if not match:
            out.append(line)
            i += 1
            continue
        list_indent = match.group("list_indent")
        out.append(f"{list_indent}- path: include\n")
        changes += 1
        i += 1
        sibling_re = re.compile(rf"^{re.escape(list_indent)}- path:")
        while i < len(lines):
            stripped = lines[i].rstrip("\n")
            if _DIRECTORY_INCLUDE.match(stripped):
                i += 1
                continue
            if sibling_re.match(stripped):
                break
            if re.match(r"^[a-z_][\w]*:", stripped) and not stripped.startswith(" "):
                break
            out.append(lines[i])
            i += 1
    return "".join(out), changes


def migrate_slcp_text(text: str) -> tuple[str, int]:
    migrated, sdk_changes = _migrate_sdk_include_paths(text)
    updated, dir_changes = _strip_in_package_directory_lines(migrated)
    return updated, sdk_changes + dir_changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_repo_root_from_script(),
        help="matter_extension repo root",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing files",
    )
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    apps_root = repo_root / "slc" / "apps"
    total_files = 0
    total_changes = 0
    for slcp in sorted(apps_root.rglob("*.slcp")):
        n = migrate_file(slcp, args.dry_run)
        if n:
            total_files += 1
            total_changes += n
            action = "would update" if args.dry_run else "updated"
            rel = slcp.relative_to(repo_root)
            print(f"{action} {rel} ({n} change(s))")
    print(f"done: {total_changes} change(s) in {total_files} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
