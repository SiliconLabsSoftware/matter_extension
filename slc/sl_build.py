#!/usr/bin/env python3

"""
 * @file sl_build.py
 * @brief Build a Matter application from a reference project file.
 *
 * This script generates and builds a Matter application using a reference .slcp or .slcw project file
 * and a Silicon Labs board name. It invokes SLC and Make to produce the application binaries.
 *
 * Usage:
 *   python3 sl_build.py <PathToReferenceProjectFile(.slcp or .slcw)> <SilabsBoard> [--verbose]
 *
 * Example:
 *   python3 sl_build.py path/to/sample.slcp brd4338a
 *

"""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

import shutil

from sl_create_new_app import CreateApp

def validate_tools():
    """Validate required build tools are available on system."""
    tools = [
        ("slc", "slc not detected on host. Please run slc/sl_setup_env.py to install slc."),
        ("arm-none-eabi-gcc", "arm-none-eabi-gcc not detected on host. Please run slc/sl_setup_env.py to install arm gcc toolchain.")
    ]
    
    for tool, error_msg in tools:
        if not shutil.which(tool):
            logging.error(error_msg)
            sys.exit(1)
    
    logging.info("Required tools found: slc, arm-none-eabi-gcc")


def parse_project_file(reference_project_file):
    """Parse project file and determine build parameters.
    
    Returns:
        tuple: (project_flag, silabs_app, output_dir, makefile_path)
    """
    if reference_project_file.endswith('.slcp'):
        project_flag = "-p"
        silabs_app = os.path.basename(reference_project_file)[:-5]
        output_dir = os.path.dirname(reference_project_file)
        makefile_path = f"{silabs_app}.Makefile"
    elif reference_project_file.endswith('.slcw'):
        project_flag = "-w"
        silabs_app = os.path.basename(reference_project_file)[:-5]
        output_dir = os.path.dirname(reference_project_file)
        makefile_path = f"{silabs_app}.solution.Makefile"
    else:
        logging.error("Project file must be a .slcp or .slcw file")
        logging.info("Example usage: python slc/sl_build.py <PathToReferenceProjectFile(.slcp or .slcw)> <SilabsBoard>")
        sys.exit(1)
    
    return project_flag, silabs_app, output_dir, makefile_path


def run_slc_generate(app, slc_path, output_dir, project_flag, reference_project_file, silabs_board):
    """Run SLC generate command to create project files.
    
    Args:
        app: createApp instance with environment settings
        slc_path: Path to slc executable
        output_dir: Output directory for generated files
        project_flag: "-p" for .slcp or "-w" for .slcw
        reference_project_file: Path to reference project file
        silabs_board: Silicon Labs board name
    """
    logging.info("Generating project files with SLC...")
    cmd = [slc_path, "generate"]
    cmd += ["-d", output_dir, project_flag, reference_project_file]
    cmd += ["--sdk-package-path", app.sisdk_root, "--sdk-package-path", app.wiseconnect_root, 
            "--sdk-package-path", app.silabs_chip_root]
    cmd += ["--with", silabs_board, "--generator-timeout=180", "-o", "makefile"]
    
    logging.info(f"Running command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        logging.info("SLC project generation completed successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"SLC project generation failed with exit code {e.returncode}")
        sys.exit(2)


def run_make_build(output_dir, makefile_path, jobs=None):
    """Run make build command.
    
    Args:
        output_dir: Directory containing the Makefile
        makefile_path: Name of the Makefile
        jobs: Number of parallel jobs (None for default)
    """
    logging.info("Building project with make...")
    cmd = ["make", "all", "-C", output_dir, "-f", makefile_path]
    
    if jobs:
        cmd.append(f"-j{jobs}")
    
    logging.info(f"Running command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        logging.info("Build completed successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"Make build failed with exit code {e.returncode}")
        sys.exit(2)


def main():
    """Main entry point for build script."""
    parser = argparse.ArgumentParser(description="Build a Matter application from a reference project file.")
    parser.add_argument("-p", "--reference_project_file", dest="reference_project_file", required=False, 
                        help="Path to the reference .slcp or .slcw project file")
    parser.add_argument("-b", "--silabs_board", dest="silabs_board", required=False, 
                        help="Silabs board name (e.g., brd4338a)")
    parser.add_argument("-j", "--jobs", dest="jobs", type=int, default=None,
                        help="Number of parallel make jobs (default: 13)")
    parser.add_argument("-v", "--verbose", action="store_true", 
                        help="Enable verbose (debug) logging")
    # Accept positional arguments for backward compatibility
    parser.add_argument("args", nargs="*", help=argparse.SUPPRESS)
    args = parser.parse_args()

    # Setup logging first
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='[%(levelname)s] %(message)s')

    # Validate and parse arguments
    if not args.reference_project_file or not args.silabs_board:
        if len(args.args) >= 2:
            args.reference_project_file = args.args[0]
            args.silabs_board = args.args[1]
        else:
            parser.error("reference_project_file and silabs_board are required.")

    reference_project_file = args.reference_project_file
    silabs_board = args.silabs_board.lower()
    jobs = args.jobs if args.jobs else 13

    # Validate reference project file exists
    if not os.path.exists(reference_project_file):
        logging.error(f"Reference project file does not exist: {reference_project_file}")
        sys.exit(1)

    # Initialize app instance for environment and board validation
    try:
        app = CreateApp()
    except SystemExit:
        logging.error("Failed to initialize application environment")
        sys.exit(1)

    # Validate board argument
    if not app.validate_board_argument(silabs_board):
        sys.exit(1)

    # Validate required tools are available
    validate_tools()

    # Parse project file configuration
    project_flag, silabs_app, output_dir, makefile_path = parse_project_file(reference_project_file)

    # Get SLC path from app
    slc_path = app.slc_path

    # Generate project files with SLC
    run_slc_generate(app, slc_path, output_dir, project_flag, reference_project_file, silabs_board)

    # Build project with make
    run_make_build(output_dir, makefile_path, jobs)

    logging.info("Build process completed successfully")

if __name__ == "__main__":
    main()