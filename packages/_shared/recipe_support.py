"""Shared helpers for Matter Conan recipes.

Recipes stay thin ``ConanFile`` subclasses. This module is not a ``ConanFile``.
``packages/pkgctl.py`` exports every recipe listed in ``packages/packages.yaml``.

File lists, versions, channels, path relocation, and the copy into the package
come from ``silabs_package_assistant`` (``find_slc_files_to_release``,
``list_files_in_slc_file``, ``get_version``, ``get_base_version``,
``get_channel``, ``trim_paths``, ``copy_files``, ``generate_metadata``).

Two Conan contexts matter:

* ``conan export-pkg`` loads ``packages/<name>/conanfile.py`` from the checkout.
  ``layout()`` sets the source folder to the checkout root, and ``package()``
  reads the tree from there.
* A later ``conan install`` loads the copy under the cache ``e/`` folder, which
  is not a git checkout. ``requirements()`` and ``set_version()`` must use files
  copied beside the recipe (``matter.slce``, ``matter_dependencies.yaml``).

Adding ``matter_internal`` / ``matter_app_internal`` later means a new
``PackageSpec``, a ``conanfile.py``, and one entry in ``packages.yaml``.
Internal content is selected by SLC ``quality: internal``, not by path.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import yaml

# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

LINE_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")

# Pinned dependency versions for the matter stack, in packages/ beside this recipe tree.
DEP_VERSIONS_FILE = "matter_dependencies.yaml"

PACKAGE_USER = "silabs"
PACKAGE_LICENSE = (
    "www.silabs.com/about-us/legal/master-software-license-agreement"
)
PACKAGE_AUTHOR = "Silicon Laboratories Inc."
PACKAGE_HOMEPAGE = (
    "https://github.com/SiliconLabsSoftware/matter_extension/blob/main/README.md"
)
PACKAGE_URL = "https://github.com/SiliconLabsSoftware/matter_extension"
PACKAGE_TOPICS = "silabs"
PYTHON_REQUIRES = "silabs_package_assistant/[~2]@silabs"

SL_METADATA = {
    "slack_channel": "#matter-development",
    "team": "MATTER",
    "confluence_doc": "",
    "jira_project": "https://jira.silabs.com/projects/MATTER/summary",
    "maintainers": [],
}

# Public packages. Internal recipes will use ("internal",).
PUBLIC_QUALITIES = ("production", "evaluation", "experimental")

# Consumed as separate Conan packages (SiSDK / Wi-Fi / AWS OTA). SLC
# components may list files under these trees; never ship the trees themselves.
EXCLUDED_PATH_PREFIXES = (
    "third_party/simplicity_sdk",
    "third_party/aws_ota_sdk",
    "third_party/wifi_sdk",
)

# sdk_extension id only; a component line "- id: wifi" has no version.
_WISECONNECT_EXTENSION = re.compile(
    r"^(\s*- id: )wiseconnect3_sdk(\r?\n\s+version:)",
    re.MULTILINE,
)


def slt_options() -> dict:
    """SLT metadata options. A fresh dict per recipe so Conan cannot alias them."""
    return {
        "compatibleVersion": ["ANY"],
        "subPackage": [True, False],
        "releaseNotesUrl": ["ANY"],
        "packageType": ["ANY"],
        "sdkLtsTag": ["ANY"],
    }


def slt_default_options() -> dict:
    """Default SLT option values. ``packageType`` is ``sdk`` for Matter packages."""
    return {
        "compatibleVersion": "ANY",
        "subPackage": False,
        "releaseNotesUrl": "",
        "packageType": "sdk",
        "sdkLtsTag": "",
    }


@dataclass(frozen=True)
class PackageSpec:
    """What differs between recipes. ``package()`` and ``requirements()`` read this.

    ``kind`` is ``stack`` (SLCE + extra manifest + components) or ``app``
    (``.slcp`` / ``.slcw`` projects and the files they reference).

    ``also_require`` lists sibling packages that use the same line-version
    range as ``matter``. ``matter_app_internal`` will set
    ``require_matter=True`` and ``also_require=("matter_internal",)``.
    ``matter_internal`` will set ``require_matter=True`` and
    ``qualities=("internal",)``.
    """

    name: str
    description: str
    kind: str
    required_root_files: tuple[str, ...]
    qualities: tuple[str, ...] = PUBLIC_QUALITIES
    slc_packages: tuple[str, ...] = ("matter",)
    extra_filename: str | None = None
    skip_sample_apps: bool = False
    rewrite_wiseconnect: bool = False
    # Assistant trim_paths rules, "source=>dest". copy_files applies them.
    path_mappings: tuple[str, ...] = ()
    require_dep_versions: bool = False
    require_matter: bool = False
    also_require: tuple[str, ...] = ()


MATTER = PackageSpec(
    name="matter",
    description="Matter extension for Simplicity SDK Suite",
    kind="stack",
    required_root_files=(
        "matter.slsdk",
        "src/app/zap-templates/app-templates.json",
        "src/app/zap-templates/zcl/zcl.json",
    ),
    extra_filename="matter.slce.extra",
    skip_sample_apps=True,
    require_dep_versions=True,
)

MATTER_APP = PackageSpec(
    name="matter_app",
    description="matter sample-app package",
    kind="app",
    required_root_files=(
        "matter_app.slsdk",
        "matter_templates.xml",
    ),
    rewrite_wiseconnect=True,
    path_mappings=(
        "packages/build_app.sh=>build_app.sh",
        "packages/_shared/release_stream_channel=>release_stream_channel",
    ),
    require_matter=True,
)


def spec_of(conanfile) -> PackageSpec:
    """Return the ``PackageSpec`` a recipe declares as ``_spec``, checking its name matches."""
    spec = conanfile._spec
    if spec.name != conanfile.name:
        raise RuntimeError(
            f"{conanfile.name} recipe _spec.name is {spec.name!r}"
        )
    return spec


# ---------------------------------------------------------------------------
# Checkout root and exported recipe files
# ---------------------------------------------------------------------------

def read_package_metadata(name: str, *, recipe_file: str | Path) -> str:
    """Read a one-line file from ``e/_shared`` or ``packages/_shared``."""
    recipe_dir = Path(recipe_file).resolve().parent
    paths = [
        recipe_dir / "_shared" / name,
        recipe_dir.parent / "_shared" / name,
    ]
    for path in paths:
        if path.is_file():
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value
            raise RuntimeError(f"{path} is empty")
    raise FileNotFoundError(
        f"{name} not found under packages/_shared or exported recipe _shared/"
    )


def _checkout_from_recipe_dir(recipe_dir: Path) -> Optional[Path]:
    """Return the checkout when ``recipe_dir`` is ``packages/<name>`` or ``_shared``."""
    if recipe_dir.parent.name != "packages":
        return None
    root = recipe_dir.parent.parent
    if (root / "matter.slce").is_file():
        return root
    return None


def checkout_root(conanfile) -> Path:
    """Checkout root. Fails in the Conan cache, where there is no checkout."""
    recipe_folder = getattr(conanfile, "recipe_folder", None)
    if recipe_folder:
        found = _checkout_from_recipe_dir(Path(recipe_folder))
        if found is not None:
            return found
    raise RuntimeError(
        "Matter checkout not found. Recipes must live in packages/<name>/ "
        "inside a checkout that contains matter.slce."
    )


def packaging_root(conanfile) -> Path:
    """Tree ``package()`` copies from. Source folder after ``layout()``, else checkout."""
    source = getattr(conanfile, "source_folder", None)
    if source and (Path(source) / "matter.slce").is_file():
        return Path(source)
    return checkout_root(conanfile)


def slce_path(conanfile, filename: str = "matter.slce") -> str:
    """Exported ``e/matter.slce`` when present, otherwise the checkout copy."""
    recipe_folder = getattr(conanfile, "recipe_folder", None)
    if recipe_folder:
        exported = Path(recipe_folder) / filename
        if exported.is_file():
            return str(exported)
    return str(checkout_root(conanfile) / filename)


def apply_layout(conanfile) -> None:
    """Point ``export-pkg`` at the checkout. No-op for a cache recipe."""
    recipe_dir = Path(conanfile.recipe_folder)
    if _checkout_from_recipe_dir(recipe_dir) is None:
        return
    conanfile.folders.root = "../.."
    conanfile.folders.source = "."


# ---------------------------------------------------------------------------
# Version and channel
# ---------------------------------------------------------------------------

def set_version(conanfile) -> None:
    """Set ``version`` and ``channel`` when the caller has not set them.

    Version: ``MATTER_PACKAGE_VERSION`` overrides everything. Otherwise a version
    already set on the recipe (``--version``) is kept. If none is set,
    ``get_version`` builds it from ``matter.slce`` plus ``SL_PRERELEASE``.

    Channel comes from ``get_channel`` unless ``MATTER_PACKAGE_CHANNEL`` or
    ``--channel`` is set. ``get_channel`` maps ``main``, ``release/*``, and
    ``sisdk-YYYY.M`` onto ``release_stream_channel``. A ``release_*`` branch
    keeps its own name, so ``build-pkg.sh`` and CI pass the channel explicitly.
    """
    assistant = _assistant(conanfile)
    override = os.environ.get("MATTER_PACKAGE_VERSION", "").strip()
    if override:
        conanfile.version = override
    else:
        conanfile.version = conanfile.version or assistant.get_version(slce_path(conanfile))

    if conanfile.channel:
        return
    channel_override = os.environ.get("MATTER_PACKAGE_CHANNEL", "").strip()
    if channel_override:
        conanfile.channel = channel_override
        return
    conanfile.channel = assistant.get_channel(conanfile)


def _assistant(conanfile):
    """The ``silabs_package_assistant`` module loaded through ``python_requires``."""
    return conanfile.python_requires["silabs_package_assistant"].module


def _path_pairs(spec: PackageSpec) -> list[tuple[str, str]]:
    """Split ``source=>dest`` rules used by ``trim_paths``."""
    pairs = []
    for rule in spec.path_mappings:
        src, dst = rule.split("=>", 1)
        pairs.append((src, dst))
    return pairs


def matter_line_version(conanfile) -> str:
    """X.Y.Z line version of ``matter.slce``, without a prerelease suffix."""
    line = _assistant(conanfile).get_base_version(slce_path(conanfile))
    if not LINE_VERSION_RE.match(line):
        raise RuntimeError(f"matter.slce version must be X.Y.Z, got {line!r}")
    return line


def matter_conan_range(line_version: str) -> str:
    """Conan range for a line version, e.g. ``2.10.0`` -> ``[>=2.10.0 <2.10.1,include_prerelease]``."""
    major, minor, patch = line_version.split(".")
    upper = f"{major}.{minor}.{int(patch) + 1}"
    return f"[>={line_version} <{upper},include_prerelease]"


def apply_requirements(conanfile) -> None:
    """Deps from the YAML, then ``matter`` and any ``also_require`` siblings."""
    spec = spec_of(conanfile)
    channel = conanfile.release_stream_channel
    user = conanfile.user
    if spec.require_dep_versions:
        for dep_name, dep_version in load_dep_versions(conanfile).items():
            conanfile.requires(f"{dep_name}/{dep_version}@{user}/{channel}")
    if not spec.require_matter and not spec.also_require:
        return
    rng = matter_conan_range(matter_line_version(conanfile))
    names = []
    if spec.require_matter:
        names.append("matter")
    names.extend(spec.also_require)
    for dep_name in names:
        conanfile.requires(f"{dep_name}/{rng}@{user}/{channel}")


# ---------------------------------------------------------------------------
# Export into the Conan cache
# ---------------------------------------------------------------------------

def _copy(conanfile, pattern: str, src: str, dst: str) -> None:
    """Copy files matching ``pattern`` from ``src`` to ``dst`` with Conan's ``copy``."""
    from conan.tools.files import copy

    copy(conanfile, pattern, src=src, dst=dst)


def export_recipe_files(conanfile) -> None:
    """Copy the files a cache reload of ``requirements()`` / ``set_version()`` needs."""
    spec = spec_of(conanfile)
    root = checkout_root(conanfile)

    shared_src = Path(conanfile.recipe_folder).parent / "_shared"
    if shared_src.is_dir():
        from conan.tools.files import copy

        copy(
            conanfile,
            "*",
            src=str(shared_src),
            dst=os.path.join(conanfile.export_folder, "_shared"),
            excludes=("__pycache__", "*.pyc", "*.sh"),
        )

    slce_src = root / "matter.slce"
    if slce_src.is_file():
        _copy(conanfile, slce_src.name, str(slce_src.parent), conanfile.export_folder)

    if spec.require_dep_versions:
        for dep_src in _dep_version_candidates(conanfile, root):
            if dep_src.is_file():
                _copy(conanfile, dep_src.name, str(dep_src.parent), conanfile.export_folder)
                break

    if spec.extra_filename:
        extra = Path(conanfile.recipe_folder) / spec.extra_filename
        if extra.is_file():
            _copy(conanfile, extra.name, str(extra.parent), conanfile.export_folder)


def apply_package_info(conanfile) -> None:
    """Expose the package folder to consumers as ``SLC_SDK_PACKAGE_PATH``."""
    conanfile.buildenv_info.append_path("SLC_SDK_PACKAGE_PATH", conanfile.package_folder)


# ---------------------------------------------------------------------------
# Dependency versions
# ---------------------------------------------------------------------------

def _dep_version_candidates(conanfile, root: Optional[Path]) -> list[Path]:
    """Cache copy beside the recipe first, then the checkout's packages/ folder."""
    candidates = []
    recipe_folder = getattr(conanfile, "recipe_folder", None)
    if recipe_folder:
        candidates.append(Path(recipe_folder) / DEP_VERSIONS_FILE)
    if root is not None:
        candidates.append(root / "packages" / DEP_VERSIONS_FILE)
    return candidates


def load_dep_versions(conanfile) -> dict:
    """Flat name -> version map. Cache copy first, then ``packages/``."""
    root = _checkout_from_recipe_dir(Path(conanfile.recipe_folder))
    target = None
    for candidate in _dep_version_candidates(conanfile, root):
        if candidate.is_file():
            target = candidate
            break
    if target is None:
        raise FileNotFoundError(
            f"{DEP_VERSIONS_FILE} not found beside the recipe or under packages/"
        )
    try:
        data = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        raise RuntimeError(f"Failed to parse {target}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"{target} must contain a mapping")
    if any(key in data for key in ("common", "thread", "wifi")):
        merged: dict = {}
        for group in ("common", "thread", "wifi"):
            group_data = data.get(group) or {}
            if not isinstance(group_data, dict):
                raise RuntimeError(f"Dependency group {group!r} in {target} must be a mapping")
            for name, version in group_data.items():
                if version is not None:
                    merged[name] = version
        return merged
    return {key: value for key, value in data.items() if value is not None}


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

def _resolve(root: Path, path: str) -> Path:
    """Absolute paths are returned as-is. Relative paths are joined to ``root``."""
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / path
    return candidate


def _relative(root: Path, path: str) -> str:
    """Path relative to ``root``, or the absolute path if it lies outside ``root``."""
    resolved = _resolve(root, path).resolve()
    try:
        return str(resolved.relative_to(root.resolve()))
    except ValueError:
        return str(resolved)


def _existing_relative(root: Path, files: Iterable[str]) -> set[str]:
    """Keep only entries that are files, as ``root``-relative paths."""
    kept: set[str] = set()
    for file in files:
        resolved = _resolve(root, file)
        if resolved.is_file():
            kept.add(_relative(root, str(resolved)))
    return kept


def _required_present(root: Path, required: tuple[str, ...]) -> set[str]:
    """The entries of ``required`` that exist as files under ``root``."""
    return {name for name in required if (root / name).is_file()}


def _require_root_files(files: set[str], *, root: Path, required: tuple[str, ...], package_name: str) -> None:
    """Raise if a required root file is missing from ``files``. Relative or absolute entries both match."""
    if not required:
        return
    root = root.resolve()
    packaged_rels: set[str] = set()
    packaged_resolved: set[Path] = set()
    for entry in files:
        candidate = Path(entry)
        if not candidate.is_absolute():
            candidate = root / candidate
        try:
            resolved = candidate.resolve()
            packaged_resolved.add(resolved)
            packaged_rels.add(str(resolved.relative_to(root)))
        except (ValueError, OSError):
            packaged_rels.add(str(entry))
    missing = [
        name
        for name in required
        if name not in files
        and name not in packaged_rels
        and (root / name).resolve() not in packaged_resolved
    ]
    if missing:
        raise FileNotFoundError(
            f"{package_name} package is missing required root metadata files: "
            f"{missing}. Ensure they exist under the repo root and are packaged."
        )


def _is_excluded_packaging_path(path: str) -> bool:
    """True when ``path`` is under an SDK tree that ships as its own Conan package."""
    normalized = path.replace("\\", "/").lstrip("./")
    for prefix in EXCLUDED_PATH_PREFIXES:
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return True
        if f"/{prefix}/" in normalized or normalized.endswith("/" + prefix):
            return True
    return False


def _drop_excluded_paths(conanfile, files: set[str]) -> set[str]:
    """Remove excluded SDK trees from a collected file set and log how many were dropped."""
    kept = {path for path in files if not _is_excluded_packaging_path(path)}
    dropped = len(files) - len(kept)
    if dropped:
        conanfile.output.info(
            f"Excluded {dropped} file(s) under {', '.join(EXCLUDED_PATH_PREFIXES)}"
        )
    return kept


def _sample_app_skip_reason(path: str) -> Optional[str]:
    """Why a ``matter.slce.extra`` path belongs to the app package, or None to keep it."""
    normalized = path.replace("\\", "/")
    if _is_excluded_packaging_path(normalized):
        return "separate Conan package (not shipped in matter)"
    if normalized.startswith("slc/apps/"):
        return "sample-app content (owned by the app package)"
    if normalized.endswith((".slcp", ".slcw")):
        return "sample project/workspace (owned by the app package)"
    if normalized.startswith("slc/script/internal/") or normalized == "slc/script/internal":
        return "internal scripts (not packaged)"
    return None


def _extra_candidates(conanfile, root: Path, filename: str) -> list[tuple[Path, str]]:
    """Locations of the extra manifest in priority order: recipe copy, ``packages/<name>/``, repo root.

    Each entry is ``(path, repo-relative name)``.
    """
    candidates: list[tuple[Path, str]] = []
    recipe_folder = getattr(conanfile, "recipe_folder", None)
    if recipe_folder:
        recipe_extra = Path(recipe_folder) / filename
        if recipe_extra.is_file():
            try:
                rel = str(recipe_extra.resolve().relative_to(root.resolve()))
            except ValueError:
                rel = str(recipe_extra)
            candidates.append((recipe_extra, rel))
    packaged = root / "packages" / spec_of(conanfile).name / filename
    if packaged.is_file():
        candidates.append((packaged, str(packaged.relative_to(root.resolve()))))
    at_root = root / filename
    if at_root.is_file():
        candidates.append((at_root, filename))
    return candidates


def _read_stack_extra(conanfile, root: Path) -> tuple[set[str], list[str], list[str]]:
    """Read the extra manifest. Sample-app paths are skipped for the stack package.

    Returns ``(files, git_extra_files, git_path_mapping)``. The git lists feed
    the filter-repo files only.
    """
    spec = spec_of(conanfile)
    empty: tuple[set[str], list[str], list[str]] = (set(), [], [])
    if not spec.extra_filename:
        return empty
    candidates = _extra_candidates(conanfile, root, spec.extra_filename)
    if not candidates:
        conanfile.output.warning(
            f"{spec.extra_filename} not found (looked under the recipe and packages/{spec.name})"
        )
        return empty

    extra_path, descriptor_rel = candidates[0]
    files = {descriptor_rel}
    try:
        data = yaml.safe_load(extra_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        conanfile.output.warning(f"Failed to parse {extra_path}: {exc}")
        return files, [], []

    skipped = 0
    missing = 0
    for path in data.get("extra_files") or []:
        if spec.skip_sample_apps:
            reason = _sample_app_skip_reason(path)
            if reason:
                conanfile.output.info(f"{spec.extra_filename}: skipped {path}: {reason}")
                skipped += 1
                continue
        resolved = _resolve(root, path)
        if resolved.is_file():
            files.add(_relative(root, str(resolved)))
        else:
            conanfile.output.warning(
                f"{spec.extra_filename}: referenced extra file missing and skipped: {path}"
            )
            missing += 1
    conanfile.output.info(
        f"{spec.extra_filename}: skipped {skipped} sample-app path(s), "
        f"{missing} missing path(s); kept {len(files)} file(s)"
    )
    return files, list(data.get("git_extra_files") or []), list(data.get("git_path_mapping") or [])


def _stack_component_files(conanfile, root: Path) -> set[str]:
    """Files ``find_slc_files_to_release`` lists for ``matter.slce``, filtered by quality and package."""
    spec = spec_of(conanfile)
    assistant = _assistant(conanfile)
    slce = root / "matter.slce"
    if not slce.is_file():
        raise FileNotFoundError(f"SLCE file not found: {slce}")
    found = assistant.find_slc_files_to_release(
        slc_sdk_or_extension_def_file=str(slce),
        desired_qualities=list(spec.qualities),
        fail_on_missing_files=False,
        include_slcp=False,
        include_slcc=True,
        desired_packages=list(spec.slc_packages),
    )
    return set(found or [])


def _iter_projects(root: Path):
    """Projects outside ``third_party``.

    ``find_slc_files_to_release`` is not used here. It walks every ``.slcp``
    under the SLCE root, including ``third_party``, and only accepts ``.slcw``
    that sit on a ``component_path``. Sample apps live under ``slc/apps``.
    """
    for slc_file in root.rglob("*.slc*"):
        if "third_party" in slc_file.parts:
            continue
        if slc_file.suffix not in (".slcp", ".slcw"):
            continue
        yield slc_file


def _files_from_assistant_paths(root: Path, paths: Iterable[str]) -> set[str]:
    """Turn assistant output into files under ``root``.

    The assistant can return a directory, so its files are expanded here.
    An entry outside ``root`` raises an error.
    """
    root = root.resolve()
    collected: set[str] = set()
    for entry in paths:
        resolved = Path(entry)
        if not resolved.is_absolute():
            resolved = root / entry
        resolved = resolved.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise FileNotFoundError(f"{entry} is outside the checkout") from exc
        if _is_excluded_packaging_path(_relative(root, str(resolved))):
            continue
        if resolved.is_dir():
            collected.update(str(path) for path in resolved.rglob("*") if path.is_file())
        elif resolved.is_file():
            collected.add(str(resolved))
    return collected


def _app_files(conanfile, root: Path) -> set[str]:
    """Projects whose package and quality match, plus the files the assistant lists.

    ``list_files_in_slc_file`` applies the quality and package filter and expands
    ``file_list`` entries. A path that is a directory (no ``file_list``) is expanded
    here, because the assistant returns the directory itself.
    """
    spec = spec_of(conanfile)
    assistant = _assistant(conanfile)
    collected: set[str] = set()
    for slc_file in _iter_projects(root):
        try:
            related = assistant.list_files_in_slc_file(
                slc_file_path=str(slc_file),
                desired_qualities=list(spec.qualities),
                desired_packages=list(spec.slc_packages),
                fail_on_missing_files=True,
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"{spec.name} packaging is missing a file referenced by {slc_file}. "
                "Initialize third_party/matter_sdk before export-pkg. "
                f"{exc}"
            ) from exc
        except Exception as exc:
            conanfile.output.warning(f"Failed processing {slc_file}: {exc}")
            continue
        if related:
            collected.update(_files_from_assistant_paths(root, related))
    conanfile.output.info(f"Gathered {len(collected)} app files for {spec.name}")
    return collected


@dataclass
class PackagePlan:
    """Repo-relative files to package, and the filter-repo path mappings, for one recipe."""

    files: set[str]
    pathmap: list[str]


def collect_files(conanfile, *, for_filelist: bool) -> PackagePlan:
    """Repo-relative files for ``package()`` or the filter-repo list from ``build()``."""
    spec = spec_of(conanfile)
    root = packaging_root(conanfile)
    files: set[str] = {"License"}
    pathmap: list[str] = []

    if spec.kind == "stack":
        extra_files, git_extra, git_pathmap = _read_stack_extra(conanfile, root)
        files.update(extra_files)
        files.update(_stack_component_files(conanfile, root))
        if for_filelist:
            files.update(_existing_relative(root, git_extra))
            pathmap.extend(git_pathmap)
    elif spec.kind == "app":
        files.update(_app_files(conanfile, root))
    else:
        raise RuntimeError(f"Unknown package kind {spec.kind!r} on {spec.name}")

    files.update(_required_present(root, spec.required_root_files))
    files = _existing_relative(root, files)
    files = _drop_excluded_paths(conanfile, files)
    files.update(_required_present(root, spec.required_root_files))
    _require_root_files(
        files, root=root, required=spec.required_root_files, package_name=spec.name
    )

    if for_filelist:
        for src, dst in _path_pairs(spec):
            if (root / src).is_file():
                files.add(src)
            pathmap.append(f"{src}:{dst}")
    return PackagePlan(files=files, pathmap=pathmap)


def _rewrite_wiseconnect(conanfile, files: set[str]) -> None:
    """Rename the ``wiseconnect3_sdk`` extension id to ``wifi`` in the packaged SLCP and SLCW files."""
    package_root = Path(conanfile.package_folder)
    changed = 0
    for rel in files:
        path = Path(rel)
        if path.is_absolute() or path.suffix not in (".slcp", ".slcw"):
            continue
        slc_file = package_root / path
        text = slc_file.read_text(encoding="utf-8")
        if "wiseconnect3_sdk" not in text:
            continue
        new_text, count = _WISECONNECT_EXTENSION.subn(r"\1wifi\2", text)
        if count:
            slc_file.write_text(new_text, encoding="utf-8")
            changed += count
    conanfile.output.info(f"Mapped {changed} sdk_extension wiseconnect3_sdk id(s) to wifi")


def package_from_spec(conanfile) -> None:
    """Copy the planned files into the package, applying path trimming and the WiseConnect rewrite.

    Writes the package metadata last.
    """
    spec = spec_of(conanfile)
    root = packaging_root(conanfile)
    plan = collect_files(conanfile, for_filelist=False)
    files = set(plan.files)
    for src, _dst in _path_pairs(spec):
        if not (root / src).is_file():
            raise FileNotFoundError(f"missing {root / src}")
        files.add(src)

    assistant = _assistant(conanfile)
    file_list = list(files)
    mapping = None
    if spec.path_mappings:
        trimmed = assistant.trim_paths(file_list, list(spec.path_mappings))
        mapping = dict(zip(file_list, trimmed))
    assistant.copy_files(
        files_to_package=file_list,
        src_folder=str(root),
        dst_folder=os.path.join(conanfile.package_folder, "."),
        trims_mapping=mapping,
    )
    if spec.rewrite_wiseconnect:
        _rewrite_wiseconnect(conanfile, files)

    lock_name = f"conan-{spec.name}.lock"
    if (root / lock_name).is_file():
        _copy(conanfile, lock_name, str(root), os.path.join(conanfile.package_folder, "."))
    assistant.generate_metadata(conanfile, files)


def write_filelists(conanfile) -> None:
    """Write the filter-repo lists. ``build()`` does not compile anything."""
    spec = spec_of(conanfile)
    root = packaging_root(conanfile)
    plan = collect_files(conanfile, for_filelist=True)
    list_path = root / f"{spec.name}-filter-repo-filelist.txt"
    map_path = root / f"{spec.name}-filter-repo-pathmap.txt"
    list_path.write_text("".join(f"{path}\n" for path in sorted(plan.files)), encoding="utf-8")
    map_path.write_text("".join(f"{line}\n" for line in plan.pathmap), encoding="utf-8")
