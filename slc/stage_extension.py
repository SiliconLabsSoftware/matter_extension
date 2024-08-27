"""
This script copies a trimmed-down version of the repository to a specified target location, making it compatible for use with Simplicity Studio.
It also initializes and updates Git submodules before performing the copy operation.

Usage:
    python3 slc/copy_extension.py <target_location>

Example:
    python3 slc/copy_extension.py /path/to/target

Arguments:
    target_location: The destination directory where the extension will be copied.
"""

import os
import shutil
import subprocess
import argparse

exclude_directory = ['simplicity_sdk', 'wifi_sdk', "out"]

def run_submodule_commands():
    """Run the git submodule sync and init commands."""
    try:
        subprocess.run(['git', 'submodule', 'sync'], check=True)
        print("Submodule sync completed successfully.")

        subprocess.run(["git", "submodule", "update", "--init"], check=True)
        print("Submodule init completed successfully.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running submodule commands: {e}")

def copy_directory(source_directory, target_location):
    """Copy the source directory to the target location, excluding specified directories, hidden files, and Git files."""
    try:
        for root, dirs, files in os.walk(source_directory):
            # Exclude specified directories
            dirs[:] = [d for d in dirs if d not in exclude_directory and not d.startswith('.')]
            
            for file in files:
                # Skip hidden files and Git files
                if file.startswith('.'):
                    continue
                
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_location, "matter_extension", os.path.relpath(source_file, source_directory))
                target_directory = os.path.dirname(target_file)
                os.makedirs(target_directory, exist_ok=True)
                try:
                    shutil.copy2(source_file, target_file)
                except Exception as e:
                    print(f"An error occurred while copying {source_file}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Copy directory to target location.")
    parser.add_argument('target_location', type=str, help='The target location to copy the directory to.')
    args = parser.parse_args()
    
    target_location = args.target_location
    
    # Define the source directory and the directory to exclude
    source_directory = os.getcwd()
    
    # Run the submodule init and sync --recursive commands
    run_submodule_commands()
    
    # Copy the root directory to the target location, excluding the specified directory
    copy_directory(source_directory, target_location)
    print(f"Copied files to {target_location}/matter_extension.")

if __name__ == "__main__":
    main()