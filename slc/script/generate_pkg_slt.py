#!/usr/bin/env python3

"""
@file generate_pkg_slt.py
@brief Generate pkg.slt files adjacent to SLC projects (.slcp / .slcw).

Sample app pkg.slt files declare a dependency on matter_app only. Stack and
platform dependencies are declared in the matter Conan recipe and resolved
transitively by SLT at install time (matter_app -> matter -> stack).

MATTER VERSION RESOLUTION (priority)
    1. Explicit --matter-version CLI argument.
    2. Version field from the matter.slce file in the extension root (auto-appended with "-0.dev").

SAMPLE APP PACKAGE
    By default (--update-sample-app-pkg True), also generates 'packages/matter_app/pkg.slt'.
    By default (--update-stack-pkg True), also generates 'packages/matter/pkg.slt'.

VERSION-ONLY MODE
    Use --version-only to resolve and print just the Matter version without
    generating any pkg.slt files.

USAGE EXAMPLES
    python3 slc/script/generate_pkg_slt.py -d slc
    python3 slc/script/generate_pkg_slt.py -d slc --matter-version 2.7.0-beta.1
    python3 slc/script/generate_pkg_slt.py --version-only
"""

import argparse
import logging
import os
import sys
from typing import Optional

import yaml

logger = logging.getLogger(__name__)


def build_pkg_slt_content(package_name: str, package_version: str) -> str:
    """Return pkg.slt content for a single Conan package dependency."""
    return f"""# Version defaults to "0" if not defined
version = "0"


[dependency]
# Get a specific version of the package
{package_name} = {{ version = "{package_version}", installer ="conan", prerelease=true }}
"""


def resolve_matter_version(cli_version: Optional[str]) -> str:
    """Determine the Matter package version to embed."""
    if cli_version:
        logger.debug("Matter version provided via CLI: %s", cli_version)
        return cli_version

    script_dir = os.path.dirname(os.path.abspath(__file__))
    slce_file = os.path.join(script_dir, "..", "..", "matter.slce")
    try:
        with open(slce_file, "r", encoding="utf-8") as sf:
            slce_data = yaml.safe_load(sf)
            if slce_data and "version" in slce_data:
                version = str(slce_data["version"]).strip()
                if version:
                    version = version + "-0.dev"
                    logger.debug("Matter version read from matter.slce: %s", version)
                    return version
                logger.warning("Version field in %s is empty", slce_file)
    except FileNotFoundError:
        logger.debug("matter.slce file %s not found", slce_file)
    except Exception as e:
        logger.warning("Failed to parse matter.slce file %s: %s", slce_file, e)

    logger.error(
        "Unable to determine Matter package version: provide --matter-version "
        "or ensure matter.slce has a valid version field."
    )
    sys.exit(1)


def write_pkg_slt(pkg_slt_path: str, package_name: str, package_version: str) -> None:
    logger.info("Generating %s for %s version: %s", pkg_slt_path, package_name, package_version)
    content = build_pkg_slt_content(package_name, package_version)
    with open(pkg_slt_path, "w", encoding="utf-8") as pkg_slt_file:
        pkg_slt_file.write(content)
    logger.debug("Generated %s", pkg_slt_path)


def generate_app_pkg_slt_files(base_directory, matter_app_version, exclude_patterns):
    """Generate matter_app-only pkg.slt for every directory with .slcp/.slcw."""
    logger.info("Using matter_app package version: %s", matter_app_version)
    app_content = build_pkg_slt_content("matter_app", matter_app_version)

    for root, dirs, files in os.walk(base_directory):
        if any(patt and patt in root for patt in exclude_patterns):
            logger.debug("Skipping excluded directory tree: %s", root)
            continue
        if exclude_patterns:
            pruned = []
            for d in dirs:
                full = os.path.join(root, d)
                if any(patt and patt in full for patt in exclude_patterns):
                    logger.debug("Pruning excluded subdirectory: %s", full)
                else:
                    pruned.append(d)
            dirs[:] = pruned
        if not any(file.endswith((".slcp", ".slcw")) for file in files):
            continue

        pkg_slt_path = os.path.join(root, "pkg.slt")
        try:
            with open(pkg_slt_path, "w", encoding="utf-8") as pkg_slt_file:
                pkg_slt_file.write(app_content)
            logger.debug("Generated pkg.slt in: %s", pkg_slt_path)
        except Exception as e:
            logger.error("Failed to generate pkg.slt in %s: %s", pkg_slt_path, e)


def main():
    parser = argparse.ArgumentParser(
        description="Generate pkg.slt files in directories containing .slcp files."
    )
    parser.add_argument(
        "--directory", "-d", default=os.getcwd(),
        help="Base directory to search for .slcp files. Defaults to current working directory.",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument(
        "--matter-version",
        help="Explicit Matter/matter_app package version; overrides matter.slce file.",
    )
    parser.add_argument(
        "--version-only", action="store_true",
        help="Only resolve and print the Matter version, then exit.",
    )
    parser.add_argument(
        "--exclude", "-e", action="append", default=[],
        help="Directory exclude pattern (substring match). Repeatable or comma-separated.",
    )
    parser.add_argument(
        "--update-sample-app-pkg", "-s",
        type=lambda x: x.lower() in ("true", "1", "yes", "on"),
        default=True, metavar="BOOL",
        help="Update packages/matter_app/pkg.slt (default: True).",
    )
    parser.add_argument(
        "--update-stack-pkg", "-k",
        type=lambda x: x.lower() in ("true", "1", "yes", "on"),
        default=True, metavar="BOOL",
        help="Update packages/matter/pkg.slt (default: True).",
    )
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")

    matter_version = resolve_matter_version(args.matter_version)

    if args.version_only:
        print(matter_version)
        sys.exit(0)

    exclude_patterns = []
    for entry in args.exclude:
        if entry:
            exclude_patterns.extend([p.strip() for p in entry.split(",") if p.strip()])
    if not exclude_patterns:
        exclude_patterns = ["third_party"]
        logger.info("No --exclude provided; defaulting to exclude: %s", exclude_patterns)

    generate_app_pkg_slt_files(args.directory, matter_version, exclude_patterns)

    if args.update_sample_app_pkg:
        write_pkg_slt("packages/matter_app/pkg.slt", "matter_app", matter_version)
    if args.update_stack_pkg:
        write_pkg_slt("packages/matter/pkg.slt", "matter", matter_version)


if __name__ == "__main__":
    main()
