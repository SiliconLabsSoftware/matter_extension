#!/usr/bin/env python3
"""Migrate .slcp files to technology-direct sdk/sdk_extension headers."""

from __future__ import annotations

import re
import sys
from pathlib import Path

SDK_BLOCK = """sdk:
  id: simplicity_sdk
  version: "2026.6.0"
  vendor: silabs
"""

MATTER_EXT = """  - id: matter
    version: "2.9.0"
    vendor: silabs
"""

WIFI_SOC_EXTS = MATTER_EXT + """  - id: wifi
    version: "4.1.0"
    vendor: silabs
  - id: platform_siwx91x
    version: "4.1.0"
    vendor: silabs
  - id: bluetooth_le_siwx91x
    version: "4.1.0"
    vendor: silabs
"""

WIFI_NCP_EXTS = MATTER_EXT + """  - id: wifi
    version: "4.1.0"
    vendor: silabs
  - id: platform_siwx91x
    version: "4.1.0"
    vendor: silabs
  - id: platform_nwp_siwx91x
    version: "4.1.0"
    vendor: silabs
  - id: bluetooth_le_siwx91x
    version: "4.1.0"
    vendor: silabs
"""

THREAD_EXTS = MATTER_EXT + """  - id: openthread
    version: "3.1.0"
    vendor: silabs
  - id: openthread_stack
    version: "3.1.0"
    vendor: silabs
  - id: multiprotocol
    version: "1.1.0"
    vendor: silabs
"""

SECTION_START = re.compile(
    r"(?m)^(component:|provides:|requires:|config_file:|template_contribution:|readme:|ui_hints:|other_file:|post_build:)"
)
SDK_SECTION = re.compile(
    r"(?ms)^sdk:\n(?:  [^\n]+\n)+"
)
SDK_EXTENSION_SECTION = re.compile(
    r"(?ms)^sdk_extension:\n(?:  - id: [^\n]+\n    version: \"[^\"]+\"\n    vendor: silabs\n)+"
)


def _wifi_header(ncp: bool) -> str:
    exts = WIFI_NCP_EXTS if ncp else WIFI_SOC_EXTS
    return SDK_BLOCK + "sdk_extension:\n" + exts + "\n"


def _thread_header() -> str:
    return SDK_BLOCK + "sdk_extension:\n" + THREAD_EXTS + "\n"


def _strip_sdk_sections(text: str) -> str:
    text = SDK_EXTENSION_SECTION.sub("", text)
    text = SDK_SECTION.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def _insert_header(text: str, header: str) -> str:
    match = SECTION_START.search(text)
    if not match:
        return text.rstrip() + "\n\n" + header
    pos = match.start()
    prefix = text[:pos].rstrip() + "\n\n"
    suffix = text[pos:]
    return prefix + header + suffix


def migrate_slcp(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    posix = path.as_posix().lower()
    if "/wifi/" in posix:
        header = _wifi_header(ncp="ncp" in path.name.lower())
    elif "/thread/" in posix:
        header = _thread_header()
    else:
        return False

    stripped = _strip_sdk_sections(text)
    updated = _insert_header(stripped, header)
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    apps = repo / "slc" / "apps"
    changed = 0
    for slcp in sorted(apps.rglob("*.slcp")):
        if migrate_slcp(slcp):
            print(slcp.relative_to(repo))
            changed += 1
    print(f"Updated {changed} .slcp file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
