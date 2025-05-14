#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import logging
from argparse import ArgumentParser
from sl_create_new_app import createApp

# Initialize logger
logger = logging.getLogger(__name__)

EXAMPLE_USAGE = "python slc/sl_build.py <PathToReferenceProjectFile(.slcp or .slcw)> <SilabsBoard> [--verbose] [--with <config>] [--without <config>]"

def main():
    parser = ArgumentParser(description="Build Silabs projects using slc.")
    parser.add_argument("reference_project_file", help="Path to the reference project file (.slcp or .slcw)")
    parser.add_argument("silabs_board", help="Silabs board name")
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose logging (DEBUG level)"
    )
    parser.add_argument(
        "--w", 
        help="Additional configuration to include in the build process"
    )
    parser.add_argument(
        "--without", 
        help="Configuration to exclude from the build process"
    )
    parser.add_argument(
    "--output_suffix",
    help="Optional suffix to append to the output directory name"
    )
    parser.add_argument(
        "--ci", 
        action="store_true", 
        help="Use for CI builds",
    )
    args = parser.parse_args()

    # Set logging level based on verbose flag
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    reference_project_file = args.reference_project_file
    silabs_board = args.silabs_board.lower()
    with_config = args.w
    without_config = args.without
    ci =  args.ci
    output_suffix = args.output_suffix
    App = createApp( ci)

    # Determine project flag and paths
    if reference_project_file.endswith('.slcp'):
        project_flag = "-p"
        silabs_app = os.path.basename(reference_project_file)[:-5]
        if  ci:
            output_dir = f"out/{silabs_board}/{silabs_app}-{output_suffix}"
        else:
            output_dir = os.path.dirname(reference_project_file)
        makefile_path = f"{silabs_app}.Makefile"
    elif reference_project_file.endswith('.slcw'):
        project_flag = "-w"
        silabs_app = os.path.basename(reference_project_file)[:-5]
        if  ci:
            output_dir = f"out/{silabs_board}/{silabs_app}-solution-{output_suffix}"
        else:
            output_dir = os.path.dirname(reference_project_file)
        makefile_path = f"{silabs_app}.solution.Makefile"
    else:
        logger.error("Argument reference_project_file needs to be a .slcp or .slcw file")
        logger.info("Example usage: %s", EXAMPLE_USAGE)
        sys.exit(1)

    # Check for required tools
    if not shutil.which("slc"):
        logger.error("slc not detected on host")
        logger.error("Please run slc/sl_setup_env.py to install slc.")
        sys.exit(1)

    if not shutil.which("arm-none-eabi-gcc"):
        logger.error("arm-none-eabi-gcc not detected on host")
        logger.error("Please run slc/sl_setup_env.py to install arm gcc toolchain")
        sys.exit(1)

    slc_path = App.slc_path
    java_path = App.java_path
    SoC_boards = App.SoC_boards
    with_config_args = ";wiseconnect3_sdk" if silabs_board in SoC_boards else ""

    # Add optional configurations
    if with_config:
        with_config_args += f",{with_config}"
    if without_config:
        without_config_args = f",{without_config}"

    # Trust extensions again if using ci
    if ci:
        App.slc_trust()

    # Run slc generate command
    try:      
        logger.info("Running slc generate command...")
        cmd = [slc_path]
        cmd.append("generate")
        cmd.append("-d")
        cmd.append(output_dir)
        cmd.append(project_flag)
        cmd.append(reference_project_file)
        cmd.append("--with")
        cmd.append(silabs_board+with_config_args)
        if without_config:
            cmd.append("--without")
            cmd.append(with_config_args)
        cmd.append("--generator-timeout=180") 
        cmd.append("-o")
        cmd.append("makefile")
        if not  ci:
            cmd.append("--java-location")
            cmd.append(java_path)
        logger.info(cmd)
        subprocess.run(cmd)
    except subprocess.CalledProcessError as e:
        logger.error("Error during slc generate command: %s", e)
        sys.exit(1)

    # Run make command
    try:
        logger.info("Running make command...")
        subprocess.run(["make", "all", "-C", output_dir, "-f", makefile_path, "-j13"])
    except subprocess.CalledProcessError as e:
        logger.error("Error during make command: %s", e)
        sys.exit(1)

    logger.info("Build completed successfully.")

if __name__ == "__main__":
    main()