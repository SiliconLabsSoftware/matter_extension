"""
This script updates GitHub check runs with SQA test results for the Matter project workflows.

It interacts with GitHub Actions to:
- Retrieve the check run ID for a specific commit and job name ("Wait for Test Results").
- Update the check run with SQA test results and summary.
- Retry operations to handle delays in job startup or API propagation.

Usage:
    python send_results_to_github.py --commit_sha <sha> --sqa_result <PASS|FAIL> --sqa_summary <summary> --jenkins_url <url>

Arguments:
    --commit_sha    Commit SHA to update the check run for.
    --sqa_result    The overall result of the SQA tests (PASS/FAIL).
    --sqa_summary   The summary text of the SQA tests.
    --jenkins_url   The Jenkins build URL for this run.

Environment Variables:
    (None required directly; uses config.py for API URLs and headers.)

Dependencies:
    - requests
    - config.py (must define required URLs, repo info, and headers)

Author: Stefan Livadariu
Date: 2025-06-23
"""

import argparse
import sys
import time
import requests
import config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit_sha", required=True)
    parser.add_argument("--sqa_result", required=True)
    parser.add_argument("--sqa_summary", required=True)
    parser.add_argument("--jenkins_url", required=True)
    args = parser.parse_args()
    commit_sha = args.commit_sha
    sqa_result = args.sqa_result
    sqa_summary = args.sqa_summary
    jenkins_url = args.jenkins_url
    send_test_results_to_github(commit_sha, sqa_result, sqa_summary, jenkins_url)

def send_test_results_to_github(commit_sha, sqa_result, sqa_summary, jenkins_url):
    """
    Update the check run with the test results.
    Args:
        commit_sha (str): The commit SHA to update the check run for.
        sqa_result (str): The overall result of the SQA tests (PASS/FAIL).
        sqa_summary (str): The summary text of the SQA tests.
        jenkins_url (str): The Jenkins build URL for this run.
    Returns:
        None
    """
    check_run_id = get_check_run_id(commit_sha)
    if not check_run_id:
        print("Check run ID not found. Exiting.")
        return
    max_retries = 5
    delay = 300
    if sqa_result == "FAIL":
        conclusion = "failure"
    else:
        conclusion = "success"
    for attempt in range(max_retries):
        data = {
            "status:": "completed",
            "conclusion": conclusion,
            "output": {
                "title": "SQA Test Results",
                "summary": sqa_result,
                "text": f"{sqa_summary}\nSee test results here: {jenkins_url}",
            }
        }
        check_run_id_url = f"https://api.github.com/repos/{config.repo_owner}/{config.repo_name}/check-runs/{check_run_id}"
        print("PATCH Request Details:")
        print(f"URL: {check_run_id_url}")
        print(f"Headers: {config.github_headers}")
        print(f"Payload: {data}")
        response = requests.patch(check_run_id_url, headers=config.github_headers, json=data)
        if response.status_code == 200:
            print(f"Attempt {attempt + 1}/{max_retries}: Check run updated successfully.")
            break
        else:
            print(f"Attempt {attempt + 1}/{max_retries}: Failed to update check run. "
                  f"Status code: {response.status_code}, Response: {response.text}")
        if attempt < max_retries - 1:
            time.sleep(delay)
        if attempt == max_retries - 1:
            print(f"Attempt {attempt + 1}/{max_retries}: Check run update failed after maximum retries.")
            sys.exit(1)

def get_check_run_id(commit_sha):
    """
    Retrieve the check run ID for a specific job name, with retries to handle delays in job startup.
    Args:
        commit_sha (str): The commit SHA to fetch check runs for.
    Returns:
        int or None: The check run ID if found, otherwise None.
    """
    job_name = "Wait for Test Results"
    max_retries = 5
    delay = 300
    check_runs_url = f"{config.commits_url}/{commit_sha}/check-runs"
    print(f"Fetching check runs from: {check_runs_url}")
    for attempt in range(max_retries):
        check_runs_url = f"{config.commits_url}/{commit_sha}/check-runs"
        response = requests.get(check_runs_url, headers=config.github_headers)
        if response.status_code == 200:
            check_runs = response.json().get("check_runs", [])
            for check_run in check_runs:
                if check_run["name"] == job_name:
                    return check_run["id"]
            print(f"Attempt {attempt + 1}/{max_retries}: No matching check run found for job: {job_name}.")
        else:
            print(f"Attempt {attempt + 1}/{max_retries}: Failed to retrieve check runs. "
                  f"Status code: {response.status_code}, Response: {response.text}")
        if attempt < max_retries - 1:
            time.sleep(delay)
        if attempt == max_retries - 1:
            print(f"Exceeded maximum retries ({max_retries}). Check run ID not found.")
            sys.exit(1)
    return None


if __name__ == '__main__':
    main()
