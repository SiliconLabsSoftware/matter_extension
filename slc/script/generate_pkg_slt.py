#!/usr/bin/env python3

"""
@file generate_pkg_slt.py
@brief Generate pkg.slt files next to SLC projects that contain .slcp files.

@details
    - Recursively walks a base directory provided via --directory/-d.
    - For each directory that contains at least one .slcp file, writes a pkg.slt
        file with default content that pins the Matter stack dependency to
        version "2.6.1" using the Conan installer.
    - Existing pkg.slt files at the same path will be overwritten.

@usage
    python3 generate_pkg_slt.py [--directory <BASE_PATH>] [--verbose]

@args
    --directory, -d  Optional. Base directory to search for .slcp files.
                     Defaults to current working directory.
    --verbose, -v    Optional. Enable verbose logging output.

@output
    - Creates pkg.slt files alongside .slcp projects and logs progress to stdout.
"""

import os
import sys
import argparse
import logging

def build_content_strings(matter_version: str):
    """Return content templates filled with the provided Matter version."""
    pkg_slt_content_common = f"""# Version defaults to "0" if not defined
version = "0"
 
 
[dependency]
# Get a specific version of the package
matter = {{ version = "{matter_version}", installer ="conan"}}
"""

    pkg_slt_content_thread = """openthread = { version = "0.1.5", installer ="conan"}
bluetooth_le_host = { version = "0.0.6", installer ="conan"}
rail_module = { version = "0.0.5", installer ="conan"}
"""

    pkg_slt_content_wifi = """wifi = { version = "0.0.7", installer ="conan"}
platform_nwp_siwx91x = { version = "0.0.3", installer ="conan"}
bluetooth_le_siwx91x = { version = "0.0.3", installer ="conan"}
lwip = { version = "0.0.5", installer ="conan"}
bluetooth_le_host = { version = "0.0.6", installer ="conan"}
"""

    pkg_slt_content_all = f"""# Version defaults to "0" if not defined
version = "0"
 
 
[dependency]
# Get a specific version of the package
matter = {{ version = "{matter_version}", installer ="conan"}}
"""
    return pkg_slt_content_common, pkg_slt_content_thread, pkg_slt_content_wifi, pkg_slt_content_all

def resolve_matter_version(cli_version: str | None) -> str:
    """Determine the Matter package version to embed.

    Priority:
      1. --matter-version CLI argument if provided
      2. Contents of local file 'matter_package_version' located alongside this script
    """
    if cli_version:
        return cli_version
    script_dir = os.path.dirname(os.path.abspath(__file__))
    version_file = os.path.join(script_dir, "matter_package_version")  # note intentional existing filename
    try:
        with open(version_file, "r", encoding="utf-8") as vf:
            version = vf.read().strip()
            if version:
                return version
    except FileNotFoundError:
        # Nothing found: log error and exit
        logging.error("Unable to determine Matter package version: provide --matter-version or create 'matter_pacakge_version' file with a version string.")
        sys.exit(1)


def generate_pkg_slt_files(base_directory, verbose, common, matter_version):
    # Configure logging
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO, format="%(message)s")
    logger = logging.getLogger()
    logger.info(f"Using Matter package version: {matter_version}")

    pkg_slt_content_common, pkg_slt_content_thread, pkg_slt_content_wifi, pkg_slt_content_all = build_content_strings(matter_version)

    for root, dirs, files in os.walk(base_directory):
    # Check if a .slcp or .slcw file exists in the current directory
        if any(file.endswith((".slcp", ".slcw")) for file in files):
            if common:
                # Force use of the 'all' content only
                pkg_slt_content = pkg_slt_content_all
            else:
                # Determine content based on path heuristics
                if "efr" in root:
                    pkg_slt_content = pkg_slt_content_common + pkg_slt_content_thread
                elif "siwx917" in root:
                    pkg_slt_content = pkg_slt_content_common + pkg_slt_content_wifi
                else:
                    # Default to common content if no specific platform substring matches
                    pkg_slt_content = pkg_slt_content_common
            pkg_slt_path = os.path.join(root, "pkg.slt")
            try:
                # Write the pkg.slt file
                with open(pkg_slt_path, "w") as pkg_slt_file:
                    pkg_slt_file.write(pkg_slt_content)
                logger.info(f"Generated pkg.slt in: {pkg_slt_path}")
            except Exception as e:
                logger.error(f"Failed to generate pkg.slt in {pkg_slt_path}: {e}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate pkg.slt files in directories containing .slcp files.")
    parser.add_argument("--directory", "-d", default=os.getcwd(), help="Base directory to search for .slcp files. Defaults to current working directory.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--common", action="store_true", help="Generate pkg.slt using only the universal pkg_slt_content_all for every project.")
    parser.add_argument("--matter-version", help="Explicit Matter package version to embed; overrides matter_pacakge_version file.")
    args = parser.parse_args()

    # Configure logging early so resolve_matter_version can report errors
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s")
    matter_version = resolve_matter_version(args.matter_version)
    generate_pkg_slt_files(args.directory, args.verbose, args.common, matter_version)

if __name__ == "__main__":
    main()