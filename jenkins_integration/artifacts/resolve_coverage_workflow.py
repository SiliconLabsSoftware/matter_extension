"""
Resolve the GitHub Actions "Build Dev apps" run for a branch and wait until the
lcov coverage artifact is available.

Used by the coverage-only Jenkins test path (no app binaries / UBAI upload).

Prints the same markers as upload_artifacts so jenkinsFunctions.parse_upload_artifacts_output
can extract commit_sha / run_number / workflow_id:

    Workflow run number - <n>.
    Workflow ID - <id>. Commit SHA - <sha>

Usage:
    python resolve_coverage_workflow.py --branch_name <branch>

Environment:
    GITHUB_ACCESS_TOKEN
"""

import argparse
import fnmatch
import sys
import time
from urllib.parse import quote

import os

workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import jenkins_integration.config as config
from jenkins_integration.github.github_workflow import _make_github_api_request

WORKFLOW_NAME = "Build Dev apps"
COVERAGE_ARTIFACT_GLOB = "lcov-report-*-coverage"
# Coverage build is long; allow up to ~90 minutes.
MAX_RETRIES = 90
WAIT_INTERVAL_SEC = 60


def _parse_args():
    parser = argparse.ArgumentParser(description="Resolve Build Dev apps run and wait for coverage artifact")
    parser.add_argument("--branch_name", required=True, help="Git branch name (e.g. test/sonarqube-upload)")
    parser.add_argument("--max_retries", type=int, default=MAX_RETRIES)
    parser.add_argument("--wait_interval", type=int, default=WAIT_INTERVAL_SEC)
    return parser.parse_args()


def _list_branch_runs(branch_name):
    url = (
        f"{config.actions_runs_base_url}"
        f"?per_page=30&branch={quote(branch_name, safe='')}"
    )
    print(f"Listing workflow runs for branch '{branch_name}': {url}")
    response = _make_github_api_request(url)
    return response.json().get("workflow_runs") or []


def _find_build_dev_apps_run(branch_name):
    runs = [r for r in _list_branch_runs(branch_name) if r.get("name") == WORKFLOW_NAME]
    if not runs:
        raise RuntimeError(f"No '{WORKFLOW_NAME}' workflow runs found for branch: {branch_name}")

    in_progress = [r for r in runs if r.get("status") == "in_progress"]
    if in_progress:
        return in_progress[0]

    # Prefer newest successful completed run; otherwise newest completed.
    successful = [r for r in runs if r.get("status") == "completed" and r.get("conclusion") == "success"]
    if successful:
        return successful[0]

    completed = [r for r in runs if r.get("status") == "completed"]
    if completed:
        run = completed[0]
        print(
            f"[warn] Latest '{WORKFLOW_NAME}' run conclusion={run.get('conclusion')}; "
            "still waiting for coverage artifact if present."
        )
        return run

    return runs[0]


def _get_run(workflow_id):
    url = f"{config.actions_runs_base_url}/{workflow_id}"
    return _make_github_api_request(url).json()


def _find_coverage_artifact(workflow_id):
    url = f"{config.actions_runs_base_url}/{workflow_id}/artifacts?per_page=100"
    response = _make_github_api_request(url)
    artifacts = response.json().get("artifacts") or []
    for artifact in artifacts:
        if fnmatch.fnmatch(artifact.get("name", ""), COVERAGE_ARTIFACT_GLOB):
            return artifact
    return None


def _wait_for_coverage_artifact(workflow_id, max_retries, wait_interval):
    print(f"Waiting for coverage artifact matching '{COVERAGE_ARTIFACT_GLOB}' on workflow {workflow_id}")
    print(f"Max wait: {max_retries} x {wait_interval}s")

    for attempt in range(1, max_retries + 2):
        run = _get_run(workflow_id)
        status = run.get("status")
        conclusion = run.get("conclusion")
        print(f"Attempt {attempt}/{max_retries}: workflow status={status} conclusion={conclusion}")

        artifact = _find_coverage_artifact(workflow_id)
        if artifact:
            print(
                f"Coverage artifact ready: {artifact.get('name')} "
                f"(id={artifact.get('id')}, size={artifact.get('size_in_bytes')})"
            )
            return artifact

        if status == "completed" and conclusion not in (None, "success"):
            available = [
                a.get("name")
                for a in (_make_github_api_request(
                    f"{config.actions_runs_base_url}/{workflow_id}/artifacts?per_page=100"
                ).json().get("artifacts") or [])
            ]
            raise RuntimeError(
                f"Workflow {workflow_id} finished with conclusion '{conclusion}' "
                f"and no coverage artifact. Available: {available}"
            )

        if attempt > max_retries:
            raise TimeoutError(
                f"Coverage artifact not available after {max_retries} minutes "
                f"for workflow {workflow_id}"
            )

        print(f"Coverage artifact not ready. Sleeping {wait_interval}s...")
        time.sleep(wait_interval)


def main():
    args = _parse_args()
    run = _find_build_dev_apps_run(args.branch_name)

    run_number = run.get("run_number")
    workflow_id = run.get("id")
    commit_sha = run.get("head_sha")
    if not run_number or not workflow_id or not commit_sha:
        raise RuntimeError(f"Incomplete workflow run data: {run}")

    # Markers consumed by parse_upload_artifacts_output
    print(f"Workflow run number - {run_number}.\nWorkflow ID - {workflow_id}. Commit SHA - {commit_sha}")

    _wait_for_coverage_artifact(workflow_id, args.max_retries, args.wait_interval)
    print("Coverage workflow resolved successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
