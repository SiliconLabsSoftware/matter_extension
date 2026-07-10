"""Shared helpers for matter stack dependency versions."""

from pathlib import Path
import yaml

DEP_VERSIONS_FILE = "dependency_versions.yaml"


def load_grouped_deps(repo_root: Path) -> dict:
    path = repo_root / "slc" / "script" / DEP_VERSIONS_FILE
    if not path.exists():
        raise FileNotFoundError(f"Dependency versions file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def flatten_matter_stack_deps(grouped: dict) -> dict[str, str]:
    merged: dict[str, str] = {}
    for group in ("common", "thread", "wifi"):
        for name, version in (grouped.get(group) or {}).items():
            merged[name] = str(version)
    return merged


def load_flattened_stack_deps(repo_root: Path) -> dict[str, str]:
    grouped = load_grouped_deps(repo_root)
    flat = grouped.get("dependencies")
    if flat:
        return {str(name): str(version) for name, version in flat.items()}
    return flatten_matter_stack_deps(grouped)
