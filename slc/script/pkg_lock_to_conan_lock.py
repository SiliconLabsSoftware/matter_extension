#!/usr/bin/env python3
"""Convert an SLT pkg.lock into a Conan 2 conan.lock (and optional conanfile.txt).

SLT pkg.lock (TOML-like) is not accepted by `conan install --lockfile`.
This script extracts installer=\"conan\" entries and emits Conan lock JSON.

Example:
  python3 slc/script/pkg_lock_to_conan_lock.py \\
    --input .github/pkg-manifest/pkg.lock \\
    --output .github/pkg-manifest/conan.lock \\
    --conanfile .github/pkg-manifest/conanfile.txt
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Tuple


_ENTRY_RE = re.compile(
    r'^\s*([A-Za-z0-9_.-]+)\s*=\s*\[\{([^}]*)\}\]',
    re.MULTILINE,
)
_FIELD_RE = re.compile(r'(\w+)\s*=\s*"([^"]*)"')


def parse_pkg_lock(text: str) -> List[Tuple[str, dict]]:
    """Return [(name, fields)] for dependency table entries."""
    # Limit to [dependency] section
    dep_match = re.search(r"^\[dependency\]\s*$", text, re.MULTILINE)
    if not dep_match:
        raise SystemExit("pkg.lock missing [dependency] section")
    start = dep_match.end()
    next_section = re.search(r"^\[", text[start:], re.MULTILINE)
    body = text[start : start + next_section.start()] if next_section else text[start:]

    entries: List[Tuple[str, dict]] = []
    for match in _ENTRY_RE.finditer(body):
        name = match.group(1)
        fields = dict(_FIELD_RE.findall(match.group(2)))
        entries.append((name, fields))
    return entries


def conan_ref(name: str, fields: dict) -> str:
    """Build a Conan reference string from pkg.lock fields."""
    ref = (fields.get("ref") or "").strip()
    if ref:
        # Drop Conan lock timestamp suffix if somehow present; keep recipe revision.
        return ref.split("%", 1)[0]
    version = (fields.get("version") or "").strip()
    if not version:
        raise SystemExit(f"{name}: missing both ref and version")
    return f"{name}/{version}@silabs"


# Silabs SDK recipes python_require; not present in SLT pkg.lock.
_DEFAULT_PYTHON_REQUIRES = [
    "silabs_package_assistant/1.8.0@silabs#1f4a525f99fdcc0d289cfd2fd532b6aefa7006c7",
]

# Package names that Silabs recipes often declare as tool/build_requires.
# When present in requires, also list them under build_requires (same pin).
_BUILD_REQUIRE_NAMES = frozenset(
    {
        "bluetooth_bgbuild",
        "cmake",
        "ninja",
        "gcc-arm-none-eabi",
        "llvm-arm-toolchain-for-embedded",
    }
)


def _ref_name(ref: str) -> str:
    return ref.split("/", 1)[0]


def build_conan_lock(
    requires: List[str],
    python_requires: List[str] | None = None,
) -> dict:
    # Sort reverse-alpha to roughly match common-team lock style; stable output.
    ordered = sorted(set(requires), reverse=True)
    pyreqs = list(python_requires if python_requires is not None else _DEFAULT_PYTHON_REQUIRES)
    build_requires = sorted(
        (r for r in ordered if _ref_name(r) in _BUILD_REQUIRE_NAMES),
        reverse=True,
    )
    return {
        "version": "0.5",
        "requires": ordered,
        "build_requires": build_requires,
        "python_requires": pyreqs,
        "config_requires": [],
    }


def build_conanfile(requires: List[str]) -> str:
    lines = ["[requires]"]
    # Exact pins matching the lock (name/version@user from each ref).
    for ref in sorted(set(requires)):
        # ref may include #revision; conanfile requires usually omit revision.
        req = ref.split("#", 1)[0]
        lines.append(req)
    lines.extend(["", "[generators]", "CMakeDeps", ""])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=Path(".github/pkg-manifest/pkg.lock"),
        help="SLT pkg.lock path",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path(".github/pkg-manifest/conan.lock"),
        help="Output Conan lock path",
    )
    parser.add_argument(
        "--conanfile",
        type=Path,
        default=None,
        help="Optional conanfile.txt to write (exact requires from pkg.lock)",
    )
    parser.add_argument(
        "--include-matter",
        action="store_true",
        help="Keep matter/matter_app in the Conan lock (default: omit; CI installs local Matter packages)",
    )
    parser.add_argument(
        "--python-requires",
        action="append",
        default=None,
        metavar="REF",
        help=(
            "Conan python_requires pin for the lock (repeatable). "
            "Default: silabs_package_assistant/1.8.0@silabs#..."
        ),
    )
    args = parser.parse_args()

    text = args.input.read_text(encoding="utf-8")
    entries = parse_pkg_lock(text)

    requires: List[str] = []
    skipped_archive = 0
    for name, fields in entries:
        installer = (fields.get("installer") or "").lower()
        if installer != "conan":
            skipped_archive += 1
            continue
        if not args.include_matter and name in {"matter", "matter_app"}:
            continue
        requires.append(conan_ref(name, fields))

    if not requires:
        raise SystemExit(f"No conan dependencies found in {args.input}")

    lock = build_conan_lock(requires, python_requires=args.python_requires)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(lock, indent=4) + "\n", encoding="utf-8")

    conanfile_path = args.conanfile
    if conanfile_path is None:
        # Default beside the lock when writing under pkg-manifest.
        conanfile_path = args.output.with_name("conanfile.txt")
    conanfile_path.write_text(build_conanfile(requires), encoding="utf-8")

    print(
        f"Wrote {args.output} ({len(lock['requires'])} requires; "
        f"{len(lock['build_requires'])} build_requires; "
        f"{len(lock['python_requires'])} python_requires; "
        f"skipped {skipped_archive} non-conan; omitted matter={not args.include_matter})",
        file=sys.stderr,
    )
    print(f"Wrote {conanfile_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
