#!/usr/bin/env python3

"""
@file generate_pkg_slt.py
@brief Generate pkg.slt files adjacent to SLC projects (.slcp / .slcw) with
       pinned dependency versions (Matter + platform-specific extras).

OVERVIEW
    This tool walks a base directory (recursively) and, for every directory
    containing at least one .slcp or .slcw file, (re)writes a pkg.slt file.

VERSION RESOLUTION
    - The Matter package version is resolved in this priority order:
        1. Explicit --matter-version CLI argument.
        2. Version field from the matter.slce file in the extension root.
    - No hardcoded Matter version lives in the script logic.

DEPENDENCY VERSION SOURCE
    - All non-Matter dependency versions (openthread, wifi, lwip, etc.) are
      centrally defined once in the DEP_VERSIONS dictionary near the top of
      the file. Updating those constants automatically updates all generated
      pkg.slt files.

PLATFORM HEURISTICS (when --common is NOT used)
    - If the directory path does not contain 'siwx917'      -> append Thread / BLE host set.
    - If the directory path contains 'siwx917'              -> append Wi-Fi / 91x set.
    - Otherwise                                             -> only the Matter dependency.
    - The logic can be extended easily if new platform markers are needed.

--common MODE
    - When --common is supplied, every discovered project receives a uniform
      pkg.slt containing only the Matter dependency (using the shared template).

SAFETY / IDEMPOTENCE
    - Existing pkg.slt files are overwritten (by design) to ensure consistency.

USAGE EXAMPLES
    python3 generate_pkg_slt.py -d slc                      # heuristic mode
    python3 generate_pkg_slt.py -d slc --common             # uniform content
    python3 generate_pkg_slt.py -d slc --matter-version 2.7.0-beta.1
    python3 generate_pkg_slt.py --verbose

ARGUMENTS
    --directory, -d     Base directory to search (default: cwd)
    --verbose, -v       Verbose logging
    --common            Force universal content (ignore platform heuristics)
    --matter-version    Override Matter version (else read from matter.slce)

OUTPUT
    - Creates / overwrites pkg.slt files and logs each generated path.
    - Directories can be excluded via --exclude/-e (repeatable / comma-separated).
"""

import os
import sys
import argparse
import logging
from typing import Dict, Optional
import yaml

# Module-level logger (configured once in main)
logger = logging.getLogger(__name__)


def load_dep_versions(filename: str = "dependency_versions.yaml") -> Dict[str, str]:
    """Load dependency versions from shared YAML file at repo root.

    Falls back to embedded defaults if file is missing (so the script remains
    usable in isolation), but logs a warning encouraging creation of the file.
    """
    # Attempt to locate the file relative to this script first, then cwd.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, filename),  # same directory (slc/script)
        os.path.join(script_dir, "..", "..", filename),  # legacy repo root location
        os.path.join(os.getcwd(), filename),  # current working directory fallback
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    logger.debug("Loaded dependency versions from %s", path)
                    return data
            except Exception as e:
                logger.error("Failed parsing dependency versions file %s: %s", path, e)
                break
    # Fallback defaults (should mirror committed YAML); warn about fallback.
    logger.warning("dependency_versions.yaml not found; using embedded fallback versions")
    return {
        "openthread": "0.1.5",
        "bluetooth_le_host": "0.0.6",
        "rail_module": "0.0.5",
        "wifi": "0.0.7",
        "platform_nwp_siwx91x": "0.0.3",
        "bluetooth_le_siwx91x": "0.0.3",
        "lwip": "0.0.5",
    }


DEP_VERSIONS: Dict[str, str] = load_dep_versions()


def build_content_strings(matter_version: str):
    """Return content templates filled with the provided Matter version.

    Uses centralized DEP_VERSIONS so individual dependency version bumps
    only require changing the dictionary above.
    """
    # Common header (matter dependency only)
    pkg_slt_content_common = f"""# Version defaults to "0" if not defined
version = "0"
 
 
[dependency]
# Get a specific version of the package
matter = {{ version = "{matter_version}", installer ="conan"}}
"""

    # Thread / EFR variant dependencies
    pkg_slt_content_thread = """openthread = { version = "%s", installer ="conan"}
bluetooth_le_host = { version = "%s", installer ="conan"}
rail_module = { version = "%s", installer ="conan"}
""" % (
        DEP_VERSIONS["openthread"],
        DEP_VERSIONS["bluetooth_le_host"],
        DEP_VERSIONS["rail_module"],
    )

    # Wi-Fi / 91x variant dependencies
    pkg_slt_content_wifi = """wifi = { version = "%s", installer ="conan"}
platform_nwp_siwx91x = { version = "%s", installer ="conan"}
bluetooth_le_siwx91x = { version = "%s", installer ="conan"}
lwip = { version = "%s", installer ="conan"}
bluetooth_le_host = { version = "%s", installer ="conan"}
""" % (
        DEP_VERSIONS["wifi"],
        DEP_VERSIONS["platform_nwp_siwx91x"],
        DEP_VERSIONS["bluetooth_le_siwx91x"],
        DEP_VERSIONS["lwip"],
        DEP_VERSIONS["bluetooth_le_host"],
    )

    # Universal (common) variant (could differ later; currently same as common header)
    pkg_slt_content_all = f"""# Version defaults to "0" if not defined
version = "0"
 
 
[dependency]
# Get a specific version of the package
matter = {{ version = "{matter_version}", installer ="conan"}}
"""
    return (
        pkg_slt_content_common,
        pkg_slt_content_thread,
        pkg_slt_content_wifi,
        pkg_slt_content_all,
    )


def resolve_matter_version(cli_version: Optional[str]) -> str:
    """Determine the Matter package version to embed.

    Priority:
      1. --matter-version CLI argument if provided
      2. Version field from matter.slce file in the extension root
    Exits with error if no source provides a version.
    """
    if cli_version:
        logger.debug("Matter version provided via CLI: %s", cli_version)
        return cli_version

    script_dir = os.path.dirname(os.path.abspath(__file__))
    logger.debug("Script directory: %s", script_dir)

    # Try matter.slce file
    slce_file = os.path.join(script_dir, "..", "..", "matter.slce")
    try:
        with open(slce_file, "r", encoding="utf-8") as sf:
            slce_data = yaml.safe_load(sf)
            if slce_data and "version" in slce_data:
                version = str(slce_data["version"]).strip()
                if version:
                    version = version+"-0.dev"
                    logger.debug("Matter version read from matter.slce: %s", version)
                    return version
                else:
                    logger.warning("Version field in %s is empty", slce_file)
    except FileNotFoundError:
        logger.debug("matter.slce file %s not found", slce_file)
    except Exception as e:
        logger.warning("Failed to parse matter.slce file %s: %s", slce_file, e)

    logger.error("Unable to determine Matter package version: provide --matter-version or ensure matter.slce has a valid version field.")
    sys.exit(1)


def generate_pkg_slt_files(base_directory, verbose, common, matter_version, exclude_patterns):
    logger.info(f"Using Matter package version: {matter_version}")

    pkg_slt_content_common, pkg_slt_content_thread, pkg_slt_content_wifi, pkg_slt_content_all = build_content_strings(
        matter_version)

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

        if common:
            pkg_slt_content = pkg_slt_content_all
        else:
            path_components = os.path.normpath(root).split(os.path.sep)
            if "siwx917" in path_components:
                pkg_slt_content = pkg_slt_content_common + pkg_slt_content_wifi
            elif "efr" in path_components:
                pkg_slt_content = pkg_slt_content_common + pkg_slt_content_thread
            else:
                pkg_slt_content = pkg_slt_content_common

        pkg_slt_path = os.path.join(root, "pkg.slt")
        try:
            with open(pkg_slt_path, "w", encoding="utf-8") as pkg_slt_file:
                pkg_slt_file.write(pkg_slt_content)
            logger.info(f"Generated pkg.slt in: {pkg_slt_path}")
        except Exception as e:
            logger.error(f"Failed to generate pkg.slt in {pkg_slt_path}: {e}")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate pkg.slt files in directories containing .slcp files.")
    parser.add_argument("--directory", "-d", default=os.getcwd(),
                        help="Base directory to search for .slcp files. Defaults to current working directory.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--common", action="store_true",
                        help="Generate pkg.slt using only the universal pkg_slt_content_all for every project.")
    parser.add_argument("--matter-version", help="Explicit Matter package version to embed; overrides matter.slce file.")
    parser.add_argument("--version-only", action="store_true", help="Only resolve and print the Matter version, then exit.")
    parser.add_argument("--exclude", "-e", action="append", default=[],
                        help="Directory exclude pattern (substring match). Can be repeated or provide comma-separated values.")
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
    generate_pkg_slt_files(args.directory, args.verbose, args.common, matter_version, exclude_patterns)


if __name__ == "__main__":
    main()
