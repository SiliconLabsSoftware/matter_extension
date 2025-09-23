#!/usr/bin/env python3

"""
This script scans a specified directory for `.slcc`, `.slcp`, and `.slce` files and verifies whether they contain 
specific strings (`package: matter` or `id: matter`). It excludes the `third_party` directory during the scan.

Usage:
    python3 verify_package_matter.py --directory <directory_to_scan> [--verbose]

Example:
    python3 verify_package_matter.py --directory /example/directory --verbose

Arguments:
    - --directory: The directory to scan for `.slcc`, `.slcp`, and `.slce` files.
    - --verbose: Enable detailed output.

Output:
    - Warnings for files missing the required strings are printed to the console.
    - A summary of validation results is logged with appropriate exit codes.

Example:
    If the user provides `/example/directory` as input, the script scans for `.slcc`, `.slcp`, and `.slce` files, 
    checks for the required strings, and logs the results. Files missing the required strings are listed in the console output.
"""

import os
import argparse
import logging
import sys

# Configure logging
logger = logging.getLogger(__name__)

def configure_logging(verbose):
    """
    Configure logging level based on the verbose flag.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

def find_files_with_extension(directory, extensions):
    """
    Recursively find all files with the given extensions in the specified directory,
    excluding the 'third_party' directory.
    """
    files = []
    for root, dirnames, filenames in os.walk(directory):
        # Exclude 'third_party' directory
        dirnames[:] = [d for d in dirnames if d != 'third_party']
        for filename in filenames:
            if filename.endswith(extensions):
                files.append(os.path.join(root, filename))
    return files

def verify_package_matter(file_path):
    """
    Verify if the file contains the string 'package: matter' or 'id: matter'.
    """
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if file_path.endswith('.slce'):
                    if 'id: matter' in line:
                        return True
                elif 'package: matter' in line:
                    return True
        return False
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return False

def main():
    """
    Main function to parse .slcc, .slcp, and .slce files and verify 'package: matter' or 'id: matter'.
    """
    parser = argparse.ArgumentParser(description="Scan .slcc, .slcp, and .slce files for 'package: matter' or 'id: matter'.")
    parser.add_argument("--directory", type=str, required=True, help="Directory to scan for .slcc, .slcp, and .slce files.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    # Configure logging
    configure_logging(args.verbose)

    directory = args.directory
    extensions = ('.slcc', '.slcp', '.slce')
    files = find_files_with_extension(directory, extensions)
    
    if not files:
        logger.info("No .slcc, .slcp, or .slce files found.")
        return 0

    missing_files = []

    for file_path in files:
        if not verify_package_matter(file_path):
            if file_path.endswith(".slce"):
                logger.warning(f"'id: matter' NOT found in: {file_path}")
            else:
                logger.warning(f"'package: matter' NOT found in: {file_path}")
            missing_files.append(file_path)

    # Print missing files and return appropriate exit code
    if missing_files:
        logger.error(f"Validation failed: {len(missing_files)} files without required 'package: matter' or 'id: matter' declarations found:")
        for file_path in missing_files:
            logger.error(f"  - {file_path}")
        return 1
    else:
        logger.info("Validation successful: All .slcc, .slcp, and .slce files contain the required strings.")
        return 0

if __name__ == "__main__":
    sys.exit(main())