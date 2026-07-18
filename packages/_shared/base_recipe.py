from pathlib import Path
from conan import ConanFile
from conan.tools.files import copy
from contextlib import contextmanager
import os
import shutil
import yaml

# Shared metadata and helpers for matter packages

MATTER_SDK_PATH_PREFIX = "third_party/matter_sdk/"

# VCS metadata is not used at build time; copying it bloats the matter package (~10 GB).
MATTER_SDK_PACKAGE_EXCLUDES = (".git",)

_RECIPE_PATH = Path(__file__).resolve()
try:
    SHARED_REPO_ROOT = _RECIPE_PATH.parents[2]
except IndexError:
    SHARED_REPO_ROOT = _RECIPE_PATH.parent


class MatterBaseRecipe(ConanFile):
    user = "silabs"
    license = "www.silabs.com/about-us/legal/master-software-license-agreement"
    author = "Silicon Laboratories Inc."
    homepage = "https://github.com/SiliconLabsSoftware/matter_extension/blob/main/README.md"
    url = "https://github.com/SiliconLabsSoftware/matter_extension"
    topics = "silabs"
    python_requires = "silabs_package_assistant/[>=1]@silabs"

    sl_metadata = {
        "slack_channel": "#matter-development",
        "team": "MATTER",
        "confluence_doc": "",
        "jira_project": "https://jira.silabs.com/projects/MATTER/summary",
        "maintainers": [],
    }

    def set_version(self):
        pass

    def package_id(self):
        self.info.clear()

    @property
    def repo_root(self) -> Path:
        return SHARED_REPO_ROOT

    @property
    def dep_versions(self) -> dict:
        return _DEP_VERSIONS

    @property
    def matter_stack_requires(self) -> dict[str, str]:
        return load_matter_sdk_dependencies(self.repo_root)

    @property
    def matter_package_version(self) -> str:
        return resolve_matter_package_version(self.repo_root)

    def export_shared_recipe_support(self) -> None:
        shared_src = Path(self.recipe_folder).parent / "_shared"
        if shared_src.is_dir():
            copy(
                self,
                "*.py",
                src=str(shared_src),
                dst=os.path.join(self.export_folder, "_shared"),
            )
        for dep_src in _dependency_versions_candidates(self.repo_root):
            if dep_src.is_file():
                copy(
                    self,
                    dep_src.name,
                    src=str(dep_src.parent),
                    dst=self.export_folder,
                )
                break
        slce_src = self.repo_root / "matter.slce"
        if slce_src.is_file():
            copy(self, slce_src.name, src=str(slce_src.parent), dst=self.export_folder)


def flatten_matter_stack_deps(grouped: dict) -> dict[str, str]:
    merged: dict[str, str] = {}
    for group in ("common", "thread", "wifi"):
        for name, version in (grouped.get(group) or {}).items():
            merged[name] = str(version)
    return merged


def _exported_recipe_dependency_versions() -> Path | None:
    """dependency_versions.yaml co-located with the exported Conan recipe (cache e/)."""
    if _RECIPE_PATH.parent.name == "_shared":
        return _RECIPE_PATH.parents[1] / "dependency_versions.yaml"
    return None


def _dependency_versions_candidates(repo_root: Path) -> list[Path]:
    candidates: list[Path] = []
    exported = _exported_recipe_dependency_versions()
    if exported is not None:
        candidates.append(exported)
    candidates.append(repo_root / "slc" / "script" / "dependency_versions.yaml")
    return candidates


def load_matter_sdk_dependencies(repo_root: Path) -> dict[str, str]:
    for path in _dependency_versions_candidates(repo_root):
        if not path.is_file():
            continue
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        flat = data.get("dependencies")
        if flat:
            return {str(name): str(version) for name, version in flat.items()}
        return flatten_matter_stack_deps(data)
    raise FileNotFoundError(
        "dependency_versions.yaml not found for matter_sdk stack dependencies"
    )


def resolve_matter_sdk_source_root(repo_root: Path) -> Path:
    """Standalone matter_sdk clone used during matter_app export validation."""
    env_root = os.environ.get("MATTER_SDK_SOURCE_ROOT", "").strip()
    if env_root:
        return Path(env_root).resolve()
    sibling = repo_root.parent.parent.parent / "matter_sdk"
    if sibling.is_dir() and (sibling / "src").is_dir():
        return sibling.resolve()
    submodule = repo_root / "third_party" / "matter_sdk"
    if submodule.is_dir() and (submodule / "src").is_dir():
        return submodule.resolve()
    raise FileNotFoundError(
        "matter_sdk sources not found for export. Set MATTER_SDK_SOURCE_ROOT."
    )


def is_matter_sdk_package_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return normalized.startswith(MATTER_SDK_PATH_PREFIX) or normalized == MATTER_SDK_PATH_PREFIX.rstrip("/")


def package_matter_sdk_tree(
    conanfile: ConanFile,
    package_folder: Path,
    sdk_source_root: Path,
    repo_root: Path | None = None,
) -> None:
    """Copy matter_sdk tree (nlio/nlassert/mbedtls come from nested matter_sdk submodules)."""
    sdk_source_root = sdk_source_root.resolve()
    sdk_dst = package_folder / "third_party" / "matter_sdk"
    copy(
        conanfile,
        "*",
        src=str(sdk_source_root),
        dst=str(sdk_dst),
        keep_path=True,
        excludes=MATTER_SDK_PACKAGE_EXCLUDES,
    )
    _remove_packaged_git_metadata(sdk_dst)


def _remove_packaged_git_metadata(tree_root: Path) -> None:
    """Drop any .git directory left under a packaged tree (defensive cleanup)."""
    git_dir = tree_root / ".git"
    if git_dir.is_dir():
        shutil.rmtree(git_dir)


def _ensure_export_symlink(link_path: Path, target: Path) -> bool:
    """Create symlink when link_path is absent. Returns True if this call created it."""
    if link_path.exists():
        return False
    target = target.resolve()
    if not target.exists():
        raise FileNotFoundError(f"Export stub target does not exist: {target}")
    link_path.parent.mkdir(parents=True, exist_ok=True)
    link_path.symlink_to(target, target_is_directory=target.is_dir())
    return True


@contextmanager
def matter_sdk_export_stub(repo_root: Path):
    """Link matter_sdk for SLCC validation during export when submodule is absent."""
    sdk_root = resolve_matter_sdk_source_root(repo_root)
    created: list[Path] = []

    def maybe_link(link: Path, target: Path) -> None:
        if _ensure_export_symlink(link, target):
            created.append(link)

    matter_sdk_link = repo_root / "third_party" / "matter_sdk"
    if not matter_sdk_link.exists():
        maybe_link(matter_sdk_link, sdk_root)

    prev_cwd = os.getcwd()
    os.chdir(repo_root)
    try:
        yield repo_root / "third_party" / "matter_sdk"
    finally:
        os.chdir(prev_cwd)
        for link in reversed(created):
            if link.is_symlink():
                link.unlink()


def resolve_matter_package_version(repo_root: Path) -> str:
    candidates = [
        repo_root / "matter.slce",
        _RECIPE_PATH.parent.parent / "matter.slce",
        _RECIPE_PATH.parent / "matter.slce",
    ]
    for slce_path in candidates:
        if not slce_path.exists():
            continue
        with slce_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        version = str(data.get("version", "")).strip()
        if not version:
            raise RuntimeError(f"Version field missing or empty in {slce_path}")
        return version
    raise FileNotFoundError(
        f"SLCE file not found under {repo_root} or exported recipe folder"
    )


def _load_dep_versions_shared(filename: str = "dependency_versions.yaml") -> dict:
    candidates = list(_dependency_versions_candidates(SHARED_REPO_ROOT))
    candidates.extend(
        [
            _RECIPE_PATH.parent / filename,
            _RECIPE_PATH.parent.parent / filename,
        ]
    )
    for target in candidates:
        if not target.exists():
            continue
        try:
            with target.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise RuntimeError(
                f"Failed to parse dependency versions file {target}: {e}"
            ) from e
    raise FileNotFoundError(
        "Dependency versions file not found. Expected at "
        f"{SHARED_REPO_ROOT / 'slc' / 'script' / filename} "
        "or alongside the exported recipe."
    )


_DEP_VERSIONS = _load_dep_versions_shared()
