#!/usr/bin/env python3
"""Write filtered autogen/slc-sdk.slconf for an app directory after slt install."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Filter SLT pkg.slconf sdk-package-path for slc generate"
    )
    parser.add_argument(
        "--app-dir",
        dest="app_dir",
        type=Path,
        help="App directory containing autogen/pkg.slconf",
    )
    parser.add_argument(
        "app_dir_pos",
        nargs="?",
        type=Path,
        help="App directory (alternative to --app-dir)",
    )
    parser.add_argument(
        "--slcp-name",
        "--slcp",
        default="",
        dest="slcp_name",
        help="Optional .slcp basename for SoC vs NCP detection",
    )
    args = parser.parse_args()

    app_dir = args.app_dir or args.app_dir_pos
    if app_dir is None:
        parser.error("app directory is required (--app-dir or positional)")

    repo_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo_root / "slc"))
    from script.matter_slconf.slconf_io import write_filtered_app_slconf

    try:
        out = write_filtered_app_slconf(app_dir, slcp_name=args.slcp_name)
    except (FileNotFoundError, RuntimeError) as exc:
        print(exc, file=sys.stderr)
        return 1

    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
