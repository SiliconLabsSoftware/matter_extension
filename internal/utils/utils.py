"""
Utility functions module.

This module contains common utility functions and validation helpers used across
the artifact upload system.

Author: Stefan Livadariu
Date: 2025-06-19
"""

import argparse
import sys
import os

# Add the workspace root to Python path to enable importing internal modules
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

# Import internal modules
from github.github_workflow import get_latest_sha, get_workflow_info, wait_for_artifacts
from artifacts.ubai_client import search_file_in_ubai
from artifacts.artifact_processor import download_and_upload_artifacts


def parse_arguments():
    """
    Parse and validate command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="Upload build artifacts for Matter project workflows")
    parser.add_argument("--branch_name", required=True, help="Name of the branch or PR (e.g., 'main', 'PR-123')")
    parser.add_argument("--sqa", required=True, choices=['true', 'false'], help="Boolean flag to indicate SQA builds")
    parser.add_argument("--commit_sha", required=True, help="Commit SHA to use (required for SQA)")
    parser.add_argument("--run_number", required=True, help="Workflow run number (required for SQA)")
    
    args = parser.parse_args()
    args.sqa = args.sqa.lower() == 'true'
    return args


def determine_workflow_info(args):
    """
    Determine workflow information based on build type (SQA vs DEV).
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        dict: Workflow information containing commit_sha, build_number, and workflow_id
    """
    if args.sqa:
        return _get_sqa_workflow_info(args)
    else:
        return _get_dev_workflow_info(args)


def _get_sqa_workflow_info(args):
    """
    Get workflow information for SQA builds.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        dict: Workflow information for SQA builds
        
    Raises:
        ValueError: If workflow data is invalid or wrong job type is triggered
        RuntimeError: If API request fails or no matching workflow is found
    """
    try:
        commit_sha = args.commit_sha
        build_number = args.run_number
        _, workflow_id = get_workflow_info(args.branch_name, commit_sha, sqa=True)
        
        return {
            'commit_sha': commit_sha,
            'build_number': build_number,
            'workflow_id': workflow_id,
            'branch_name': args.branch_name
        }
    except (ValueError, RuntimeError) as e:
        print(f"Failed to get SQA workflow info for branch '{args.branch_name}': {e}")
        sys.exit(1)


def _get_dev_workflow_info(args):
    """
    Get workflow information for regular (non-SQA) builds.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        dict: Workflow information for regular builds
        
    Raises:
        ValueError: If branch name format is invalid or workflow data is invalid
        RuntimeError: If GitHub API request fails or workflow info cannot be determined
    """
    try:
        commit_sha, pr_build_number = get_latest_sha(args.branch_name)
        
        if pr_build_number is None:
            run_number, workflow_id = get_workflow_info(args.branch_name, commit_sha)
            build_number = run_number
            branch_name = args.branch_name
        else:
            run_number, workflow_id = get_workflow_info(pr_build_number, commit_sha, pr=True)
            build_number = run_number
            branch_name = args.branch_name
        
        return {
            'commit_sha': commit_sha,
            'build_number': build_number,
            'workflow_id': workflow_id,
            'branch_name': branch_name
        }
    except (ValueError, RuntimeError) as e:
        print(f"Failed to get DEV workflow info for branch '{args.branch_name}': {e}")
        sys.exit(1)


def artifacts_already_uploaded(workflow_info, sqa):
    """
    Check if artifacts are already uploaded to UBAI.
    
    Args:
        workflow_info (dict): Workflow information containing branch_name and build_number
        sqa (bool): Whether this is an SQA build
        
    Returns:
        bool: True if artifacts are already uploaded, False otherwise
    """
    return search_file_in_ubai(workflow_info['branch_name'], workflow_info['build_number'], sqa) is not None


def process_artifacts(workflow_info, sqa):
    """
    Process artifacts by waiting for them to be ready, then downloading and uploading.
    
    Args:
        workflow_info (dict): Workflow information containing commit_sha, branch_name, build_number, and workflow_id
        sqa (bool): Whether this is an SQA build
    """
    print("Merged artifacts file not present in UBAI. Proceeding to download and upload artifacts.")
    wait_for_artifacts(workflow_info['commit_sha'], sqa)
    download_and_upload_artifacts(
        workflow_info['workflow_id'],
        workflow_info['branch_name'],
        workflow_info['build_number'],
        sqa
    ) 