from pathlib import Path
from conan import ConanFile
from conan.tools.files import copy
from typing import Generator, Optional
import os
import re
import yaml

# Shared metadata and helpers for matter packages

_RECIPE_PATH = Path(__file__).resolve()
try:
    SHARED_REPO_ROOT = _RECIPE_PATH.parents[2]
except IndexError:
    SHARED_REPO_ROOT = _RECIPE_PATH.parent

_LINE_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


class MatterBaseRecipe(ConanFile):
    user = "silabs"
    license = "www.silabs.com/about-us/legal/master-software-license-agreement"
    author = "Silicon Laboratories Inc."
    homepage = "https://github.com/SiliconLabsSoftware/matter_extension/blob/main/README.md"
    url = "https://github.com/SiliconLabsSoftware/matter_extension"
    topics = "silabs"
    python_requires = "silabs_package_assistant/[>=1 <2]@silabs"

    # Central SL metadata
    sl_metadata = {
        "slack_channel": "#matter-development",
        "team": "MATTER",
        "confluence_doc": "",
        "jira_project": "https://jira.silabs.com/projects/MATTER/summary",
        "maintainers": [],
    }

    # Sample apps that must never be Conan-packaged (git-checkout only).
    # Subclasses may override.
    _EXCLUDED_APP_PATH_PARTS = ("dishwasher_app",)

    # Project input sections only — skip export/artifact build outputs, filter tags, etc.
    _INPUT_PATH_KEYS = (
        "source",
        "include",
        "config_file",
        "other_file",
        "readme",
        "post_build",
    )

    def set_version(self):
        """Resolve Conan version (SLCE base + SL_PRERELEASE*).

        Priority:
          1. MATTER_PACKAGE_VERSION env (explicit override for local/CI one-offs)
          2. silabs_package_assistant.get_version(matter.slce)
             - local: base + "-0.dev" (e.g. 2.10.0-0.dev)
             - CI with SL_PRERELEASE + SL_PRERELEASE_NUMBER: base + "-alpha.N"
        """
        override = os.environ.get("MATTER_PACKAGE_VERSION", "").strip()
        if override:
            self.version = override
            return

        assistant = self.python_requires["silabs_package_assistant"].module
        self.version = self.version or assistant.get_version(self.matter_slce_path)

    def package_id(self):
        # Unified behavior: header-only / content-only style id
        self.info.clear()

    def export_shared_recipe_support(self) -> None:
        """Copy helpers into the Conan export folder so cached recipes can import _shared.

        Without this, slt install reloads e/conanfile.py and fails with:
        ModuleNotFoundError: No module named '_shared'
        """
        shared_src = Path(self.recipe_folder).parent / "_shared"
        if shared_src.is_dir():
            copy(
                self,
                "*",
                src=str(shared_src),
                dst=os.path.join(self.export_folder, "_shared"),
                excludes=("__pycache__", "*.pyc", "*.sh"),
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

    @property
    def repo_root(self) -> Path:
        """Repository root directory (shared across all Matter recipes)."""
        return SHARED_REPO_ROOT

    @property
    def matter_slce_path(self) -> str:
        """Path to matter.slce (repo root, or beside exported recipe in Conan cache)."""
        candidates = [self.repo_root / "matter.slce"]
        recipe_folder = getattr(self, "recipe_folder", None)
        if recipe_folder:
            candidates.insert(0, Path(recipe_folder) / "matter.slce")
        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
        return str(self.repo_root / "matter.slce")

    @property
    def matter_line_version(self) -> str:
        """X.Y.Z line version from matter.slce (no prerelease suffix)."""
        assistant = self.python_requires["silabs_package_assistant"].module
        line = assistant.get_base_version(self.matter_slce_path)
        if not _LINE_VERSION_RE.match(line):
            raise RuntimeError(
                f"matter.slce version must be X.Y.Z, got {line!r}"
            )
        return line

    @property
    def matter_conan_range(self) -> str:
        """Conan requires() range for matter (includes prereleases)."""
        line = self.matter_line_version
        major, minor, patch = line.split(".")
        upper = f"{major}.{minor}.{int(patch) + 1}"
        return f"[>={line} <{upper},include_prerelease]"

    # --------------- Required root metadata files ---------------
    # Subclasses define _REQUIRED_ROOT_FILES as a tuple of repo-relative paths.
    # Then: files_to_package.update(self._gather_required_root_files())
    #       self._require_root_files(files_to_package)

    def _gather_required_root_files(self) -> set[str]:
        """Return repo-relative paths from _REQUIRED_ROOT_FILES that exist on disk."""
        required = getattr(self, "_REQUIRED_ROOT_FILES", ())
        collected: set[str] = set()
        for name in required:
            if (self.repo_root / name).is_file():
                collected.add(name)
        return collected

    def _require_root_files(self, files_to_package: set[str]) -> None:
        """Hard-fail if any _REQUIRED_ROOT_FILES entry is missing from the package set."""
        required = getattr(self, "_REQUIRED_ROOT_FILES", ())
        if not required:
            return

        root = self.repo_root.resolve()
        packaged_rels: set[str] = set()
        packaged_resolved: set[Path] = set()
        for entry in files_to_package:
            p = Path(entry)
            if not p.is_absolute():
                p = root / p
            try:
                resolved = p.resolve()
                packaged_resolved.add(resolved)
                packaged_rels.add(str(resolved.relative_to(root)))
            except (ValueError, OSError):
                packaged_rels.add(str(entry))

        missing = [
            name
            for name in required
            if name not in files_to_package
            and name not in packaged_rels
            and (root / name).resolve() not in packaged_resolved
        ]
        if missing:
            pkg = getattr(self, "name", type(self).__name__)
            raise FileNotFoundError(
                f"{pkg} package is missing required root metadata files: {missing}. "
                "Ensure they exist under the repo root and are packaged successfully."
            )

    # --------------- Shared dependency versions ---------------
    @property
    def dep_versions(self) -> dict:
        """Access centralized dependency versions loaded from canonical YAML.

        Path: <repo_root>/slc/script/dependency_versions.yaml
        Raises FileNotFoundError or RuntimeError if missing/malformed to fail fast.
        Cached at module import time for performance.
        """
        return _DEP_VERSIONS

    # --------------- Sample-app / SLC packaging helpers ---------------
    def _existing_repo_relative_files(self, files: set[str]) -> set[str]:
        """Keep existing files as paths relative to repo_root (cwd-independent)."""
        root = self.repo_root.resolve()
        normalized: set[str] = set()
        for file in files:
            p = Path(file)
            if not p.is_absolute():
                p = root / file
            if not p.is_file():
                continue
            try:
                normalized.add(str(p.resolve().relative_to(root)))
            except ValueError:
                normalized.add(str(p.resolve()))
        return normalized

    @classmethod
    def _iter_slc_path_entries(cls, node) -> Generator[str, None, None]:
        """Yield every string 'path' value from nested SLC YAML structures."""
        if isinstance(node, dict):
            path_val = node.get("path")
            if isinstance(path_val, str):
                yield path_val
            for value in node.values():
                yield from cls._iter_slc_path_entries(value)
        elif isinstance(node, list):
            for item in node:
                yield from cls._iter_slc_path_entries(item)

    @classmethod
    def _iter_input_path_entries(cls, data: dict) -> Generator[str, None, None]:
        """Yield path values from sample input sections only."""
        for key in cls._INPUT_PATH_KEYS:
            section = data.get(key)
            if section is None:
                continue
            yield from cls._iter_slc_path_entries(section)

    @classmethod
    def _iter_slcc_input_file_paths(cls, data: dict) -> Generator[str, None, None]:
        """Yield repo-style paths from .slcc input sections (honors file_list)."""
        for key in cls._INPUT_PATH_KEYS:
            section = data.get(key)
            if not isinstance(section, list):
                continue
            for item in section:
                if not isinstance(item, dict):
                    continue
                base = item.get("path")
                if not isinstance(base, str) or not base.strip():
                    continue
                base = base.strip().replace("\\", "/")
                file_list = item.get("file_list")
                if file_list:
                    for fl in file_list:
                        if isinstance(fl, dict) and isinstance(fl.get("path"), str):
                            sub = fl["path"].strip().replace("\\", "/").lstrip("/")
                            yield f"{base.rstrip('/')}/{sub}"
                        elif isinstance(fl, str) and fl.strip():
                            yield f"{base.rstrip('/')}/{fl.strip().lstrip('/')}"
                else:
                    yield base

    @classmethod
    def _is_excluded_app_path(cls, path) -> bool:
        """True when the SLC project lives under an app excluded from packaging."""
        excluded = getattr(cls, "_EXCLUDED_APP_PATH_PARTS", ())
        parts = Path(path).parts
        return any(part in excluded for part in parts)

    @staticmethod
    def _slc_project_selected(
        data: dict,
        desired_qualities: list[str],
        desired_packages: list[str],
    ) -> bool:
        """Match Matter projects/components by quality and package id."""
        quality = data.get("quality")
        if quality is not None and quality not in desired_qualities:
            return False

        package = data.get("package")
        if package in desired_packages:
            return True

        for ext in data.get("sdk_extension") or []:
            if isinstance(ext, dict) and ext.get("id") in desired_packages:
                return True
        return False

    def _gather_slcp_external_inputs(
        self,
        desired_qualities: list[str],
        desired_packages: list[str],
    ) -> set[str]:
        """Collect files referenced by .slcp/.slcw input paths for packaging.

        Only source/include/config_file/other_file/readme/post_build paths are
        considered. Export artifacts (e.g. artifact/*.o) are ignored.

        Sample projects use repo-relative paths such as
        ../../../../third_party/matter_sdk/... . Those must exist under the
        app package root so CLI generate resolves them the same way as in the
        git tree.
        """
        root = self.repo_root.resolve()
        collected: set[str] = set()
        missing: list[str] = []
        pkg = getattr(self, "name", type(self).__name__)

        for slc_file in root.rglob("*.slc*"):
            if "third_party" in slc_file.parts:
                continue
            if slc_file.suffix not in (".slcp", ".slcw"):
                continue
            if self._is_excluded_app_path(slc_file):
                continue

            try:
                data = yaml.safe_load(slc_file.read_text(encoding="utf-8")) or {}
            except Exception as e:
                self.output.warning(f"Skip unreadable {slc_file}: {e}")
                continue

            if not isinstance(data, dict):
                continue
            if not self._slc_project_selected(data, desired_qualities, desired_packages):
                continue

            for rel in self._iter_input_path_entries(data):
                # Skip bare file_list names (resolved under their include dir).
                if "/" not in rel and not rel.startswith("."):
                    continue

                resolved = (slc_file.parent / rel).resolve()
                try:
                    resolved.relative_to(root)
                except ValueError:
                    missing.append(f"{slc_file}: {rel} (outside repo)")
                    continue

                if not resolved.exists():
                    missing.append(f"{slc_file}: {rel}")
                    continue

                if resolved.is_file():
                    collected.add(str(resolved))
                elif resolved.is_dir():
                    for file_path in resolved.rglob("*"):
                        if file_path.is_file():
                            collected.add(str(file_path))

        if missing:
            sample = "\n  ".join(missing[:30])
            more = f"\n  ... and {len(missing) - 30} more" if len(missing) > 30 else ""
            raise FileNotFoundError(
                f"{pkg} packaging missing .slcp/.slcw inputs "
                "(initialize third_party/matter_sdk submodule before export-pkg):\n  "
                f"{sample}{more}"
            )

        self.output.info(
            f"Gathered {len(collected)} files from .slcp/.slcw input path references "
            f"for {pkg} packaging"
        )
        return collected

    def _gather_internal_slcc_files(self, desired_packages: list[str]) -> set[str]:
        """Collect quality:internal .slcc files and their input path references.

        These stack components are excluded from the public matter package and must
        ship with matter_internal (e.g. matter_ble_dmp_test + DMP btconf).
        """
        root = self.repo_root.resolve()
        component_root = root / "slc" / "component"
        collected: set[str] = set()
        missing: list[str] = []
        pkg = getattr(self, "name", type(self).__name__)

        if not component_root.is_dir():
            return collected

        for slcc_file in component_root.rglob("*.slcc"):
            try:
                data = yaml.safe_load(slcc_file.read_text(encoding="utf-8")) or {}
            except Exception as e:
                self.output.warning(f"Skip unreadable {slcc_file}: {e}")
                continue

            if not isinstance(data, dict):
                continue
            if data.get("quality") != "internal":
                continue
            if not self._slc_project_selected(
                data, desired_qualities=["internal"], desired_packages=desired_packages
            ):
                continue

            try:
                collected.add(str(slcc_file.resolve().relative_to(root)))
            except ValueError:
                collected.add(str(slcc_file.resolve()))

            for rel in self._iter_slcc_input_file_paths(data):
                # .slcc paths are normally repo-relative; fall back to slcc-relative.
                candidates = []
                if rel.startswith((".", "/")):
                    candidates.append((slcc_file.parent / rel).resolve())
                else:
                    candidates.append((root / rel).resolve())
                    candidates.append((slcc_file.parent / rel).resolve())

                resolved = next((c for c in candidates if c.exists()), None)
                if resolved is None:
                    missing.append(f"{slcc_file}: {rel}")
                    continue
                try:
                    resolved.relative_to(root)
                except ValueError:
                    missing.append(f"{slcc_file}: {rel} (outside repo)")
                    continue

                if resolved.is_file():
                    collected.add(str(resolved))
                elif resolved.is_dir():
                    for file_path in resolved.rglob("*"):
                        if file_path.is_file():
                            collected.add(str(file_path))

        if missing:
            sample = "\n  ".join(missing[:30])
            more = f"\n  ... and {len(missing) - 30} more" if len(missing) > 30 else ""
            raise FileNotFoundError(
                f"{pkg} packaging missing internal .slcc inputs "
                "(initialize third_party/matter_sdk submodule before export-pkg):\n  "
                f"{sample}{more}"
            )

        self.output.info(
            f"Gathered {len(collected)} files from internal .slcc components "
            f"for {pkg} packaging"
        )
        return collected

    def _gather_slc_release_files(
        self,
        desired_qualities: list[str],
        desired_packages: list[str],
        assistant,
    ) -> set:
        """Discover .slcp/.slcw files (excluding third_party) and collect related release files.

        Returns a set of file paths including the SLC definition file itself plus any related files
        when the assistant reports matches for the given qualities/packages.
        """
        collected: set[str] = set()
        root = self.repo_root
        for slc_file in root.rglob("*.slc*"):
            if "third_party" in slc_file.parts:
                continue
            if slc_file.suffix not in (".slcp", ".slcw"):
                continue
            if self._is_excluded_app_path(slc_file):
                continue
            rel_path = str(slc_file)
            try:
                related = assistant.list_files_in_slc_file(
                    slc_file_path=rel_path,
                    desired_qualities=desired_qualities,
                    desired_packages=desired_packages,
                    fail_on_missing_files=False,
                )
            except Exception as e:
                self.output.warning(f"Failed processing {rel_path}: {e}")
                continue
            if related:
                collected.add(rel_path)
                collected.update(related)
        return collected

    def _collect_app_package_files(
        self,
        desired_qualities: list[str],
        desired_packages: list[str],
        assistant,
        *,
        include_internal_slcc: bool = False,
        seed: Optional[set[str]] = None,
    ) -> set[str]:
        """Gather sample-app package file set (release + inputs + optional internal .slcc).

        Shared by matter_app / matter_app_internal package() and build() to avoid drift.
        Returns existing repo-relative paths with required root files re-applied and checked.
        """
        files_to_package: set[str] = set(seed or ())
        files_to_package.update(
            self._gather_slc_release_files(
                desired_qualities=desired_qualities,
                desired_packages=desired_packages,
                assistant=assistant,
            )
        )
        files_to_package.update(self._gather_required_root_files())
        files_to_package.update(
            self._gather_slcp_external_inputs(
                desired_qualities=desired_qualities,
                desired_packages=desired_packages,
            )
        )
        if include_internal_slcc:
            files_to_package.update(
                self._gather_internal_slcc_files(desired_packages=desired_packages)
            )
        # Resolve against repo_root — cwd during export-pkg is not always the repo.
        files_to_package = self._existing_repo_relative_files(files_to_package)
        # Root metadata uses repo-relative names; re-add after exists-filter, then hard-require.
        files_to_package.update(self._gather_required_root_files())
        self._require_root_files(files_to_package)
        return files_to_package


def _dependency_versions_candidates(repo_root: Path) -> list[Path]:
    """Repo path plus copy co-located with exported recipe (cache e/)."""
    candidates: list[Path] = [
        repo_root / "slc" / "script" / "dependency_versions.yaml",
    ]
    # When this file lives at e/_shared/base_recipe.py, yaml is at e/
    if _RECIPE_PATH.parent.name == "_shared":
        candidates.insert(0, _RECIPE_PATH.parents[1] / "dependency_versions.yaml")
    return candidates


def _load_dep_versions_shared(filename: str = "dependency_versions.yaml") -> dict:
    """Load dependency versions as a flat name->version map for Conan recipes.

    Supports the grouped YAML format (common/thread/wifi) used by generation
    scripts, and the legacy flat format. For the stack package, all groups are
    merged (common, then thread, then wifi; later entries override duplicates).
    """
    target = None
    for candidate in _dependency_versions_candidates(SHARED_REPO_ROOT):
        # Allow override of filename for the last path segment when searching repo
        if candidate.name != filename and candidate.parent.name == "script":
            candidate = candidate.parent / filename
        if candidate.is_file():
            target = candidate
            break
    if target is None:
        raise FileNotFoundError(
            f"Dependency versions file '{filename}' not found under "
            f"{SHARED_REPO_ROOT}/slc/script or exported recipe folder"
        )
    try:
        with target.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception as e:
        raise RuntimeError(
            f"Failed to parse dependency versions file {target}: {e}"
        )

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Dependency versions file {target} must contain a mapping"
        )

    if any(k in data for k in ("common", "thread", "wifi")):
        merged: dict = {}
        for group in ("common", "thread", "wifi"):
            group_data = data.get(group) or {}
            if not isinstance(group_data, dict):
                raise RuntimeError(
                    f"Dependency group '{group}' in {target} must be a mapping"
                )
            for name, version in group_data.items():
                if version is None:
                    continue
                merged[name] = version
        return merged

    return {k: v for k, v in data.items() if v is not None}


_DEP_VERSIONS = _load_dep_versions_shared()
