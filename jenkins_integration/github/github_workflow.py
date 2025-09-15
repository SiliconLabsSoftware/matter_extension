"""
GitHub workflow management module.

This module handles all GitHub API interactions including:
- Fetching workflow information
- Getting commit SHAs for branches and PRs
- Waiting for artifacts to be ready
- Managing workflow runs and check runs.
"""

import requests
import time
import os
import sys

# Add the workspace root to Python path to enable importing internal modules
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import jenkins_integration.config as config


def get_latest_sha(branch_name):
    """
    Get the latest commit SHA for a branch or PR.
    
    Args:
        branch_name (str): Branch name or PR identifier (e.g., 'main', 'PR-123').
        
    Returns:
        tuple: (commit_sha (str), pr_number (str or None), base_branch (str or None))
        
    Raises:
        ValueError: If the branch_name format is invalid
        RuntimeError: If the API request fails or no matching PR is found
    """
    if not branch_name:
        raise ValueError("Branch name cannot be empty")
    
    if branch_name.startswith("PR-"):
        return _get_pr_latest_sha(branch_name)
    else:
        return _get_branch_latest_sha(branch_name)


def _get_pr_latest_sha(pr_identifier):
    """
    Get the latest commit SHA for a pull request.
    
    Args:
        pr_identifier (str): PR identifier in format 'PR-123'
        
    Returns:
        tuple: (commit_sha (str), pr_number (str), head_branch (str))
        
    Raises:
        ValueError: If PR identifier format is invalid
        RuntimeError: If API request fails or PR not found
    """
    try:
        pr_number = pr_identifier.split('-')[1]
        if not pr_number.isdigit():
            raise ValueError(f"Invalid PR number in identifier: {pr_identifier}")
    except IndexError:
        raise ValueError(f"Invalid PR identifier format: {pr_identifier}. Expected format: PR-123")
    
    print(f"Fetching PR #{pr_number} information from GitHub API")
    response = _make_github_api_request(config.pr_sha_url)
    prs_data = response.json()
    commit_sha, head_ref = _find_pr_commit_sha(prs_data, pr_number)
    print(f"Found commit SHA for PR #{pr_number}: {commit_sha}")
    print(f"Head branch: {head_ref}")
    print(f"Commit SHA - {commit_sha}")
    print(f"PR Number: {pr_number}")
    return commit_sha, pr_number, head_ref


def _get_branch_latest_sha(branch_name):
    """
    Get the latest commit SHA for a branch.
    
    Args:
        branch_name (str): Branch name (e.g., 'main', 'develop')
        
    Returns:
        tuple: (commit_sha (str), None, None)
        
    Raises:
        RuntimeError: If API request fails
    """
    print(f"Fetching latest commit SHA for branch: {branch_name}")
    branch_url = config.sha_url + branch_name
    response = _make_github_api_request(branch_url)
    branch_data = response.json()
    
    if not branch_data:
        raise RuntimeError(f"No data returned for branch: {branch_name}")
    
    commit_sha = branch_data[0]['sha']
    print(f"Found commit SHA for branch {branch_name}: {commit_sha}")
    print(f"Commit SHA - {commit_sha}")
    return commit_sha, None, None


def get_workflow_info(branch_name, commit_sha, sqa=False, pr=False, head_branch=None):
    """
    Get the workflow run number and ID for a given branch and commit SHA.
    
    Args:
        branch_name (str): The branch name of the workflow or PR number if is a Pull Request.
        commit_sha (str): The commit SHA of the workflow.
        sqa (bool): Whether to get SQA workflow info (default: False).
        pr (bool): Whether this is a PR workflow (default: False).
        head_branch (str): The head branch for PR workflows (default: None).
        
    Returns:
        tuple: (run_number (int), workflow_id (int))
        
    Raises:
        RuntimeError: If the API request fails or no matching workflow is found
        ValueError: If the workflow data is invalid or wrong job type is triggered
    """
    if pr:
        if head_branch:
            pr_url = f"{config.actions_runs_url_pr}&branch={head_branch}"
        else:
            pr_url = config.actions_runs_url_pr
        print(f"Fetching workflow runs from actions/runs event Pull Request URL: {pr_url}")
        response = _make_github_api_request(pr_url)
        workflow_runs = response.json().get('workflow_runs', [])
        workflow_name = _get_workflow_name(sqa)
        return _find_pr_workflow(workflow_runs, branch_name, commit_sha, workflow_name)
    else:
        print(f"Fetching workflow runs from actions/runs URL: {config.actions_runs_url}")
        response = _make_github_api_request(config.actions_runs_url)
        workflow_runs = response.json().get('workflow_runs', [])
        workflow_name = _get_workflow_name(sqa)
        return _find_branch_workflow(workflow_runs, branch_name, commit_sha, workflow_name)


def wait_for_artifacts(commit_sha, sqa=False):
    """
    Wait for the required artifacts to be built and available in GitHub Actions.
    
    Args:
        commit_sha (str): The commit SHA to check for artifacts.
        sqa (bool): Whether to wait for SQA builds (default: False).
        
    Raises:
        ValueError: If commit_sha is invalid
        RuntimeError: If fetching check runs fails
        TimeoutError: If artifacts are not ready after max retries
    """
    if not commit_sha:
        raise ValueError("Commit SHA cannot be empty")
    
    config_data = _get_wait_config(sqa)
    print(f"Waiting for artifacts to be built for commit: {commit_sha}")
    print(f"Job to wait for: {config_data['job_name']}")
    print(f"Max wait time: {config_data['max_retries']} minutes")
    
    for attempt in range(1, config_data['max_retries'] + 4):
        try:
            if _check_artifacts_ready(commit_sha, config_data['job_name']):
                print(f"Artifacts are ready after {attempt} attempts!")
                return
        except RuntimeError as e:
            print(f"Error checking artifacts (attempt {attempt}): {e}")
        
        if attempt > config_data['max_retries']:
            raise TimeoutError(f"Building artifacts did not complete after {config_data['max_retries']} minutes. Exiting.")
        
        print(f"Attempt {attempt}/{config_data['max_retries']}: Artifacts not ready. Waiting {config_data['wait_interval']} seconds...")
        time.sleep(config_data['wait_interval'])


def _make_github_api_request(url):
    """
    Make a GitHub API request with proper error handling.
    
    Args:
        url (str): GitHub API URL to request
        
    Returns:
        requests.Response: Successful response object
        
    Raises:
        RuntimeError: If the API request fails
    """
    print(f"Making GitHub API request to: {url}")
    
    response = requests.get(url=url, headers=config.github_headers)
    
    if response.status_code != 200:
        error_msg = f"GitHub API request failed. Status: {response.status_code}, Response: {response.text}"
        print(error_msg)
        raise RuntimeError(error_msg)
    
    return response


def _find_pr_commit_sha(prs_data, pr_number):
    """
    Find the commit SHA and head branch for a specific PR number.
    
    Args:
        prs_data (list): List of PR data from GitHub API
        pr_number (str): PR number to search for
        
    Returns:
        tuple: (commit_sha (str), head_ref (str))
        
    Raises:
        RuntimeError: If PR is not found
    """
    for pr in prs_data:
        if str(pr['number']) == pr_number:
            return pr['head']['sha'], pr['head']['ref']
    
    raise RuntimeError(f"No matching PR found for number: {pr_number}")


def _get_workflow_name(sqa):
    """
    Get the workflow name based on build type.
    
    Args:
        sqa (bool): Whether this is an SQA build
        
    Returns:
        str: The workflow name to search for
    """
    return "Build SQA apps" if sqa else "Build Dev apps"


def _find_branch_workflow(workflow_runs, branch_name, commit_sha, workflow_name):
    """
    Find a branch workflow that matches the given criteria.
    
    Args:
        workflow_runs (list): List of workflow runs from GitHub API
        branch_name (str): Branch name to match
        commit_sha (str): Commit SHA to match
        workflow_name (str): Workflow name to match
        
    Returns:
        tuple: (run_number (int), workflow_id (int))
        
    Raises:
        ValueError: If wrong job type is triggered (PR found in branch workflow)
        RuntimeError: If no matching workflow is found or workflow data is invalid
    """
    for workflow in workflow_runs:
        if _matches_branch_workflow(workflow, branch_name, commit_sha, workflow_name):
            _validate_branch_workflow(workflow)
            return _extract_workflow_info(workflow)
    
    raise RuntimeError(f"No matching branch workflow found for branch: {branch_name} and commit SHA: {commit_sha}")


def _find_pr_workflow(workflow_runs, pr_number, commit_sha, workflow_name):
    """
    Find a PR workflow that matches the given criteria.
    
    Args:
        workflow_runs (list): List of workflow runs from GitHub API
        pr_number (str): PR number to match
        commit_sha (str): Commit SHA to match
        workflow_name (str): Workflow name to match
        
    Returns:
        tuple: (run_number (int), workflow_id (int))
        
    Raises:
        RuntimeError: If no matching workflow is found or workflow data is invalid
    """
    for workflow in workflow_runs:
        if _matches_pr_workflow(workflow, pr_number, commit_sha, workflow_name):
            return _extract_workflow_info(workflow)
    
    raise RuntimeError(f"No matching PR workflow found for PR: {pr_number} and commit SHA: {commit_sha}")


def _matches_branch_workflow(workflow, branch_name, commit_sha, workflow_name):
    """
    Check if a workflow matches branch workflow criteria.
    
    Args:
        workflow (dict): Workflow data from GitHub API
        branch_name (str): Branch name to match
        commit_sha (str): Commit SHA to match
        workflow_name (str): Workflow name to match
        
    Returns:
        bool: True if workflow matches criteria
    """
    return (workflow.get('head_branch') == branch_name and 
            workflow.get('head_sha') == commit_sha and 
            workflow.get('name') == workflow_name)


def _matches_pr_workflow(workflow, pr_number, commit_sha, workflow_name):
    """
    Check if a workflow matches PR workflow criteria.
    
    Args:
        workflow (dict): Workflow data from GitHub API
        pr_number (str): PR number to match
        commit_sha (str): Commit SHA to match
        workflow_name (str): Workflow name to match
        
    Returns:
        bool: True if workflow matches criteria
    """
    pull_requests = workflow.get('pull_requests', [])
    return (pull_requests and 
            pull_requests[0].get("number") == int(pr_number) and 
            workflow.get('head_sha') == commit_sha and 
            workflow.get('name') == workflow_name)


def _validate_branch_workflow(workflow):
    """
    Validate that a branch workflow doesn't have pull requests (wrong job type).
    
    Args:
        workflow (dict): Workflow data from GitHub API
        
    Raises:
        ValueError: If pull requests are found in a branch workflow
    """
    if workflow.get('pull_requests'):
        raise ValueError("Pull request found in workflow data. Wrong Jenkins job triggered. "
                        "The PR job matching your GitHub PR number should be triggered instead of the branch job.")


def _extract_workflow_info(workflow):
    """
    Extract run number and workflow ID from workflow data.
    
    Args:
        workflow (dict): Workflow data from GitHub API
        
    Returns:
        tuple: (run_number (int), workflow_id (int))
        
    Raises:
        RuntimeError: If required workflow data is missing
    """
    run_number = workflow.get('run_number')
    workflow_id = workflow.get('id')
    
    if not run_number or not workflow_id:
        raise RuntimeError("Run number or workflow ID is missing in the workflow data.")
    
    print(f"Workflow run number - {run_number}.\nWorkflow ID - {workflow_id}.")
    return run_number, workflow_id


def _get_wait_config(sqa):
    """
    Get configuration for artifact waiting based on build type.
    
    Args:
        sqa (bool): Whether this is an SQA build
        
    Returns:
        dict: Configuration containing job_name, max_retries, and wait_interval
    """
    return {
        'job_name': "Merge SQA App Artifacts" if sqa else "Merge App Artifacts",
        'max_retries': 60,
        'wait_interval': 60
    }


def _check_artifacts_ready(commit_sha, job_name):
    """
    Check if artifacts are ready by examining GitHub check runs.
    
    Args:
        commit_sha (str): The commit SHA to check
        job_name (str): The name of the job to wait for
        
    Returns:
        bool: True if artifacts are ready, False otherwise
        
    Raises:
        RuntimeError: If the API request fails
    """
    check_runs = _fetch_check_runs(commit_sha)
    for check_run in check_runs:
        if _is_test_timeout(check_run):
            _handle_test_timeout()
            continue
        if check_run.get('name') == job_name:
            return _is_artifact_job_complete(check_run)
    return False


def _fetch_check_runs(commit_sha):
    """
    Fetch check runs for a specific commit from GitHub API.
    
    Args:
        commit_sha (str): The commit SHA to fetch check runs for
        
    Returns:
        list: List of check run data from GitHub API
        
    Raises:
        RuntimeError: If the API request fails
    """
    check_runs_url = f"{config.commits_url}/{commit_sha}/check-runs"
    print(f"Fetching check-runs from URL: {check_runs_url}")
    response = _make_github_api_request(check_runs_url)
    return response.json().get('check_runs', [])


def _is_test_timeout(check_run):
    """
    Check if a check run indicates a test timeout.
    
    Args:
        check_run (dict): Check run data from GitHub API
        
    Returns:
        bool: True if this is a test timeout check run
    """
    return (check_run.get('name') == "Wait for Test Results" and 
            check_run.get('conclusion') == "timed_out")


def _handle_test_timeout():
    """
    Handle the case where test results have timed out.
    """
    print("Waiting for test results timed out for the latest workflow run. "
          "Jenkins job running on completed workflow. Bypass sending test results to GitHub.")


def _is_artifact_job_complete(check_run):
    """
    Check if the artifact job has completed successfully.
    
    Args:
        check_run (dict): Check run data from GitHub API
        
    Returns:
        bool: True if the job completed successfully
    """
    job_name = check_run.get('name')
    status = check_run.get('status')
    conclusion = check_run.get('conclusion')
    print(f"Check Run: {job_name}, STATUS: {status}, CONCLUSION: {conclusion}")
    if status == 'completed' and conclusion == "success":
        print(f"{job_name} finished successfully. Artifacts are built. "
              f"Workflow Id: {check_run['id']}")
        return True
    return False 