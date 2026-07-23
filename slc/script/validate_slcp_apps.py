#!/usr/bin/env python3
"""CI helper: validate .slcp sdk/extension versions against autogen/pkg.slconf."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Matter app .slcp headers")
    parser.add_argument(
        "--apps-root",
        type=Path,
        default=None,
        help="Defaults to <repo>/slc/apps",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    apps_root = args.apps_root or (repo_root / "slc" / "apps")
    sys.path.insert(0, str(repo_root / "slc"))
    from script.matter_slconf.validate import validate_slcp_against_slconf

    failures = 0
    checked = 0
    for pkg_slt in sorted(apps_root.rglob("pkg.slt")):
        app_dir = pkg_slt.parent
        slconf = app_dir / "autogen" / "pkg.slconf"
        if not slconf.is_file():
            continue
        for slcp in sorted(app_dir.glob("*.slcp")):
            checked += 1
            errors = validate_slcp_against_slconf(slcp, slconf)
            if errors:
                failures += 1
                print(f"FAIL {slcp.relative_to(repo_root)}", file=sys.stderr)
                for err in errors:
                    print(f"  {err}", file=sys.stderr)
    if checked == 0:
        print("No apps with autogen/pkg.slconf found; run slt install first", file=sys.stderr)
        return 2
    if failures:
        print(f"{failures}/{checked} .slcp file(s) failed validation", file=sys.stderr)
        return 1
    print(f"OK: {checked} .slcp file(s) validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
