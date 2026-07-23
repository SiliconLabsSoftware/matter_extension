#!/usr/bin/env python3
"""Split matter_sdk paths from matter.slce.extra into packages/matter_sdk/matter_sdk.slce.extra."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def split_slce_extra(
    matter_extra: Path,
    matter_sdk_extra: Path,
    *,
    dry_run: bool = False,
) -> tuple[int, int]:
    lines = matter_extra.read_text(encoding="utf-8").splitlines(keepends=True)
    header: list[str] = []
    matter_sdk_lines: list[str] = []
    extension_lines: list[str] = []
    footer: list[str] = []

    phase = "header"
    for line in lines:
        stripped = line.strip()
        if phase == "header":
            if stripped == "# matter_sdk paths":
                phase = "matter_sdk"
                matter_sdk_lines.append("extra_files:\n")
                continue
            header.append(line)
            continue

        if phase == "matter_sdk":
            if stripped.startswith("- third_party/matter_sdk"):
                matter_sdk_lines.append(line)
                continue
            if stripped.startswith("git_extra_files:") or stripped.startswith("git_path_mapping:"):
                phase = "footer"
                footer.append(line)
                continue
            if stripped and not stripped.startswith("#"):
                extension_lines.append(line)
            continue

        footer.append(line)

    sdk_header = (
        "id: matter_sdk\n"
        "description: Matter SDK (Connected Home IP) stack sources for Silicon Labs\n"
    )
    sdk_content = sdk_header + "".join(matter_sdk_lines)
    if not sdk_content.endswith("\n"):
        sdk_content += "\n"

    new_matter = "".join(header + extension_lines + footer)
    if not new_matter.endswith("\n"):
        new_matter += "\n"

    if dry_run:
        print(f"Would move {len(matter_sdk_lines)} lines to {matter_sdk_extra}")
        print(f"Would leave {len(extension_lines)} extension lines in {matter_extra}")
        return len(matter_sdk_lines), len(extension_lines)

    matter_sdk_extra.parent.mkdir(parents=True, exist_ok=True)
    matter_sdk_extra.write_text(sdk_content, encoding="utf-8")
    matter_extra.write_text(new_matter, encoding="utf-8")
    print(f"Wrote {matter_sdk_extra} ({len(matter_sdk_lines)} paths)")
    print(f"Updated {matter_extra}")
    return len(matter_sdk_lines), len(extension_lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = repo_root()
    matter_extra = root / "packages" / "matter" / "matter.slce.extra"
    matter_sdk_extra = root / "packages" / "matter_sdk" / "matter_sdk.slce.extra"

    if not matter_extra.is_file():
        print(f"ERROR: {matter_extra} not found", file=sys.stderr)
        return 1

    split_slce_extra(matter_extra, matter_sdk_extra, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
