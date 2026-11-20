#!/usr/bin/env python3

"""
@file generate_pkg_slt.py
@brief Generate pkg.slt files adjacent to SLC projects (.slcp / .slcw).

OVERVIEW
    Walk a base directory and, for every directory containing at least one
    .slcp or .slcw file, write a pkg.slt that depends only on matter_app.
    Existing files are overwritten.

MATTER VERSION RESOLUTION (priority)
    1. Explicit --matter-version CLI argument.
    2. slc/script/matter_package_version
    3. Version field from the matter.slce file in the extension root (auto-appended with "-0.dev").

RELEASE-STREAM
    packages/_shared/release_stream_channel (written as release-stream in every pkg.slt).

DEPENDENCIES
    Project pkg.slt files and packages/matter_app/pkg.slt depend only on matter_app.
    packages/matter/pkg.slt depends only on matter. Platform packages are
    requirements of the matter Conan recipe, not of these pkg.slt files.

VERSION-ONLY MODE
    Use --version-only to resolve and print just the Matter version without
    generating any pkg.slt files.

EXCLUDES
    Directories can be skipped using --exclude/-e. If none are provided,
    'third_party' is excluded by default.

USAGE EXAMPLES
    python3 slc/script/generate_pkg_slt.py -d slc
    python3 slc/script/generate_pkg_slt.py -d slc --matter-version 2.7.0-beta.1
    python3 slc/script/generate_pkg_slt.py -d slc -e build,temp,legacy
    python3 slc/script/generate_pkg_slt.py --version-only
    python3 slc/script/generate_pkg_slt.py --update-sample-app-pkg False

EXIT CODES
    0 on success; 1 if the Matter version cannot be resolved.
    Missing/empty release_stream_channel raises RuntimeError.
"""

import os
import sys
import argparse
import logging
from typing import Optional
import yaml

# Module-level logger (configured once in main)
logger = logging.getLogger(__name__)


def _repo_root_from_script() -> str:
    """slc/script/ -> repo root."""
    return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def resolve_release_stream_channel() -> str:
    """Read packages/_shared/release_stream_channel (pkg.slt release-stream)."""
    path = os.path.join(_repo_root_from_script(), "packages", "_shared", "release_stream_channel")
    with open(path, "r", encoding="utf-8") as f:
        value = f.read().strip()
    if not value:
        raise RuntimeError(f"release_stream_channel is empty: {path}")
    return value


def resolve_matter_version(cli_version: Optional[str]) -> str:
    """Determine the Matter package version to embed.

    Priority:
      1. --matter-version CLI argument if provided
      2. slc/script/matter_package_version
      3. Version field from matter.slce (+ "-0.dev")
    Exits with error if neither source provides a version.
    """
    if cli_version:
        logger.debug("Matter version provided via CLI: %s", cli_version)
        return cli_version

    script_dir = os.path.dirname(os.path.abspath(__file__))
    logger.debug("Script directory: %s", script_dir)

    version_file = os.path.join(script_dir, "matter_package_version")
    try:
        with open(version_file, "r", encoding="utf-8") as vf:
            version = vf.read().strip()
            if version:
                logger.debug("Matter version read from matter_package_version: %s", version)
                return version
            logger.warning("Version file %s is empty", version_file)
    except FileNotFoundError:
        logger.debug("matter_package_version file %s not found", version_file)
    except Exception as e:
        logger.warning("Failed to read matter_package_version file %s: %s", version_file, e)

    slce_file = os.path.join(_repo_root_from_script(), "matter.slce")
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
        "or ensure matter_package_version / matter.slce has a valid version."
    )
    sys.exit(1)

def generate_pkg_slt(verbose, pkg_slt_path, stack, matter_version, exclude_patterns):
    logger.info(f"Generating {pkg_slt_path} for Matter version: {matter_version}")
    release_stream = resolve_release_stream_channel()
    pkg_slt_content = f"""# Version defaults to "1" if not defined
version = "1"
release-stream = "{release_stream}"
 
 
[dependency]
# Get a specific version of the package
{stack} = {{ version = "{matter_version}", installer = "conan", user="silabs", channel="{release_stream}", prerelease = true }}
"""
    with open(pkg_slt_path, "w", encoding="utf-8") as pkg_slt_file:
        pkg_slt_file.write(pkg_slt_content)
    logger.debug(f"Generated {pkg_slt_path}")

def generate_pkg_slt_files(base_directory, verbose, matter_version, exclude_patterns):
    """Write a matter_app-only pkg.slt next to every project."""
    logger.info(f"Using Matter package version: {matter_version}")
    release_stream = resolve_release_stream_channel()
    pkg_slt_content = f"""# Version defaults to "1" if not defined
version = "1"
release-stream = "{release_stream}"
 
 
[dependency]
# Get a specific version of the package
matter_app = {{ version = "{matter_version}", installer = "conan", user="silabs", channel="{release_stream}", prerelease = true }}
"""

    for root, dirs, files in os.walk(base_directory):
        # Skip whole subtree if root matches an exclude pattern
        if any(patt and patt in root for patt in exclude_patterns):
            logger.debug(f"Skipping excluded directory tree: {root}")
            continue
        # Prune traversal: remove excluded dirs from in-place list
        if exclude_patterns:
            pruned = []
            for d in dirs:
                full = os.path.join(root, d)
                if any(patt and patt in full for patt in exclude_patterns):
                    logger.debug(f"Pruning excluded subdirectory: {full}")
                else:
                    pruned.append(d)
            dirs[:] = pruned
        # Require presence of at least one .slcp/.slcw
        if not any(file.endswith((".slcp", ".slcw")) for file in files):
            continue

        pkg_slt_path = os.path.join(root, "pkg.slt")
        try:
            with open(pkg_slt_path, "w", encoding="utf-8") as pkg_slt_file:
                pkg_slt_file.write(pkg_slt_content)
            logger.debug(f"Generated pkg.slt in: {pkg_slt_path}")
        except Exception as e:
            logger.error(f"Failed to generate pkg.slt in {pkg_slt_path}: {e}")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate pkg.slt files in directories containing .slcp files.")
    parser.add_argument("--directory", "-d", default=os.getcwd(),
                        help="Base directory to search for .slcp files. Defaults to current working directory.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--matter-version",
                        help="Explicit Matter package version to embed; overrides matter_package_version and matter.slce.")
    parser.add_argument("--version-only", action="store_true", help="Only resolve and print the Matter version, then exit.")
    parser.add_argument("--exclude", "-e", action="append", default=[],
                        help="Directory exclude pattern (substring match). Can be repeated or provide comma-separated values.")
    parser.add_argument("--update-sample-app-pkg", "-s", type=lambda x: x.lower() in ('true', '1', 'yes', 'on'), 
                        default=True, metavar="BOOL",
                        help="Update packages/matter_app/pkg.slt (default: True). Use 'False', 'True', '0', '1', 'yes', 'no', 'on', 'off'.")
    parser.add_argument("--update-stack-pkg", "-k", type=lambda x: x.lower() in ('true', '1', 'yes', 'on'), 
                        default=True, metavar="BOOL",
                        help="Update packages/matter/pkg.slt (default: True). Use 'False', 'True', '0', '1', 'yes', 'no', 'on', 'off'.")
    args = parser.parse_args()

    # Configure logging once here so all helper functions share configuration
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")
    logger.debug("Logging initialized (level=%s)", logging.getLevelName(log_level))
    matter_version = resolve_matter_version(args.matter_version)
    
    # If only version resolution is requested, print and exit
    if args.version_only:
        print(matter_version)
        sys.exit(0)  # Explicit success exit code
    
    # Flatten comma-separated patterns
    exclude_patterns = []
    for entry in args.exclude:
        if entry:
            exclude_patterns.extend([p.strip() for p in entry.split(',') if p.strip()])
    if not exclude_patterns:
        exclude_patterns = ["third_party"]
        logger.info("No --exclude provided; defaulting to exclude: %s", exclude_patterns)
    if exclude_patterns and args.verbose:
        logger.debug(f"Exclude patterns: {exclude_patterns}")
    generate_pkg_slt_files(args.directory, args.verbose, matter_version, exclude_patterns)
    if args.update_sample_app_pkg:
        generate_pkg_slt(args.verbose, 'packages/matter_app/pkg.slt', 'matter_app', matter_version, exclude_patterns)
    if args.update_stack_pkg:
        generate_pkg_slt(args.verbose, 'packages/matter/pkg.slt', 'matter', matter_version, exclude_patterns)

if __name__ == "__main__":
    main()