#!/usr/bin/env python3
"""Check the Matter components against the deprecations declared by the SDKs.

All upgrade.slcu files found under the simplicity_sdk and wifi_sdk third party
folders are parsed to build two lists:
  - components that are replaced (the upgrade entry has 'remove' and 'add')
  - components that are only deleted (the entry has 'remove' and no 'add')

The components required by the *.slcc files of the extension are then matched
against those lists. The script exits with 1 if any match is found.
"""

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SDK_ROOTS = (
    REPO_ROOT / "third_party" / "simplicity_sdk",
    REPO_ROOT / "third_party" / "wifi_sdk",
)
COMPONENT_ROOT = REPO_ROOT / "slc" / "component"
UPGRADE_FILE_NAME = "upgrade.slcu"


def find_upgrade_files(roots):
    """Return the sorted list of upgrade.slcu files found under the roots."""
    files = []
    for root in roots:
        if not root.is_dir():
            print(f"warning: directory not found: {root}", file=sys.stderr)
            continue
        files.extend(sorted(root.rglob(UPGRADE_FILE_NAME)))
    return files


def _component_name(entry):
    """Components are either a plain name or a mapping holding an id."""
    if isinstance(entry, dict):
        return str(entry.get("id", entry))
    return str(entry)


def parse_upgrade_file(path):
    """Return (replaced, deleted) lists of tuples for a single upgrade file.

    replaced entries are (old_component, new_components, sdk_version).
    deleted entries are (old_component, sdk_version).
    """
    replaced = []
    deleted = []

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for block in data.get("upgrade") or []:
        if not isinstance(block, dict):
            continue
        sdk = block.get("sdk") or {}
        version = str(sdk.get("version", "unknown"))

        for component in block.get("component") or []:
            if not isinstance(component, dict) or not component.get("remove"):
                continue
            removed = [_component_name(c) for c in component["remove"]]
            added = [_component_name(c) for c in component.get("add") or []]
            for old in removed:
                if added:
                    replaced.append((old, ", ".join(added), version))
                else:
                    deleted.append((old, version))

    return replaced, deleted


def collect(paths):
    """Parse every file and return the de-duplicated replaced/deleted lists."""
    replaced = []
    deleted = []
    for path in paths:
        try:
            file_replaced, file_deleted = parse_upgrade_file(path)
        except yaml.YAMLError as error:
            print(f"warning: cannot parse {path}: {error}", file=sys.stderr)
            continue
        replaced.extend(file_replaced)
        deleted.extend(file_deleted)
    return _unique(replaced), _unique(deleted)


def _unique(entries):
    seen = set()
    result = []
    for entry in entries:
        if entry not in seen:
            seen.add(entry)
            result.append(entry)
    return result


def parse_requires(path):
    """Return the components listed under the 'requires' field of a slcc file."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    required = []
    for entry in data.get("requires") or []:
        name = entry.get("name", entry.get("id")) if isinstance(entry, dict) else entry
        if name is not None:
            required.append(str(name))
    return _unique(required)


def collect_requires(root):
    """Return a list of (slcc_path, required_component) for every slcc file."""
    required = []
    for path in sorted(root.rglob("*.slcc")):
        try:
            names = parse_requires(path)
        except yaml.YAMLError as error:
            print(f"warning: cannot parse {path}: {error}", file=sys.stderr)
            continue
        required.extend((path, name) for name in names)
    return required


def report_deprecated_requires(required, replaced, deleted):
    """Print every required component that is deprecated and count the hits.

    A replacement keeping the same component name is only a package relocation,
    so it is reported as a warning and not counted as a hit.
    """
    replacements = {}
    for old, new, version in replaced:
        replacements.setdefault(old, (new, version))

    deletions = {}
    for old, version in deleted:
        deletions.setdefault(old, version)

    hits = 0
    for path, name in required:
        relative = path.relative_to(REPO_ROOT)
        if name in replacements:
            new, version = replacements[name]
            prefix = "warning: " if new == name else ""
            print(
                f"{prefix}{name} from {relative} is deprecated since {version}"
                f"  replace with {new}"
            )
            hits += new != name
        elif name in deletions:
            print(
                f"{name} from {relative} is deleted since {deletions[name]}"
                "  removed it."
            )
            hits += 1
    return hits


def main(argv):
    roots = [Path(arg).resolve() for arg in argv[1:]] or list(SDK_ROOTS)
    paths = find_upgrade_files(roots)
    if not paths:
        print("error: no upgrade.slcu file found", file=sys.stderr)
        return 1

    replaced, deleted = collect(paths)

    print(
        f"Parsed {len(paths)} upgrade.slcu files: "
        f"{len(replaced)} replaced and {len(deleted)} deleted components"
    )

    if not COMPONENT_ROOT.is_dir():
        print(f"error: directory not found: {COMPONENT_ROOT}", file=sys.stderr)
        return 1

    required = collect_requires(COMPONENT_ROOT)
    print(f"\nChecking {len(required)} required components of {COMPONENT_ROOT}:")
    hits = report_deprecated_requires(required, replaced, deleted)
    if hits:
        print(f"\n{hits} deprecated or deleted components are still required")
        return 1

    print("no deprecated or deleted component required")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
