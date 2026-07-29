#!/usr/bin/env python3

"""
@file generate_pkg_slt.py
@brief Generate pkg.slt files adjacent to SLC projects (.slcp / .slcw).

Sample app pkg.slt files declare a dependency on matter_app only. Stack and
platform dependencies are declared in the matter Conan recipe and resolved
transitively by SLT at install time (matter_app -> matter -> stack).

MATTER VERSION RESOLUTION
    SLC line version: matter.slce (X.Y.Z)
    Conan export ref: slc/script/matter_package_version or MATTER_PACKAGE_VERSION
    pkg.slt ranges: SLT syntax, e.g. >=2.10.0 <2.10.1 with prerelease=true

USAGE EXAMPLES
    python3 slc/script/generate_pkg_slt.py -d slc
    python3 slc/script/generate_pkg_slt.py --version-only
    python3 slc/script/generate_pkg_slt.py --line-version-only
"""

import argparse
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parents[1]
_SHARED_DIR = _REPO_ROOT / "packages" / "_shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from matter_version import (  # noqa: E402
    matter_slt_range,
    resolve_matter_conan_version,
    resolve_matter_line_version,
)


def build_pkg_slt_content(package_name: str, package_version: str) -> str:
    """Return pkg.slt content for a single Conan package dependency."""
    return f"""# Version defaults to "0" if not defined
version = "0"


[dependency]
# Get a specific version of the package
{package_name} = {{version = "{package_version}", installer = "conan", user="silabs", prerelease = true}}
"""


def resolve_matter_slt_range(repo_root: Path) -> str:
    return matter_slt_range(resolve_matter_line_version(repo_root))


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
        "--version-only", action="store_true",
        help="Print the Matter Conan export version and exit.",
    )
    parser.add_argument(
        "--line-version-only", action="store_true",
        help="Print the Matter SLC line version from matter.slce and exit.",
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

    repo_root = _REPO_ROOT

    if args.version_only:
        print(resolve_matter_conan_version(repo_root))
        sys.exit(0)

    if args.line_version_only:
        print(resolve_matter_line_version(repo_root))
        sys.exit(0)

    matter_range = resolve_matter_slt_range(repo_root)
    logger.info("Matter SLC line version: %s", resolve_matter_line_version(repo_root))
    logger.info("Matter SLT range for pkg.slt: %s", matter_range)

    exclude_patterns = []
    for entry in args.exclude:
        if entry:
            exclude_patterns.extend([p.strip() for p in entry.split(",") if p.strip()])
    if not exclude_patterns:
        exclude_patterns = ["third_party"]
        logger.info("No --exclude provided; defaulting to exclude: %s", exclude_patterns)

    generate_app_pkg_slt_files(args.directory, matter_range, exclude_patterns)

    if args.update_sample_app_pkg:
        write_pkg_slt("packages/matter_app/pkg.slt", "matter_app", matter_range)
    if args.update_stack_pkg:
        write_pkg_slt("packages/matter/pkg.slt", "matter", matter_range)


if __name__ == "__main__":
    main()
