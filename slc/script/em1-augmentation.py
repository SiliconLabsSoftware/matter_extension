#!/usr/bin/env python3

"""
This script updates the setWakeRequirement function in sleep.c to use
SL_POWER_MANAGER_EM2 instead of SL_POWER_MANAGER_EM1 to make sure the device runs on EM1DIV16 mode.

The target file is:
third_party/simplicity_sdk/../openthread/platform-abstraction/efr32/sleep.c
"""

import os
import sys
import re
from pathlib import Path


def update_sleep_c_file(file_path):
    """
    Update the setWakeRequirement function to use SL_POWER_MANAGER_EM2
    instead of SL_POWER_MANAGER_EM1.
    
    Args:
        file_path: Path to the sleep.c file
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match the setWakeRequirement function and replace EM1 with EM2
    # We want to match: (*em_operation)(SL_POWER_MANAGER_EM1);
    # and replace with: (*em_operation)(SL_POWER_MANAGER_EM2);
    # This should only occur within the setWakeRequirement function
    
    # More specific pattern that matches the exact line in setWakeRequirement function
    pattern = r'(\s+\(\*em_operation\)\()SL_POWER_MANAGER_EM1(\);)'
    replacement = r'\1SL_POWER_MANAGER_EM2\2'
    
    new_content, count = re.subn(pattern, replacement, content)
    
    if count == 0:
        print(f"Warning: No replacement made in {file_path}")
        print("The pattern SL_POWER_MANAGER_EM1 was not found in the expected location.")
        return False
    
    if count > 1:
        print(f"Warning: Multiple replacements made ({count}). Review the file manually.")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully updated {file_path}: Replaced SL_POWER_MANAGER_EM1 with SL_POWER_MANAGER_EM2")
    return True


def find_sleep_c_file(workspace_root):
    """
    Search for sleep.c file under third_party/simplicity_sdk.
    Looks for the file in openthread/platform-abstraction/efr32/sleep.c
    
    Args:
        workspace_root: Root directory of the workspace
        
    Returns:
        Path to the sleep.c file, or None if not found
    """
    simplicity_sdk_path = workspace_root / "third_party" / "simplicity_sdk"
    
    if not simplicity_sdk_path.exists():
        print(f"Error: third_party/simplicity_sdk directory not found at {simplicity_sdk_path}")
        print("Make sure submodules are checked out.")
        return None
    
    # Search for sleep.c files under third_party/simplicity_sdk
    # We're looking for the one in openthread/platform-abstraction/efr32/
    sleep_c_files = list(simplicity_sdk_path.rglob("sleep.c"))
    
    # Filter for the specific file we want (in openthread/platform-abstraction/efr32/)
    target_file = None
    for file_path in sleep_c_files:
        # Check if this is the file we're looking for
        path_parts = file_path.parts
        try:
            # Find the index of 'simplicity_sdk' in the path
            sdk_index = path_parts.index('simplicity_sdk')
            # Check if the path contains the expected subdirectory structure
            relative_parts = path_parts[sdk_index + 1:]
            if (len(relative_parts) >= 4 and 
                'openthread' in relative_parts and
                'platform-abstraction' in relative_parts and
                'efr32' in relative_parts and
                file_path.name == 'sleep.c'):
                target_file = file_path
                break
        except ValueError:
            continue
    
    if target_file is None:
        # If we didn't find the exact path, try to find any sleep.c that contains setWakeRequirement
        for file_path in sleep_c_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'setWakeRequirement' in content and 'SL_POWER_MANAGER_EM1' in content:
                        target_file = file_path
                        print(f"Found sleep.c with setWakeRequirement at: {file_path}")
                        break
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
                continue
    
    return target_file


def main():
    """Main entry point for the script."""
    # Get the workspace root (assuming script is in slc/script/)
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent.parent
    
    # Search for the sleep.c file
    sleep_c_path = find_sleep_c_file(workspace_root)
    
    if sleep_c_path is None:
        print("Error: sleep.c file not found under third_party/simplicity_sdk")
        print("Make sure submodules are checked out.")
        sys.exit(1)
    
    print(f"Found sleep.c file at: {sleep_c_path}")
    success = update_sleep_c_file(sleep_c_path)
    
    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
