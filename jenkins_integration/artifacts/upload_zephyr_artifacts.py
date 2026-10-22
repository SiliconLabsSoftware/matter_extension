"""
Download Build Zephyr artifacts from GitHub Actions and upload board binaries to UBAI.

Expects GHA layout (see build-zephyr.yaml):
    <app_name>/<TARGET>/<binary_name>.<ext>
        -> UBAI Name=<binary_name>, app_name="", target=<TARGET>

Add another app by exporting under a new <app_name>/ tree in the workflow; no
uploader changes required.

Usage:
    python upload_zephyr_artifacts.py --branch_name <branch> --build_number <n> --workflow_id <id>

Use the workflow run selected by Jenkins. Package-backed runs are skipped.
"""

import argparse
import os
import shutil
import sys
import time
import zipfile

workspace_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import jenkins_integration.config as config
from jenkins_integration.github.github_workflow import _make_github_api_request
from jenkins_integration.artifacts.ubai_client import upload_to_ubai


ARTIFACT_NAME = 'dev-artifacts-zephyr'
WORKFLOW_PATH = '.github/workflows/dev-apps-builder.yaml'
WAIT_ATTEMPTS = 20
WAIT_SECONDS = 60


def _parse_args():
    parser = argparse.ArgumentParser(
        description='Upload Build Zephyr binaries to UBAI')
    parser.add_argument('--branch_name', required=True)
    parser.add_argument('--build_number', required=True)
    parser.add_argument('--workflow_id', type=int, required=True,
                        help='Selected dev-apps workflow run ID')
    return parser.parse_args()


def _get_workflow_run(workflow_id):
    url = f"{config.actions_runs_base_url}/{workflow_id}"
    return _make_github_api_request(url).json()


def _get_artifact_download_url(workflow_id):
    url = f"{config.actions_runs_base_url}/{workflow_id}/artifacts"
    per_page = 100
    response_data = _make_github_api_request(
        f"{url}?per_page={per_page}&page=1").json()
    artifacts = response_data.get('artifacts') or []
    total_count = response_data.get('total_count', len(artifacts))
    total_pages = (total_count + per_page - 1) // per_page

    for page in range(2, total_pages + 1):
        response = _make_github_api_request(
            f"{url}?per_page={per_page}&page={page}")
        artifacts.extend(response.json().get('artifacts') or [])

    artifact = next(
        (artifact for artifact in artifacts if artifact['name'] == ARTIFACT_NAME), None)
    if not artifact:
        available = [artifact['name'] for artifact in artifacts]
        raise RuntimeError(
            f"No {ARTIFACT_NAME} on workflow {workflow_id}. Available: {available}"
        )
    return artifact['archive_download_url'], artifact['name'] + '.zip'


def _download_and_extract(download_url, artifact_name):
    artifact_file = os.path.join('.', artifact_name)
    extracted_folder = os.path.join('.', artifact_name.replace('.zip', ''))

    if os.path.exists(artifact_file):
        os.remove(artifact_file)
    if os.path.exists(extracted_folder):
        shutil.rmtree(extracted_folder)

    print(f"Downloading {artifact_name}")
    response = _make_github_api_request(download_url)
    with open(artifact_file, 'wb') as f:
        f.write(response.content)

    os.makedirs(extracted_folder, exist_ok=True)
    with zipfile.ZipFile(artifact_file, 'r') as zf:
        zf.extractall(extracted_folder)
    print(f"Extracted to {extracted_folder}")
    return extracted_folder


def _download_zephyr_artifact(workflow_id):
    """Return the artifact directory, or None for workflows without Zephyr builds."""
    for attempt in range(1, WAIT_ATTEMPTS + 1):
        run = _get_workflow_run(workflow_id)
        workflow_path = run['path'].split('@', 1)[0]
        if workflow_path != WORKFLOW_PATH:
            print(
                f"Skipping Zephyr upload for workflow {workflow_id}: {workflow_path}")
            return None
        status = run.get('status')
        conclusion = run.get('conclusion')
        if status == 'completed' and conclusion != 'success':
            raise RuntimeError(
                f"Build Zephyr workflow {workflow_id} failed with conclusion '{conclusion}'"
            )

        try:
            download_url, name = _get_artifact_download_url(workflow_id)
            return _download_and_extract(download_url, name)
        except RuntimeError as e:
            if attempt < WAIT_ATTEMPTS and ARTIFACT_NAME in str(e) and status != 'completed':
                print(
                    f"Artifact not ready ({attempt}/{WAIT_ATTEMPTS}), "
                    f"waiting {WAIT_SECONDS}s..."
                )
                time.sleep(WAIT_SECONDS)
                continue
            raise


def _iter_zephyr_binaries(root):
    """Yield (app_name, target, file_path) for each <app>/<TARGET>/<file> binary."""
    for app_name in sorted(os.listdir(root)):
        app_dir = os.path.join(root, app_name)
        if not os.path.isdir(app_dir):
            continue
        for target in sorted(os.listdir(app_dir)):
            target_dir = os.path.join(app_dir, target)
            if not os.path.isdir(target_dir):
                continue
            for file_name in sorted(os.listdir(target_dir)):
                file_path = os.path.join(target_dir, file_name)
                if os.path.isfile(file_path):
                    yield app_name, target, file_path


def _upload_binaries(root, branch_name, build_number):
    failures = []
    uploaded = 0

    for app_name, target, file_path in _iter_zephyr_binaries(root):
        file_name = os.path.basename(file_path)
        print(
            f"Uploading {app_name}/{target}/{file_name} to UBAI (target={target})")
        if upload_to_ubai(file_path, "", target, branch_name, build_number):
            uploaded += 1
        else:
            failures.append(f"{app_name}/{target}/{file_name}")

    if uploaded == 0 and not failures:
        raise RuntimeError(
            f"No Zephyr binaries found under {root}. Expected <app>/<TARGET>/<name>.<ext>"
        )
    if failures:
        raise RuntimeError(f"UBAI upload failed: {', '.join(failures)}")
    print(f"Uploaded {uploaded} Zephyr binary(ies) to UBAI")


def main():
    args = _parse_args()
    extracted = _download_zephyr_artifact(args.workflow_id)
    if extracted is None:
        return
    _upload_binaries(extracted, args.branch_name, args.build_number)
    artifact_file = os.path.join('.', ARTIFACT_NAME + '.zip')
    if not upload_to_ubai(
        file_path=artifact_file,
        app_name="matter",
        target="matter",
        branch_name=args.branch_name,
        build_number=args.build_number,
    ):
        raise RuntimeError(f"UBAI upload failed: {artifact_file}")


if __name__ == '__main__':
    main()
