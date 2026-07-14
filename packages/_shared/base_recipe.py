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

NESTED_MATTER_SDK_THIRD_PARTY_NAMES = ("nlio", "nlassert")
EXTENSION_THIRD_PARTY_NAMES = ("mbedtls", "nlio", "nlassert")

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


def _package_extension_third_party_copy(
    conanfile: ConanFile,
    repo_root: Path,
    package_folder: Path,
) -> None:
    """Copy mbedtls/nlio/nlassert from extension third_party into the matter package."""
    for name in ("nlio", "nlassert"):
        src_dir = repo_root / "third_party" / name
        dst_dir = package_folder / "third_party" / name
        if not src_dir.is_dir():
            raise FileNotFoundError(
                f"extension third_party/{name} not found under {repo_root}"
            )
        copy(
            conanfile,
            "*",
            src=str(src_dir),
            dst=str(dst_dir),
            keep_path=True,
        )

    mbedtls_src = repo_root / "third_party" / "mbedtls"
    mbedtls_dst = (
        package_folder / "third_party" / "matter_sdk" / "third_party" / "mbedtls"
    )
    if not mbedtls_src.is_dir():
        raise FileNotFoundError(
            f"extension third_party/mbedtls not found under {repo_root}"
        )
    for sub in ("library", "include"):
        sub_src = mbedtls_src / sub
        if sub_src.is_dir():
            copy(
                conanfile,
                "*",
                src=str(sub_src),
                dst=str(mbedtls_dst / sub),
                keep_path=True,
            )


def _package_nested_third_party_copy(
    conanfile: ConanFile,
    sdk_source_root: Path,
    package_folder: Path,
    name: str,
) -> None:
    """Copy nlio/nlassert from matter_sdk tree to top-level third_party paths."""
    src_dir = sdk_source_root / "third_party" / name
    dst_dir = package_folder / "third_party" / name
    repo_include = src_dir / "repo" / "include"
    if repo_include.is_dir():
        copy(
            conanfile,
            "*",
            src=str(repo_include),
            dst=str(dst_dir / "include"),
            keep_path=True,
        )
        return
    if src_dir.is_dir():
        copy(
            conanfile,
            "*",
            src=str(src_dir),
            dst=str(dst_dir),
            keep_path=True,
        )
        return
    raise FileNotFoundError(
        f"matter_sdk sources missing third_party/{name} under {sdk_source_root}"
    )


def _remove_packaged_git_metadata(tree_root: Path) -> None:
    """Drop any .git directory left under a packaged tree (defensive cleanup)."""
    git_dir = tree_root / ".git"
    if git_dir.is_dir():
        shutil.rmtree(git_dir)


def package_matter_sdk_tree(
    conanfile: ConanFile,
    package_folder: Path,
    sdk_source_root: Path,
    repo_root: Path | None = None,
) -> None:
    """Copy matter_sdk tree; mbedtls/nlio/nlassert come from extension third_party."""
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
    root = (repo_root or SHARED_REPO_ROOT).resolve()
    _package_extension_third_party_copy(conanfile, root, package_folder)


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


def _link_extension_third_party_for_export(
    repo_root: Path,
    maybe_link,
) -> None:
    """Expose extension third_party deps on matter_sdk paths used by SLCC files."""
    matter_sdk = (repo_root / "third_party" / "matter_sdk").resolve()
    top_mbedtls = repo_root / "third_party" / "mbedtls"
    nested_mbedtls = matter_sdk / "third_party" / "mbedtls"
    for sub in ("library", "include"):
        nested = nested_mbedtls / sub
        top = top_mbedtls / sub
        if not nested.exists() and top.is_dir():
            maybe_link(nested, top)

    for name in NESTED_MATTER_SDK_THIRD_PARTY_NAMES:
        top_include = repo_root / "third_party" / name / "include"
        if top_include.is_dir():
            continue
        src_dir = matter_sdk / "third_party" / name
        repo_include = src_dir / "repo" / "include"
        if repo_include.is_dir():
            maybe_link(top_include, repo_include)
        elif src_dir.is_dir():
            maybe_link(repo_root / "third_party" / name, src_dir)


@contextmanager
def matter_sdk_export_stub(repo_root: Path):
    """Link extension third_party deps for SLCC validation during export."""
    sdk_root = resolve_matter_sdk_source_root(repo_root)
    created: list[Path] = []

    def maybe_link(link: Path, target: Path) -> None:
        if _ensure_export_symlink(link, target):
            created.append(link)

    matter_sdk_link = repo_root / "third_party" / "matter_sdk"
    if not matter_sdk_link.exists():
        maybe_link(matter_sdk_link, sdk_root)

    _link_extension_third_party_for_export(repo_root, maybe_link)

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
