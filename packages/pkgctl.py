#!/usr/bin/env python3
"""Export, remove, or list the Matter Conan packages in packages/packages.yaml.

``slc/build-pkg.sh``, the GitHub package action, and Jenkins call this so a
new package is one YAML entry plus its recipe, not a new copy of each loop.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

PACKAGES_DIR = Path(__file__).resolve().parent
MANIFEST = PACKAGES_DIR / "packages.yaml"
USER = "silabs"


def load_packages() -> list[dict]:
    data = yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}
    packages = data.get("packages") or []
    if not packages:
        raise SystemExit(f"{MANIFEST} has no packages")
    for entry in packages:
        if not entry.get("name") or not entry.get("recipe"):
            raise SystemExit(f"package entry needs name and recipe: {entry}")
    return packages


def cmd_names(_args: argparse.Namespace) -> None:
    for entry in load_packages():
        print(entry["name"])


def cmd_recipes(_args: argparse.Namespace) -> None:
    for entry in load_packages():
        print(f"{entry['name']}\t{entry['recipe']}")


def cmd_export(args: argparse.Namespace) -> None:
    env = os.environ.copy()
    env["MATTER_PACKAGE_VERSION"] = args.version
    env["MATTER_PACKAGE_CHANNEL"] = args.channel
    root = PACKAGES_DIR.parent
    for entry in load_packages():
        recipe = root / entry["recipe"]
        if not recipe.is_file():
            raise SystemExit(f"recipe not found: {recipe}")
        ref = f"{entry['name']}/{args.version}@{USER}/{args.channel}"
        print(f"Exporting {ref}")
        subprocess.run(
            [
                args.conan,
                "export-pkg",
                str(recipe),
                f"--name={entry['name']}",
                f"--version={args.version}",
                f"--user={USER}",
                f"--channel={args.channel}",
            ],
            check=True,
            env=env,
        )


def cmd_remove(args: argparse.Namespace) -> None:
    if bool(args.version) != bool(args.channel):
        raise SystemExit("remove: pass both --version and --channel, or neither")
    for entry in load_packages():
        if args.version and args.channel:
            pattern = f"{entry['name']}/{args.version}@{USER}/{args.channel}"
        else:
            pattern = f"{entry['name']}/*@{USER}/*"
        print(f"Removing {pattern}")
        subprocess.run([args.conan, "remove", pattern, "-c"], check=False)


def cmd_prune_cache(args: argparse.Namespace) -> None:
    """Drop cache recipes that are not in the manifest. Used after a local export."""
    keep = {entry["name"] for entry in load_packages()}
    proc = subprocess.run(
        [args.conan, "list", "*", "-c", "--format=json"],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout or "{}")
    cache = data.get("Local Cache", data)
    for reference in cache:
        if reference.split("/", 1)[0] not in keep:
            subprocess.run([args.conan, "remove", reference, "-c"], check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    conan_arg = argparse.ArgumentParser(add_help=False)
    conan_arg.add_argument("--conan", default="conan", help="Conan executable")

    sub.add_parser("names", help="Print package names, one per line").set_defaults(func=cmd_names)
    sub.add_parser("recipes", help="Print name<TAB>recipe-path").set_defaults(func=cmd_recipes)

    export = sub.add_parser("export", parents=[conan_arg], help="conan export-pkg each recipe")
    export.add_argument("--version", required=True)
    export.add_argument("--channel", required=True)
    export.set_defaults(func=cmd_export)

    remove = sub.add_parser(
        "remove", parents=[conan_arg], help="conan remove each package from the local cache"
    )
    remove.add_argument("--version", help="Limit removal to this version")
    remove.add_argument("--channel", help="Limit removal to this channel")
    remove.set_defaults(func=cmd_remove)
    sub.add_parser(
        "prune-cache", parents=[conan_arg], help="Remove cache recipes not listed in the manifest"
    ).set_defaults(func=cmd_prune_cache)

    args = parser.parse_args()
    try:
        args.func(args)
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)


if __name__ == "__main__":
    main()
