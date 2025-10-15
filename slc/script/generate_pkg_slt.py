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
        2. Contents of the local 'matter_package_version' file located next to
           this script.
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
    --matter-version    Override Matter version (else read matter_package_version)

OUTPUT
    - Creates / overwrites pkg.slt files and logs each generated path.
    - Directories can be excluded via --exclude/-e (repeatable / comma-separated).
"""

import os
import sys
import argparse
import logging
from typing import Dict, Optional, Any
import yaml

# Module-level logger (configured once in main)
logger = logging.getLogger(__name__)


def _load_grouped_versions(filename: str = "dependency_versions.yaml") -> Dict[str, Dict[str, str]]:
    """Load grouped dependency versions (common/thread/wifi) from YAML.

    Accepts either new grouped format or legacy flat mapping. Returns a dict:
        { "common": {...}, "thread": {...}, "wifi": {...} }
    Fallback provides minimal defaults if the file is missing or malformed.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, filename),
        os.path.join(script_dir, "..", "..", filename),
        os.path.join(os.getcwd(), filename),
    ]
    raw: Dict[str, Any] = {}
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                if isinstance(data, dict):
                    raw = data
                    logger.debug("Loaded dependency versions from %s", path)
                    break
            except Exception as e:
                logger.error("Failed parsing dependency versions file %s: %s", path, e)
                break
    grouped: Dict[str, Dict[str, str]]
    if raw and any(k in raw for k in ("thread", "wifi", "common")):
        grouped = {
            "common": raw.get("common", {}) or {},
            "thread": raw.get("thread", {}) or {},
            "wifi": raw.get("wifi", {}) or {},
        }
    elif raw:  # legacy flat mapping; no explicit groups provided
        # Instead of maintaining hardcoded dependency name lists, just put all
        # flat keys into both 'thread' and 'wifi' groups so additions require
        # no script changes. Keep 'common' empty (or could optionally lift
        # universally shared entries there later).
        flat_items = {k: v for k, v in raw.items() if k not in ("common", "thread", "wifi")}
        grouped = {
            "common": {},
            "thread": dict(flat_items),
            "wifi": dict(flat_items),
        }
    else:
        logger.warning("dependency_versions.yaml not found; using embedded fallback versions")
        grouped = {
            "common": {"bluetooth_le_host": "0.0.6"},
            "thread": {"openthread": "0.1.5", "rail_module": "0.0.5"},
            "wifi": {"platform_nwp_siwx91x": "0.0.3", "bluetooth_le_siwx91x": "0.0.3", "lwip": "0.0.5"},
        }
    return grouped


DEP_GROUPS = _load_grouped_versions()


def build_content_strings(matter_version: str):
    """Return header plus platform-specific dependency blocks using grouped versions.

    The returned tuple is (common_header, thread_block, wifi_block, all_header).
    For now 'common_header' and 'all_header' are identical (Matter only) to preserve
    previous behavior when --common is supplied.
    """
    header = f"""# Version defaults to "0" if not defined
version = "0"
 
 
[dependency]
# Get a specific version of the package
matter = {{ version = "{matter_version}", installer ="conan"}}
"""

    def merged_lines(group_name: str) -> str:
        # Merge common first, then group-specific (group overrides duplicates)
        common = DEP_GROUPS.get("common", {})
        specific = DEP_GROUPS.get(group_name, {})
        merged: Dict[str, str] = dict(common)
        # Maintain insertion order: add keys from specific (overwriting any duplicates)
        for k, v in specific.items():
            merged[k] = v
        # Simple emission: rely on merged dict insertion order (Python 3.7+ preserves it)
        #  - common entries first
        #  - followed by group-specific additions / overrides
        lines = []
        for name, ver in merged.items():
            if name == "matter":
                continue
            lines.append(f"{name} = {{ version = \"{ver}\", installer =\"conan\"}}\n")
        return "".join(lines)

    thread_block = merged_lines("thread")
    wifi_block = merged_lines("wifi")
    logger.debug("Resolved dependency groups: %s", DEP_GROUPS)
    logger.debug("Thread block emitted:\n%s", thread_block)
    logger.debug("WiFi block emitted:\n%s", wifi_block)
    return header, thread_block, wifi_block, header


def resolve_matter_version(cli_version: Optional[str]) -> str:
    """Determine the Matter package version to embed.

    Priority:
      1. --matter-version CLI argument if provided
      2. Contents of local file 'matter_package_version' located alongside this script
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
                logger.debug("Matter version read from file %s: %s", version_file, version)
                return version
            else:
                logger.warning("Version file %s is empty", version_file)
    except FileNotFoundError:
        logger.debug("Version file %s not found", version_file)

    logger.error("Unable to determine Matter package version: provide --matter-version or create '%s' with a version string.",
                 os.path.basename(version_file))
    sys.exit(1)

def generate_sample_app_pkg_slt(verbose, matter_version, exclude_patterns):
    logger.info(f"Generating sample_app_pkg.slt for Matter version: {matter_version}")
    pkg_slt_path = "sample_app_pkg.slt"
    pkg_slt_content = f"""# Version defaults to "0" if not defined
version = "0"
 
 
[dependency]
# Get a specific version of the package
matter_app = {{ version = "{matter_version}", installer ="conan"}}
"""
    with open(pkg_slt_path, "w", encoding="utf-8") as pkg_slt_file:
        pkg_slt_file.write(pkg_slt_content)
    logger.debug(f"Generated sample_app_pkg.slt in: {pkg_slt_path}")

def generate_pkg_slt_files(base_directory, verbose, common, matter_version, exclude_patterns):
    logger.info(f"Using Matter package version: {matter_version}")

    pkg_slt_content_common, pkg_slt_content_thread, pkg_slt_content_wifi, pkg_slt_content_all = build_content_strings(matter_version)

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
            if "siwx917" not in path_components:
                pkg_slt_content = pkg_slt_content_common + pkg_slt_content_thread
                # logger.debug("efr app contents = %s", pkg_slt_content_thread)
            else:
                pkg_slt_content = pkg_slt_content_common + pkg_slt_content_wifi
                # logger.debug("wifi app contents = %s", pkg_slt_content_wifi)

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
    parser.add_argument("--common", action="store_true",
                        help="Generate pkg.slt using only the universal pkg_slt_content_all for every project.")
    parser.add_argument("--matter-version", help="Explicit Matter package version to embed; overrides matter_package_version file.")
    parser.add_argument("--exclude", "-e", action="append", default=[],
                        help="Directory exclude pattern (substring match). Can be repeated or provide comma-separated values.")
    parser.add_argument("--update-sample-app-pkg","-s", default=True,
                        help="Update sample_app_pkg.slt")
    args = parser.parse_args()

    # Configure logging once here so all helper functions share configuration
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")
    logger.debug("Logging initialized (level=%s)", logging.getLevelName(log_level))
    matter_version = resolve_matter_version(args.matter_version)
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
    if args.update_sample_app_pkg:
        generate_sample_app_pkg_slt(args.verbose, matter_version, exclude_patterns)


if __name__ == "__main__":
    main()