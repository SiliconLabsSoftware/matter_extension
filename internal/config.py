import os

repo_owner = "SiliconLabsSoftware"
repo_name = "matter_extension"
pr_sha_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls'
sha_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits?sha='
commits_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits'
actions_runs_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs'
actions_runs_url_pr = f'https://api.github.com/repos/{repo_owner}/{repo_name}/actions/runs?event=pull_request'

# Require new update token
_token = os.getenv("GITHUB_UPDATE_TOKEN")
if not _token:
    raise RuntimeError("Missing GITHUB_UPDATE_TOKEN in environment")

github_auth = "Bearer " + _token
github_headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': github_auth,
    'X-GitHub-Api-Version': '2022-11-28'}
artifact_upload_path_dev = 'https://artifactory.silabs.net/artifactory/gsdk-generic-development/matter_extension_github/'
artifact_upload_path_release = 'https://artifactory.silabs.net/artifactory/gsdk-generic-staging/matter_extension_github/'
artifactory_headers = {'Content-type': 'application/zip'}
