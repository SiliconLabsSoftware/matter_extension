#!/usr/bin/env python3
"""Sync example AppConfig headers into matter_app app include/ dirs.

Used before local export/generate so .slcp `path: include` resolves without
shipping third_party/matter_sdk inside matter_app.

Usage (from repo root):
  python3 slc/script/sync_app_includes.py
  python3 slc/script/sync_app_includes.py --repo-root /path/to/matter_extension
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _add_packages_path(repo_root: Path) -> None:
    packages = repo_root / "packages"
    if packages.is_dir() and str(packages) not in sys.path:
        sys.path.insert(0, str(packages))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="matter_extension repo root (default: cwd)",
    )
    args = parser.parse_args()
    repo_root = (args.repo_root or Path.cwd()).resolve()
    _add_packages_path(repo_root)

    from _shared.app_include_sync import resolve_sdk_root_for_sync, sync_app_includes

    sdk_root = resolve_sdk_root_for_sync(repo_root)
    written = sync_app_includes(repo_root, sdk_root)
    for path in written:
        print(f"synced {path.relative_to(repo_root)}")
    print(f"synced {len(written)} header(s) from {sdk_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
