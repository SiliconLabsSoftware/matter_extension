"""
Resolve the GitHub Actions 'Build Dev apps' run for the current Jenkins commit,
wait for the LCOV coverage artifact, and print workflow metadata for Groovy.

Output lines match parse_upload_artifacts_output expectations:
  Workflow run number - <n>
  Workflow ID - <id>
  Commit SHA - <sha>
  PR Number: <n>   (optional)
  SKIP_DEV_MERGE_WAIT=1   (when the run has no dev-artifacts-*, e.g. build-type test)

Usage:
    python resolve_workflow_for_coverage.py --branch_name <branch> --commit_sha <40-char-sha>

Environment:
    GITHUB_ACCESS_TOKEN
"""

import argparse
import os
import sys

workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from jenkins_integration.github.github_workflow import (
    find_build_dev_apps_run_for_commit,
    github_run_has_dev_artifacts,
    wait_for_lcov_coverage_artifact,
)


def main():
    parser = argparse.ArgumentParser(description="Resolve Build Dev apps run and wait for LCOV artifact")
    parser.add_argument("--branch_name", required=True, help="Branch or PR-123")
    parser.add_argument("--commit_sha", required=True, help="Full git SHA from Jenkins workspace")
    args = parser.parse_args()

    head_sha = args.commit_sha.strip()
    if len(head_sha) < 7:
        print(f"Invalid commit_sha: {head_sha}", file=sys.stderr)
        sys.exit(1)

    try:
        run_number, workflow_id, resolved_sha, pr_num = find_build_dev_apps_run_for_commit(
            args.branch_name, head_sha
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    if pr_num is not None:
        print(f"PR Number: {pr_num}")

    try:
        wait_for_lcov_coverage_artifact(workflow_id)
    except Exception as exc:
        print(f"ERROR waiting for LCOV artifact: {exc}", file=sys.stderr)
        sys.exit(1)

    if not github_run_has_dev_artifacts(workflow_id):
        print("SKIP_DEV_MERGE_WAIT=1")


if __name__ == "__main__":
    main()
