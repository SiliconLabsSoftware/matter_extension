#!/usr/bin/env python3
"""Build and upload the Matter skills ZIP and SLT feed from Jenkins."""

import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import quote
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / ".agents"
ARTIFACTORY = "https://artifactory.silabs.net/artifactory/studio-generic-development"
DOWNLOAD = "https://artifactory-local.silabs.net/artifactory/studio-generic-development"


def main():
    build = os.environ["BUILD_NUMBER"]
    branch = os.environ["BRANCH_NAME"]
    output_dir = REPO_ROOT / "jenkins_integration/dist"

    metadata = json.loads((AGENTS_DIR / "apack.json").read_text(encoding="utf-8"))
    match = re.search(r"^version:\s*(\S+)", (REPO_ROOT / "matter.slce").read_text(), re.MULTILINE)
    if not match:
        raise ValueError("No version found in matter.slce")
    version = f"{match.group(1)}-{build}"
    package = {"id": metadata["id"], "name": metadata["label"], "version": version}
    prefix = f"tools/mcp/{package['id']}/{quote(branch, safe='')}"
    zip_name = f"{package['id']}-{version}.zip"
    zip_location = f"{prefix}/{build}/{zip_name}"

    skills = sorted(path.parent for path in (AGENTS_DIR / "skills").glob("*/SKILL.md"))
    if not skills:
        raise ValueError("No skills found in .agents/skills")
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / zip_name
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(AGENTS_DIR / "apack.json", "apack.json")
        archive.writestr("postinstall-commands.txt", "".join(
            f"install-skills --agent all --source ${{rootdirectory}}/skills/{skill.name}\n"
            for skill in skills
        ))
        for skill in skills:
            for path in sorted(skill.rglob("*")):
                relative = path.relative_to(AGENTS_DIR)
                if path.is_file() and not any(
                    part.startswith(".") or part == "__pycache__" for part in relative.parts
                ) and path.suffix not in (".pyc", ".pyo"):
                    archive.write(path, relative.as_posix())

    site = {
        "id": package["id"], "description": metadata["description"],
        "featureLevel": 0, "packageType": "apack",
        "groups": [{**package, "groupPackages": [{"id": "mcp-config"}]}],
        "packages": [
            {**package, "os": system, "arch": arch, "dir": ".",
             "url": f"{DOWNLOAD}/{zip_location}"}
            for system, arch in [("windows", "amd64"), ("linux", "amd64"),
                                 ("darwin", "arm64"), ("darwin", "amd64")]
        ],
    }
    site_path = output_dir / "site.json"
    site_path.write_text(json.dumps(site, indent=2) + "\n", encoding="utf-8")
    print(f"ZIP: {zip_path}\nSite: {site_path}\nFeed URL: {ARTIFACTORY}/{prefix}/site.json")

    sys.path.insert(0, str(REPO_ROOT))
    from jenkins_integration.artifacts.artifactory_client import upload_to_artifactory

    upload_to_artifactory(
        str(zip_path), zip_name, branch, build,
        destination_url=f"{ARTIFACTORY}/{zip_location}"
    )
    upload_to_artifactory(
        str(site_path), "site.json", branch, build,
        destination_url=f"{ARTIFACTORY}/{prefix}/site.json", content_type="application/json"
    )


if __name__ == "__main__":
    main()
