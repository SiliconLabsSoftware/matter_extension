#!/usr/bin/env python3

"""
This script updates the setWakeRequirement function in sleep.c to use
either SL_POWER_MANAGER_EM2 or SL_POWER_MANAGER_EM1 based on the provided argument,
and updates LFRCO precision in board clock configs (brd4407a_brd4001a, brd4407a_brd4002a)
to match (EM2 -> cmuPrecisionHigh, EM1 -> cmuPrecisionDefault).

Target files (under SISDK_ROOT from slc/tools/.env):
- .../openthread/platform-abstraction/efr32/sleep.c
- .../boards/hardware/board/config/brd4407a_brd4001a/sl_clock_manager_oscillator_config.h
"""

import os
import sys
import re
import argparse
from pathlib import Path

# Allow importing stack_tooling when run as script from repo root or slc/script
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
from stack_tooling import require_sisdk_root

def update_sleep_c_file(file_path, target_mode):
    """
    Update the setWakeRequirement function to use the target power manager mode.
    
    Args:
        file_path: Path to the sleep.c file
        target_mode: Either 'EM1' or 'EM2' - the target power manager mode
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Determine source and target based on target_mode
    if target_mode == 'EM2':
        source_mode = 'EM1'
        pattern = r'(\s+\(\*em_operation\)\()SL_POWER_MANAGER_EM1(\);)'
        replacement = r'\1SL_POWER_MANAGER_EM2\2'
    else:  # target_mode == 'EM1'
        source_mode = 'EM2'
        pattern = r'(\s+\(\*em_operation\)\()SL_POWER_MANAGER_EM2(\);)'
        replacement = r'\1SL_POWER_MANAGER_EM1\2'
    
    new_content, count = re.subn(pattern, replacement, content)
    
    if count == 0:
        print(f"Warning: No replacement made in {file_path}")
        print(f"The pattern SL_POWER_MANAGER_{source_mode} was not found in the expected location.")
        return False
    
    if count > 1:
        print(f"Warning: Multiple replacements made ({count}). Review the file manually.")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully updated {file_path}: Replaced SL_POWER_MANAGER_{source_mode} with SL_POWER_MANAGER_{target_mode}")
    return True


def find_sleep_c_file(workspace_root, sisdk_root):
    """
    Search for sleep.c file under SISDK_ROOT.
    Looks for the file in openthread/platform-abstraction/efr32/sleep.c
    """
    simplicity_sdk_path = Path(sisdk_root)

    if not simplicity_sdk_path.exists():
        print(f"Error: SISDK_ROOT directory not found at {simplicity_sdk_path}")
        return None

    sleep_c_files = list(simplicity_sdk_path.rglob("sleep.c"))
    
    # Filter for the specific file we want (in openthread/platform-abstraction/efr32/)
    target_file = None
    for file_path in sleep_c_files:
        try:
            file_path.relative_to(simplicity_sdk_path)
        except ValueError:
            continue
        parts = file_path.parts
        if (
            "openthread" in parts
            and "platform-abstraction" in parts
            and "efr32" in parts
            and file_path.name == "sleep.c"
        ):
            target_file = file_path
            break
    
    if target_file is None:
        # If we didn't find the exact path, try to find any sleep.c that contains setWakeRequirement
        for file_path in sleep_c_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'setWakeRequirement' in content and ('SL_POWER_MANAGER_EM1' in content or 'SL_POWER_MANAGER_EM2' in content):
                        target_file = file_path
                        print(f"Found sleep.c with setWakeRequirement at: {file_path}")
                        break
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
                continue
    
    return target_file


# Board config dirs to update for LFRCO precision (relative to simplicity_sdk/boards/hardware/board/config/)
LFRCO_PRECISION_BOARD_CONFIGS = (
    "brd4407a_brd4001a",
    "brd4407a_brd4002a",
    "brd1019a_brd4001a",
    "brd1019a_brd4002a",
)


def find_clock_manager_oscillator_configs(sisdk_root):
    """
    Find sl_clock_manager_oscillator_config.h under board config dirs (brd4407a, brd1019a).
    """
    base = Path(sisdk_root) / "boards" / "hardware" / "board" / "config"
    if not base.exists():
        return []
    paths = []
    for name in LFRCO_PRECISION_BOARD_CONFIGS:
        p = base / name / "sl_clock_manager_oscillator_config.h"
        if p.exists():
            paths.append(p)
    return paths


def update_lfrco_precision(file_path, target_value):
    """
    Set SL_CLOCK_MANAGER_LFRCO_PRECISION to target_value (0 or 1).
    Replaces the numeric value in the #define (0 -> 1 or 1 -> 0).
    """
    if not file_path.exists():
        return False
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Match the #define line with numeric 0 or 1 and replace with target_value.
    # Use \g<1> and \g<2> so target_value (e.g. 1) is not parsed as part of a group ref.
    pattern = r"(#define\s+SL_CLOCK_MANAGER_LFRCO_PRECISION\s+)[01](\s*\n)"
    replacement = r"\g<1>" + str(target_value) + r"\g<2>"
    new_content, count = re.subn(pattern, replacement, content)
    if count == 0:
        return False
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description='Update sleep.c to use either SL_POWER_MANAGER_EM1 or SL_POWER_MANAGER_EM2',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n'
               '  %(prog)s EM2  # Replace EM1 with EM2\n'
               '  %(prog)s EM1  # Replace EM2 with EM1'
    )
    parser.add_argument(
        'mode',
        choices=['EM1', 'EM2'],
        help='Target power manager mode (EM1 or EM2)'
    )
    
    args = parser.parse_args()
    
    # Get the workspace root (assuming script is in slc/script/)
    script_dir = Path(__file__).parent
    workspace_root = script_dir.parent.parent
    try:
        sisdk_root = require_sisdk_root(workspace_root)
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)

    sleep_c_path = find_sleep_c_file(workspace_root, sisdk_root)

    if sleep_c_path is None:
        print("Error: sleep.c file not found under SISDK_ROOT")
        sys.exit(1)
    
    print(f"Found sleep.c file at: {sleep_c_path}")
    success = update_sleep_c_file(sleep_c_path, args.mode)
    if not success:
        sys.exit(1)

    # Update LFRCO precision in board clock configs: EM2 -> 1, EM1 -> 0
    target_value = 1 if args.mode == "EM2" else 0
    clock_configs = find_clock_manager_oscillator_configs(sisdk_root)
    for cfg_path in clock_configs:
        if update_lfrco_precision(cfg_path, target_value):
            print(f"Updated LFRCO precision to {target_value} in {cfg_path}")
        else:
            print(f"Error: No LFRCO precision replacement in {cfg_path}")
            sys.exit(1)


if __name__ == '__main__':
    main()
