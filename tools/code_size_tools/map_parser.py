#!/usr/bin/env python3
"""
Map Parser - Parse GNU ld (arm-none-eabi) .map files and extract flash usage.

Every input section whose load address lies in the FLASH memory region is
counted (.vectors, .text, .rodata, RAM functions, .data initializers, ...),
plus the NVM storage section and the bootloader area reserved below the
application. Categories are derived from the object path using the same rules
as the CSV parser, extended with path patterns matching the map file layout.
"""

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from csv_parser import CATEGORY_PATTERNS, FILENAME_CATEGORY_PATTERNS, get_category_from_filename

CategoryData = Dict[str, List[Tuple[str, int]]]
FunctionData = Dict[str, List[Tuple[str, int]]]

# Map-layout path patterns (substring match, first match wins).
# Checked after the file name rules and before the CSV path patterns.
MAP_PATH_PATTERNS: List[Tuple[str, str]] = [
    ("matter_sdk/src/app/clusters/", "Matter Data Model"),
    ("matter_sdk/src/app/icd/", "Matter ICD support"),
    ("matter_sdk/src/platform/silabs", "Matter Silabs Abstraction Impl"),
    ("matter_sdk/examples/platform/silabs/provision", "Silabs Matter Provisioning"),
    ("matter_sdk/examples/", "Matter Examples Code"),
    ("matter_sdk/", "Matter"),
    ("project/autogen/zap-generated/", "Matter Data Model"),
    ("project/", "Matter Examples Code"),
    ("/mbedtls/", "MBedTLS"),
    ("/freertos/", "FreeRTOS"),
    ("openthread", "OpenThread"),
    ("/thread/", "OpenThread"),
    ("bluetooth", "Bluetooth"),
    ("bgapi", "Bluetooth"),
    ("/nvm3/", "NVM"),
    ("platform_core/", "Platform"),
    ("rail_library/", "Platform"),
    ("/boards/", "Platform"),
    ("/bootloader/", "Platform"),
    ("/cmsis/", "Platform"),
    ("/segger/", "Platform"),
    ("common_15_4/", "Platform"),
]

_MEMORY_CONFIG_HEADER = "Memory Configuration"
_MEMORY_MAP_HEADER = "Linker script and memory map"
_NVM_OUTPUT_SECTION = ".nvm"
_BOOTLOADER_NAME = "bootloader"
_BOOTLOADER_CATEGORY = "Platform"

_REGION = re.compile(r"^(\S+)\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)(?:\s+(\S+))?\s*$")
# ".text  0xVMA  0xSIZE [load address 0xLMA]" or ".text" alone when the name is long
_OUTPUT_SECTION = re.compile(
    r"^([^\s*]\S*)(?:\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)(?:\s+load address 0x([0-9a-fA-F]+))?)?\s*$"
)
_OUTPUT_CONTINUATION = re.compile(
    r"^\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)(?:\s+load address 0x([0-9a-fA-F]+))?\s*$"
)
# " .text.foo  0xADDR  0xSIZE  path" or " .text.foo" alone when the name is long
_INPUT_SECTION = re.compile(r"^ ([^\s*]\S*)(?:\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)\s+(\S.*))?$")
_CONTINUATION = re.compile(r"^\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)\s+(\S.*)$")
_FILL = re.compile(r"^ \*fill\*\s+0x([0-9a-fA-F]+)\s+0x([0-9a-fA-F]+)")
_SYMBOL = re.compile(r"^\s+0x[0-9a-fA-F]+\s+(\S.*)$")


def _object_name(path: str) -> str:
    """Return the object file name (archive member if applicable)."""
    if path.endswith(")") and "(" in path:
        return path[path.rindex("(") + 1:-1]
    return path.rsplit("/", 1)[-1]


def get_map_category(path: str) -> str:
    """
    Determine the category of an object from its path in the map file.

    Args:
        path: Object path as written in the map file (may be `lib.a(member.o)`).

    Returns:
        Category name, or "Unclassified" if no rule matches.
    """
    if "lib/gcc" in path or "arm-none-eabi/lib" in path:
        return "C/C++ Standard Library"

    category = get_category_from_filename(_object_name(path))
    if category:
        return category

    for pattern, category in MAP_PATH_PATTERNS + CATEGORY_PATTERNS + FILENAME_CATEGORY_PATTERNS:
        if pattern in path:
            return category

    return "Unclassified"


def _display_names(paths: List[str]) -> Dict[str, str]:
    """Map each path to its shortest unique trailing path suffix."""
    components = {p: p.split("/") for p in paths}
    names: Dict[str, str] = {}
    depth = 1
    while len(names) < len(paths):
        counts = Counter("/".join(c[-depth:]) for c in components.values())
        for path, comps in components.items():
            if path in names:
                continue
            candidate = "/".join(comps[-depth:])
            if counts[candidate] == 1 or depth >= len(comps):
                names[path] = candidate
        depth += 1
    return names


def parse_map_file(map_file: Path) -> Tuple[CategoryData, FunctionData]:
    """
    Parse a GNU ld map file and extract flash usage per object.

    Args:
        map_file: Path to the .map file.

    Returns:
        Tuple of (category data, function data). Category data maps category
        names to (object_name, size) lists; function data maps object names
        to (symbol_name, size) lists sorted by size descending.

    Raises:
        FileNotFoundError: If the map file does not exist.
        ValueError: If the file is not a GNU ld map file.
    """
    if not map_file.is_file():
        raise FileNotFoundError(f"Map file not found: {map_file}")

    object_sizes: Dict[str, int] = defaultdict(int)
    object_functions: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    # (origin, length) of executable, non-writable regions (i.e. FLASH)
    flash_regions: List[Tuple[int, int]] = []

    stage = "preamble"
    pending_output: Optional[str] = None
    pending_section: Optional[str] = None
    in_flash_output = False
    # [section, address, size, path, first_symbol]
    current: Optional[list] = None
    # (address, listed_size, path or None for fill, label) of the current output section
    section_entries: List[Tuple[int, int, Optional[str], str]] = []

    def is_flash(address: int) -> bool:
        return any(origin <= address < origin + length for origin, length in flash_regions)

    def output_in_flash(name: str, vma: str, lma: Optional[str]) -> bool:
        return name == _NVM_OUTPUT_SECTION or is_flash(int(lma or vma, 16))

    def flush(entry: Optional[list]) -> None:
        if entry is None:
            return
        section, address, size, path, symbol = entry
        label = symbol or (section[len(".text."):] if section.startswith(".text.") else section)
        section_entries.append((address, size, path.replace("\\", "/"), label))

    def finalize_output_section() -> None:
        # Merged sections (e.g. .rodata.*.str1.1) are listed with their pre-merge size
        # at a shared address, so an entry may only own the bytes up to the next entry.
        for index, (address, size, path, label) in enumerate(section_entries):
            if index + 1 < len(section_entries):
                size = min(size, max(0, section_entries[index + 1][0] - address))
            if path is None or size == 0:
                continue
            object_sizes[path] += size
            object_functions[path][label] += size
        section_entries.clear()

    with open(map_file, "r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            line = raw_line.rstrip("\r\n")

            if stage != "map":
                if line.startswith(_MEMORY_CONFIG_HEADER):
                    stage = "memory"
                elif line.startswith(_MEMORY_MAP_HEADER):
                    stage = "map"
                elif stage == "memory":
                    match = _REGION.match(line)
                    if match:
                        attrs = match.group(4) or ""
                        if "x" in attrs and "w" not in attrs and "!" not in attrs:
                            flash_regions.append((int(match.group(2), 16), int(match.group(3), 16)))
                continue

            if pending_output is not None:
                match = _OUTPUT_CONTINUATION.match(line)
                in_flash_output = bool(match) and output_in_flash(
                    pending_output, match.group(1), match.group(3)
                )
                pending_output = None
                continue

            if pending_section is not None:
                match = _CONTINUATION.match(line)
                if match and in_flash_output:
                    current = [
                        pending_section, int(match.group(1), 16), int(match.group(2), 16),
                        match.group(3).strip(), None
                    ]
                pending_section = None
                continue

            if line and not line[0].isspace():
                flush(current)
                current = None
                finalize_output_section()
                match = _OUTPUT_SECTION.match(line)
                if not match:
                    in_flash_output = False
                elif match.group(2) is None:
                    pending_output = match.group(1)
                else:
                    in_flash_output = output_in_flash(match.group(1), match.group(2), match.group(4))
                continue

            match = _INPUT_SECTION.match(line)
            if match:
                flush(current)
                current = None
                if match.group(4) is None:
                    pending_section = match.group(1)
                elif in_flash_output:
                    current = [
                        match.group(1), int(match.group(2), 16), int(match.group(3), 16),
                        match.group(4).strip(), None
                    ]
                continue

            match = _FILL.match(line)
            if match:
                flush(current)
                current = None
                if in_flash_output:
                    section_entries.append((int(match.group(1), 16), int(match.group(2), 16), None, ""))
                continue

            if current is None:
                continue

            if not line.startswith(" ") or line.startswith(" *"):
                flush(current)
                current = None
                continue

            if current[4] is None:
                match = _SYMBOL.match(line)
                if match and "=" not in match.group(1) and not match.group(1).startswith(("PROVIDE", "(")):
                    current[4] = match.group(1).strip()

        flush(current)
        finalize_output_section()

    if stage != "map":
        raise ValueError(f"'{_MEMORY_MAP_HEADER}' not found; not a GNU ld map file: {map_file}")

    names = _display_names(list(object_sizes.keys()))
    category_data: CategoryData = {}
    function_data: FunctionData = {}
    for path, size in object_sizes.items():
        name = names[path]
        category_data.setdefault(get_map_category(path), []).append((name, size))
        function_data[name] = sorted(object_functions[path].items(), key=lambda x: x[1], reverse=True)

    # The application starts after the bootloader, at an offset from the 16 MB-aligned flash base.
    if flash_regions:
        bootloader_size = min(origin for origin, _ in flash_regions) & 0x00FFFFFF
        if bootloader_size:
            category_data.setdefault(_BOOTLOADER_CATEGORY, []).append((_BOOTLOADER_NAME, bootloader_size))

    return category_data, function_data
