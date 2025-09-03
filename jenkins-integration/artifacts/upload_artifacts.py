"""
This script automates the process of downloading, extracting, and uploading build artifacts for Matter project workflows.

It interacts with GitHub Actions, UBAI, and Artifactory to:
- Determine the latest commit SHA and workflow run for a given branch or PR.
- Wait for build artifacts to be available from GitHub Actions workflows.
- Download and extract artifacts from GitHub.
- Upload individual and merged artifacts to UBAI and Artifactory.
- Check if artifacts are already present in UBAI to avoid redundant uploads.

Usage:
    python upload_artifacts.py --branch_name <branch> --sqa <true|false> --commit_sha <sha> --run_number <number>

Arguments:
    --branch_name   Name of the branch or PR (e.g., 'main', 'PR-123').
    --sqa           Boolean flag to indicate SQA builds (true/false).
    --commit_sha    Commit SHA to use (required for SQA).
    --run_number    Workflow run number (required for SQA).

Environment Variables:
    SL_USERNAME     Username for authentication with Artifactory/UBAI.
    SL_PASSWORD     Password for authentication with Artifactory/UBAI.

Dependencies:
    - requests
    - config.py (must define required URLs and headers)
    - ubai_upload_cli, ubai_search_cli (must be available in PATH, need to use GSDK docker image )
"""

import os
import sys

# Add the workspace root to Python path to enable importing internal modules
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from jenkins-integration.utils import parse_arguments, determine_workflow_info, artifacts_already_uploaded, process_artifacts


# TODO: Will need to handle the -standard and -release binaries differently depending where they come from.
def main():
    """
    Main entry point for the artifact upload script.
    Orchestrates the artifact upload process by parsing arguments, determining workflow info,
    checking for existing artifacts, and coordinating the upload process.
    """
    args = parse_arguments()
    workflow_info = determine_workflow_info(args)
    if artifacts_already_uploaded(workflow_info, args.sqa):
        print("Merged artifacts file present in UBAI. Do not download and upload artifacts.")
        return
    process_artifacts(workflow_info, args.sqa)


if __name__ == '__main__':
    main()

