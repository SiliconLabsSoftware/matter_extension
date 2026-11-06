#!/usr/bin/env python3
"""Delete the GHCR provision bundle version tagged for a closed pull request."""

import os
import subprocess
import sys

import common


def main():
    pr = (sys.argv[1] if len(sys.argv) > 1 else None) or os.environ.get("GITHUB_PR_NUMBER")
    if not pr:
        common.die("usage: delete_provision_pr_package.py <pr_number> (or set GITHUB_PR_NUMBER)")

    gh = common.require_cmd("gh")
    tag = common.resolve_provision_tag(pr_num=str(pr))
    package_ref = common.manifest_lookup("ghcr.package")
    org, package = package_ref.removeprefix("ghcr.io/").split("/", 1)
    versions = f"/orgs/{org}/packages/container/{package}/versions"

    print(f"Looking for {package_ref}:{tag}")
    listed = subprocess.run(
        [
            gh,
            "api",
            "--paginate",
            versions,
            "--jq",
            f'.[] | select(.metadata.container.tags[]? == "{tag}") | .id',
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    version_id = listed.stdout.strip().splitlines()[0] if listed.stdout.strip() else ""
    if not version_id:
        print(f"No package version found for tag {tag}; nothing to delete")
        return

    subprocess.run([gh, "api", "-X", "DELETE", f"{versions}/{version_id}"], check=True)
    print(f"Deleted {package_ref}:{tag} (version id={version_id})")


if __name__ == "__main__":
    main()
