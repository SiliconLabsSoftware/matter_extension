#!/usr/bin/env python3
"""Strip SDK include/source/zap blocks from .slcp files (component owns them).

Keeps in-package include (path: include), provision config, and in-package
config_file entries (e.g. ThermostatConfig.h).

Usage (repo root):
  python3 slc/script/align_slcp_with_lighting.py
  python3 slc/script/align_slcp_with_lighting.py --dry-run
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_SDK_PATH = re.compile(r"third_party/matter_sdk")
_TOP_LEVEL_KEY = re.compile(r"^[a-z_][\w]*:")


def _repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def _is_list_item(line: str) -> bool:
    return line.startswith("  - ") or line.startswith("- ")


def _should_strip_config_block(block_text: str) -> bool:
    if not _SDK_PATH.search(block_text):
        return False
    if ".zap" not in block_text:
        return False
    if "zigbee-matter" in block_text or "zcl_config" in block_text:
        return False
    return True


def _strip_sdk_blocks(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    changes = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip("\n")

        if stripped.startswith("include:") or stripped.startswith("source:"):
            section = stripped.split(":", 1)[0]
            out.append(line)
            i += 1
            while i < len(lines):
                cur = lines[i]
                cur_stripped = cur.rstrip("\n")
                if _TOP_LEVEL_KEY.match(cur_stripped) and not cur_stripped.startswith(" "):
                    break
                if _is_list_item(cur_stripped):
                    block = [cur]
                    i += 1
                    while i < len(lines):
                        nxt = lines[i]
                        nxt_stripped = nxt.rstrip("\n")
                        if _is_list_item(nxt_stripped):
                            break
                        if _TOP_LEVEL_KEY.match(nxt_stripped) and not nxt_stripped.startswith(" "):
                            break
                        block.append(nxt)
                        i += 1
                    block_text = "".join(block)
                    if _SDK_PATH.search(block_text):
                        changes += 1
                        continue
                    out.extend(block)
                    continue
                out.append(cur)
                i += 1
            continue

        if stripped.startswith("config_file:"):
            out.append(line)
            i += 1
            while i < len(lines):
                cur = lines[i]
                cur_stripped = cur.rstrip("\n")
                if _TOP_LEVEL_KEY.match(cur_stripped) and not cur_stripped.startswith(" "):
                    break
                if _is_list_item(cur_stripped):
                    block = [cur]
                    i += 1
                    while i < len(lines):
                        nxt = lines[i]
                        nxt_stripped = nxt.rstrip("\n")
                        if _is_list_item(nxt_stripped):
                            break
                        if _TOP_LEVEL_KEY.match(nxt_stripped) and not nxt_stripped.startswith(" "):
                            break
                        block.append(nxt)
                        i += 1
                    block_text = "".join(block)
                    if _should_strip_config_block(block_text):
                        changes += 1
                        continue
                    out.extend(block)
                    continue
                out.append(cur)
                i += 1
            continue

        out.append(line)
        i += 1

    updated = "".join(out)
    updated = re.sub(
        r"(config_file:\n(?:  - .+\n)+)\n(?=include:)",
        r"\1\n# In-package path (synced from matter_sdk at matter_app package time).\n",
        updated,
    )
    if "# In-package path" not in updated:
        updated = updated.replace(
            "\ninclude:\n  - path: include\n",
            "\n# In-package path (synced from matter_sdk at matter_app package time).\n"
            "include:\n  - path: include\n",
        )
    if updated != text:
        changes = max(changes, 1)
    return updated, changes


def _remove_empty_sections(text: str) -> str:
    """Drop source: section when it has no list entries."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].rstrip("\n") == "source:":
            j = i + 1
            has_items = False
            while j < len(lines):
                s = lines[j].rstrip("\n")
                if _TOP_LEVEL_KEY.match(s) and not s.startswith(" "):
                    break
                if _is_list_item(s):
                    has_items = True
                    break
                j += 1
            if not has_items:
                i += 1
                while i < len(lines):
                    s = lines[i].rstrip("\n")
                    if _TOP_LEVEL_KEY.match(s) and not s.startswith(" "):
                        break
                    i += 1
                continue
        out.append(lines[i])
        i += 1
    return "".join(out)


def align_file(path: Path, dry_run: bool) -> int:
    original = path.read_text(encoding="utf-8")
    updated, changes = _strip_sdk_blocks(original)
    updated = _remove_empty_sections(updated)
    if changes and not dry_run and updated != original:
        path.write_text(updated, encoding="utf-8")
    return changes if updated != original else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=_repo_root_from_script())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    apps_root = repo_root / "slc" / "apps"
    total_files = 0
    total_changes = 0
    for slcp in sorted(apps_root.rglob("*.slcp")):
        if "bootloaders" in slcp.parts or "openthread_border_router" in slcp.parts:
            continue
        if "wake_on_matter" in slcp.parts:
            continue
        n = align_file(slcp, args.dry_run)
        if n:
            total_files += 1
            total_changes += n
            action = "would update" if args.dry_run else "updated"
            print(f"{action} {slcp.relative_to(repo_root)}")
    print(f"done: {total_changes} change(s) in {total_files} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
