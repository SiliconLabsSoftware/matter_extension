"""
UBAI (Universal Binary Artifacts Index) client module.

This module handles all UBAI operations including:
- Uploading files to UBAI with metadata
- Searching for existing artifacts in UBAI
- Managing UBAI CLI interactions
"""

import subprocess
import os


def upload_to_ubai(file_path, app_name, target, branch_name, run_number, stack="matter", workflow_id=None):
    """
    Helper function to upload a file to UBAI.
    
    Args:
        file_path (str): Path to the file to upload.
        app_name (str): Application name metadata.
        target (str): Target metadata.
        branch_name (str): Branch name metadata.
        run_number (int): Build number metadata.
        stack (str): Stack metadata (default: 'matter').
        workflow_id (int, optional): GitHub workflow ID for formatting build number as workflow_id.run_number.
    """
    # Format build number as workflow_id.run_number if workflow_id is provided
    if workflow_id is not None:
        build_number = f"{workflow_id}.{run_number}"
    else:
        build_number = str(run_number)
    
    print(f"Uploading {file_path} to UBAI with build_number: {build_number}")
    try:
        subprocess.run([
            'ubai_upload_cli',
            '--client-id', 'jenkins-gsdk-pipelines-Matter',
            '--file-path', file_path,
            '--metadata', 'app_name', app_name,
            '--metadata', 'branch', branch_name,
            '--metadata', 'build_number', build_number,
            '--metadata', 'stack', stack,
            '--metadata', 'target', target,
            '--username', os.environ.get("SL_USERNAME"),
            '--password', os.environ.get("SL_PASSWORD")
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error uploading {file_path} to UBAI: {e}")


def search_file_in_ubai(branch_name, run_number, sqa, workflow_id=None):
    """
    Check if the final artifact is already uploaded to UBAI.
    
    Args:
        branch_name (str): Branch name to search for.
        run_number (int): Build number to search for.
        sqa (bool): Whether to search for SQA or dev artifacts.
        workflow_id (int, optional): GitHub workflow ID for formatting build number as workflow_id.run_number.
        
    Returns:
        list or None: List of found artifact lines, or None if not found or error.
    """
    # TODO: Will need to handle the -standard and -release binaries differently depending where they come from.
    if sqa:
        build_binaries = "sqa-app-standard"
    else:
        build_binaries = "dev-apps-standard"
    
    # Format build number as workflow_id.run_number if workflow_id is provided
    if workflow_id is not None:
        build_number = f"{workflow_id}.{run_number}"
    else:
        build_number = str(run_number)
    
    print(f"Searching for {build_binaries} in UBAI with build_number: {build_number}")
    
    try:
        result = subprocess.run([
            'ubai_search_cli',
            '--name', build_binaries,
            '--extension', '.zip',
            '--metadata', 'app_name', "matter",
            '--metadata', 'branch', branch_name,
            '--metadata', 'build_number', build_number,
            '--metadata', 'stack', "matter",
            '--metadata', 'target', "matter"
        ], check=True, capture_output=True, text=True)
        
        print(f"UBAI Search result: {result.stdout}")
        print(f"UBAI Search result: {result.stdout.strip().splitlines()}")
        return result.stdout.strip().splitlines()
        
    except subprocess.CalledProcessError as e:
        print(f"Error searching for {build_binaries} to UBAI: {e}")
        return None 