"""Shared paths, manifest lookup, and host detection for the Renode bundle scripts."""

import hashlib
import json
import os
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RENODE_INTEGRATION_DIR = os.path.dirname(SCRIPT_DIR)
REPO_ROOT = os.path.dirname(RENODE_INTEGRATION_DIR)
MANIFEST_PATH = os.path.join(RENODE_INTEGRATION_DIR, "sim-manifest.json")
CACHE_DIR = os.path.join(RENODE_INTEGRATION_DIR, ".cache")
BUNDLE_VERSION = "v0"


def bundle_dir():
    return os.environ.get("BUNDLE_DIR", os.path.join(RENODE_INTEGRATION_DIR, "out", "bundle"))


RENODE_SRC_DIR = os.path.join(RENODE_INTEGRATION_DIR, "renode-src")


def ensure_renode_source_tree():
    """Clone and check out the Renode commit pinned in sim-manifest.json."""
    src_dir = RENODE_SRC_DIR
    commit = manifest_lookup("renode.commit")
    repo_url = manifest_lookup("renode.repo")

    if not os.path.isdir(os.path.join(src_dir, ".git")):
        subprocess.run(["git", "clone", repo_url, src_dir], check=True)
    fetched = subprocess.run(["git", "-C", src_dir, "fetch", "origin", commit, "--depth", "1"])
    if fetched.returncode != 0:
        subprocess.run(["git", "-C", src_dir, "fetch", "--unshallow"], check=False)
    subprocess.run(["git", "-C", src_dir, "checkout", commit], check=True)


def test_lib_source_dir():
    return os.path.join(RENODE_SRC_DIR, "tests", "test_lib")


def die(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_cmd(name):
    path = shutil.which(name)
    if path is None:
        die(f"missing required command: {name}")
    return path


def load_manifest():
    with open(MANIFEST_PATH, encoding="utf-8") as handle:
        return json.load(handle)


def manifest_lookup(path):
    cur = load_manifest()
    for key in path.split("."):
        cur = cur[key]
    return cur


def artifact_tag(kind, host=None):
    if kind == "common":
        return f"{BUNDLE_VERSION}-common"
    if kind == "runtime":
        return f"{BUNDLE_VERSION}-runtime-{host or detect_host()}"
    die(f"unknown bundle kind: {kind}")


def detect_host():
    system = os.uname().sysname
    machine = os.uname().machine
    if system == "Linux":
        version_path = "/proc/version"
        if os.path.isfile(version_path):
            with open(version_path, encoding="utf-8", errors="replace") as handle:
                if "microsoft" in handle.read().lower():
                    return "linux-x64"
        if machine in ("x86_64", "amd64"):
            return "linux-x64"
        if machine in ("aarch64", "arm64"):
            return "linux-arm64"
    elif system == "Darwin":
        if machine == "arm64":
            return "osx-arm64"
        if machine == "x86_64":
            return "osx-x64"
    die(f"unsupported host: {system}/{machine}")


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_debugfs():
    found = shutil.which("debugfs")
    if found:
        return found
    for candidate in (
        "/opt/homebrew/opt/e2fsprogs/sbin/debugfs",
        "/usr/sbin/debugfs",
    ):
        if os.access(candidate, os.X_OK):
            return candidate
    die("debugfs not found (install e2fsprogs)")
