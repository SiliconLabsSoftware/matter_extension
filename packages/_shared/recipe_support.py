"""Shared helpers for Matter Conan recipes.

Recipes stay thin ``ConanFile`` subclasses. This module is not a ``ConanFile``.
``packages/pkgctl.py`` exports every recipe listed in ``packages/packages.yaml``.

File lists, versions, channels, path relocation, and the copy into the package
come from ``silabs_package_assistant`` (``find_slc_files_to_release``,
``list_files_in_slc_file``, ``get_version``, ``get_base_version``,
``get_channel``, ``trim_paths``, ``copy_files``, ``generate_metadata``).

A ``matter_`` name wraps the assistant function of the same suffix and then
applies Matter rules. ``matter_get_version`` calls ``get_version``. The assistant
result is kept; this module only adds the Matter path, filter, or check.

Two Conan contexts matter:

* ``conan export-pkg`` loads ``packages/<name>/conanfile.py`` from the checkout.
  ``layout()`` sets the source folder to the checkout root, and ``package()``
  reads the tree from there.
* A later ``conan install`` loads the copy under the cache ``e/`` folder, which
  is not a git checkout. ``requirements()`` and ``set_version()`` must use files
  copied beside the recipe (``matter.slce``).

Adding ``matter_internal`` / ``matter_app_internal`` later means a new
``conanfile.py`` and one entry in ``packages.yaml``.
Internal content is selected by SLC ``quality: internal``, not by path.

Temp workaround: ``promote_internal_to_experimental`` force-includes listed
``.slcc`` assets into the customer ``matter`` package and rewrites those
packaged ``.slcc`` files from ``quality: internal`` to ``experimental``.
TODO: remove once using internal components with a production ``.slcp``
(``matter_internal`` + ``pkg.slt``) is resolved.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import yaml

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

# TODO: remove with promote_internal_to_experimental once internal+production
# .slcp packaging is resolved.
# Temp: assets for SQA BLE components kept quality:internal in source.
_PROMOTE_INTERNAL_ASSETS = {
    "slc/component/matter-platform/bluetooth/matter_ble_dmp_test_gatt.slcc": (
        "third_party/matter_sdk/examples/platform/silabs/cmp/config/btconf/"
        "gatt_configuration.btconf",
    ),
    "slc/component/matter-platform/bluetooth/matter_internal_ble_side_channel.slcc": (
        "third_party/matter_sdk/src/platform/silabs/efr32/BLEChannelImpl.h",
        "third_party/matter_sdk/src/platform/silabs/efr32/BLEChannelImpl.cpp",
    ),
}

_QUALITY_INTERNAL_LINE = re.compile(r"^([ \t]*quality:[ \t]*)internal[ \t]*$", re.MULTILINE)


# ---------------------------------------------------------------------------
# Checkout root and exported recipe files
# ---------------------------------------------------------------------------

def _checkout_from_recipe_dir(recipe_dir: Path) -> Optional[Path]:
    """Return the git checkout when ``recipe_dir`` is under ``packages/``.

    That is ``packages/<name>`` during ``export-pkg``, or ``packages/_shared``.
    Returns None in the Conan cache, whose parent directory is not ``packages``.
    """
    if recipe_dir.parent.name != "packages":
        return None
    root = recipe_dir.parent.parent
    if (root / "matter.slce").is_file():
        return root
    return None


def checkout_root(conanfile) -> Path:
    """Repo root that contains ``matter.slce``.

    Raises in the Conan cache. A cache recipe must use the files exported
    beside it, not this checkout.
    """
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
    """Tree ``package()`` and ``build()`` read.

    After ``apply_layout`` this is the source folder, which is the checkout.
    Before layout, or when the source folder has no ``matter.slce``, it falls
    back to ``checkout_root``.
    """
    source = getattr(conanfile, "source_folder", None)
    if source and (Path(source) / "matter.slce").is_file():
        return Path(source)
    return checkout_root(conanfile)


def slce_path(conanfile, filename: str = "matter.slce") -> str:
    """Path to ``matter.slce`` for version and dependency-range reads.

    The copy exported next to the recipe (``e/matter.slce``) wins, so a later
    ``conan install`` does not need the git checkout.
    """
    recipe_folder = getattr(conanfile, "recipe_folder", None)
    if recipe_folder:
        exported = Path(recipe_folder) / filename
        if exported.is_file():
            return str(exported)
    return str(checkout_root(conanfile) / filename)


def apply_layout(conanfile) -> None:
    """Point ``conan export-pkg`` at the checkout.

    The recipe lives in ``packages/<name>``, so the Conan root is two levels
    up and the source folder is that root. A recipe already in the cache is
    left unchanged.
    """
    recipe_dir = Path(conanfile.recipe_folder)
    if _checkout_from_recipe_dir(recipe_dir) is None:
        return
    conanfile.folders.root = "../.."
    conanfile.folders.source = "."


# ---------------------------------------------------------------------------
# Version and channel
# ---------------------------------------------------------------------------

def matter_get_version(conanfile) -> str:
    """Conan version for this package.

    Calls ``silabs_package_assistant.get_version`` with ``slce_path``. The
    assistant reads the ``X.Y.Z`` line from ``matter.slce`` and appends the
    ``SL_PRERELEASE`` suffix (``-0.dev`` when that variable is unset).
    """
    return _assistant(conanfile).get_version(slce_path(conanfile))


def set_version(conanfile) -> None:
    """Set ``version`` and ``channel`` when the caller has not set them.

    Version, first match wins: ``MATTER_PACKAGE_VERSION``, then ``--version``,
    then ``matter_get_version``.

    Channel, first match wins: ``--channel`` (already on ``conanfile.channel``),
    then ``MATTER_PACKAGE_CHANNEL``, then ``get_channel``. ``get_channel`` uses
    ``release_stream_channel`` for ``main``, ``release/*``, ``sisdk-YYYY.M``,
    and a detached HEAD. Any other branch becomes the channel, so CI passes
    the channel explicitly.
    """
    assistant = _assistant(conanfile)
    override = os.environ.get("MATTER_PACKAGE_VERSION", "").strip()
    if override:
        conanfile.version = override
    else:
        conanfile.version = conanfile.version or matter_get_version(conanfile)

    if conanfile.channel:
        return
    channel_override = os.environ.get("MATTER_PACKAGE_CHANNEL", "").strip()
    if channel_override:
        conanfile.channel = channel_override
        return
    conanfile.channel = assistant.get_channel(conanfile)


def _assistant(conanfile):
    """The ``silabs_package_assistant`` module from ``python_requires``.

    Recipes declare ``python_requires = "silabs_package_assistant/[~2]@silabs"``.
    Every ``matter_*`` wrapper calls through this.
    """
    return conanfile.python_requires["silabs_package_assistant"].module


def _path_pairs(path_mappings: Iterable[str]) -> list[tuple[str, str]]:
    """Split ``source=>dest`` rules into ``(source, dest)`` pairs.

    ``trim_paths`` consumes the same strings but returns only destinations.
    The pairs are how this module checks that each source file exists and
    adds it to the copy set.
    """
    pairs = []
    for rule in path_mappings:
        src, dst = rule.split("=>", 1)
        pairs.append((src, dst))
    return pairs


# ---------------------------------------------------------------------------
# Export into the Conan cache
# ---------------------------------------------------------------------------

def _copy(conanfile, pattern: str, src: str, dst: str) -> None:
    """Copy files matching ``pattern`` with ``conan.tools.files.copy``.

    Used for export globs and the lock file. The package file list is copied
    by ``copy_files`` instead, which takes explicit paths and a trim map.
    """
    from conan.tools.files import copy

    copy(conanfile, pattern, src=src, dst=dst)


def export_recipe_files(
    conanfile,
    *,
    extra_filename: str | None = None,
) -> None:
    """Copy the files a cache reload of ``requirements()`` and ``set_version()`` needs.

    Copies ``packages/_shared`` and ``matter.slce`` into the export folder.
    ``extra_filename`` copies that manifest from the recipe directory.
    """
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

    if extra_filename:
        extra = Path(conanfile.recipe_folder) / extra_filename
        if extra.is_file():
            _copy(conanfile, extra.name, str(extra.parent), conanfile.export_folder)


def apply_package_info(conanfile) -> None:
    """Publish the package folder to consumers as ``SLC_SDK_PACKAGE_PATH``.

    SLC and the sample-app build scripts locate the installed package through
    this environment variable.
    """
    conanfile.buildenv_info.append_path("SLC_SDK_PACKAGE_PATH", conanfile.package_folder)


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

def _resolve(root: Path, path: str) -> Path:
    """Join ``path`` to ``root``. An absolute path is returned unchanged."""
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / path
    return candidate


def _relative(root: Path, path: str) -> str:
    """``path`` relative to ``root``.

    A file that resolves outside ``root`` keeps its absolute path so the
    caller can still see it.
    """
    resolved = _resolve(root, path).resolve()
    try:
        return str(resolved.relative_to(root.resolve()))
    except ValueError:
        return str(resolved)


def _existing_relative(root: Path, files: Iterable[str]) -> set[str]:
    """Drop entries that are not files. What remains is relative to ``root``."""
    kept: set[str] = set()
    for file in files:
        resolved = _resolve(root, file)
        if resolved.is_file():
            kept.add(_relative(root, str(resolved)))
    return kept


def _required_present(root: Path, required: tuple[str, ...]) -> set[str]:
    """The names in ``required`` that exist as files under ``root``."""
    return {name for name in required if (root / name).is_file()}


def _require_root_files(files: set[str], *, root: Path, required: tuple[str, ...], package_name: str) -> None:
    """Fail the package when a required root file is missing from ``files``.

    A required name matches a relative entry, an absolute entry, or the same
    file reached by either spelling.
    """
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
    """True when ``path`` is under SiSDK, the AWS OTA SDK, or the Wi-Fi SDK.

    Those trees are separate Conan packages. SLC files may point at them;
    this package must not ship them.
    """
    normalized = path.replace("\\", "/").lstrip("./")
    for prefix in EXCLUDED_PATH_PREFIXES:
        if normalized == prefix or normalized.startswith(prefix + "/"):
            return True
        if f"/{prefix}/" in normalized or normalized.endswith("/" + prefix):
            return True
    return False


def _drop_excluded_paths(conanfile, files: set[str]) -> set[str]:
    """Remove ``EXCLUDED_PATH_PREFIXES`` from ``files`` and log the count."""
    kept = {path for path in files if not _is_excluded_packaging_path(path)}
    dropped = len(files) - len(kept)
    if dropped:
        conanfile.output.info(
            f"Excluded {dropped} file(s) under {', '.join(EXCLUDED_PATH_PREFIXES)}"
        )
    return kept


def _sample_app_skip_reason(path: str) -> Optional[str]:
    """Why a stack extra-manifest path is left out, or None to keep it.

    Left out: the separate SDK trees, ``slc/apps``, ``.slcp`` and ``.slcw``
    projects, and ``slc/script/internal``. Those belong to ``matter_app`` or
    are not packaged.
    """
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
    """Places the extra manifest may live. The first hit wins.

    Order: beside the recipe, ``packages/<name>/``, then the repo root.
    Each entry is ``(absolute path, repo-relative name)``.
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
    packaged = root / "packages" / conanfile.name / filename
    if packaged.is_file():
        candidates.append((packaged, str(packaged.relative_to(root.resolve()))))
    at_root = root / filename
    if at_root.is_file():
        candidates.append((at_root, filename))
    return candidates


def _read_stack_extra(
    conanfile, root: Path, *, extra_filename: str | None, skip_sample_apps: bool
) -> tuple[set[str], list[str], list[str]]:
    """Read the stack extra manifest, usually ``matter.slce.extra``.

    ``extra_files`` that exist are returned for the package. When
    ``skip_sample_apps`` is set, paths that belong to the app package are
    logged and dropped. ``git_extra_files`` and ``git_path_mapping`` are
    returned for the filter-repo lists only; ``package()`` ignores them.
    A missing or unreadable manifest is a warning, not a failure.
    """
    empty: tuple[set[str], list[str], list[str]] = (set(), [], [])
    if not extra_filename:
        return empty
    candidates = _extra_candidates(conanfile, root, extra_filename)
    if not candidates:
        conanfile.output.warning(
            f"{extra_filename} not found (looked under the recipe and packages/{conanfile.name})"
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
        if skip_sample_apps:
            reason = _sample_app_skip_reason(path)
            if reason:
                conanfile.output.info(f"{extra_filename}: skipped {path}: {reason}")
                skipped += 1
                continue
        resolved = _resolve(root, path)
        if resolved.is_file():
            files.add(_relative(root, str(resolved)))
        else:
            conanfile.output.warning(
                f"{extra_filename}: referenced extra file missing and skipped: {path}"
            )
            missing += 1
    conanfile.output.info(
        f"{extra_filename}: skipped {skipped} sample-app path(s), "
        f"{missing} missing path(s); kept {len(files)} file(s)"
    )
    return files, list(data.get("git_extra_files") or []), list(data.get("git_path_mapping") or [])


def _matter_find_slc_files_to_release(conanfile, root: Path, qualities: tuple[str, ...]) -> set[str]:
    """Stack files from ``find_slc_files_to_release`` on ``matter.slce``.

    The assistant walks the SLCE ``component_path`` entries. This call limits
    that walk to ``qualities`` and the ``matter`` SLC package, and it skips
    ``.slcp`` files so sample apps stay out of the stack package. Missing
    files are left for the assistant to warn about.
    """
    assistant = _assistant(conanfile)
    slce = root / "matter.slce"
    if not slce.is_file():
        raise FileNotFoundError(f"SLCE file not found: {slce}")
    found = assistant.find_slc_files_to_release(
        slc_sdk_or_extension_def_file=str(slce),
        desired_qualities=list(qualities),
        fail_on_missing_files=False,
        include_slcp=False,
        include_slcc=True,
        desired_packages=["matter"],
    )
    return set(found or [])


def _iter_projects(root: Path):
    """``.slcp`` and ``.slcw`` projects outside ``third_party``.

    This replaces the assistant's own crawl. ``find_slc_files_to_release``
    walks every ``.slcp`` under the SLCE root, including ``third_party``, and
    only accepts a ``.slcw`` that sits on a ``component_path``. Sample apps
    live under ``slc/apps``. Each project found here is still passed to
    ``list_files_in_slc_file``.
    """
    for slc_file in root.rglob("*.slc*"):
        if "third_party" in slc_file.parts:
            continue
        if slc_file.suffix not in (".slcp", ".slcw"):
            continue
        yield slc_file


def _files_from_assistant_paths(root: Path, paths: Iterable[str]) -> set[str]:
    """Turn assistant paths into files that live under ``root``.

    ``list_files_in_slc_file`` returns a directory when an SLC path has no
    ``file_list``; that directory is expanded here. A path outside the
    checkout raises. Paths under the separate SDK trees are dropped.
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


def _matter_list_files_in_slc_file(conanfile, root: Path, qualities: tuple[str, ...]) -> set[str]:
    """Files for the sample-app package.

    ``_iter_projects`` chooses the projects. Each one is passed to
    ``list_files_in_slc_file`` with ``qualities`` and the ``matter`` package,
    which applies the SLC filter and expands ``file_list`` entries.
    ``_files_from_assistant_paths`` then expands any directory the assistant
    returned. A missing referenced file fails the package. Any other error
    is logged and that project is skipped.
    """
    assistant = _assistant(conanfile)
    collected: set[str] = set()
    for slc_file in _iter_projects(root):
        try:
            related = assistant.list_files_in_slc_file(
                slc_file_path=str(slc_file),
                desired_qualities=list(qualities),
                desired_packages=["matter"],
                fail_on_missing_files=True,
            )
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"{conanfile.name} packaging is missing a file referenced by {slc_file}. "
                "Initialize third_party/matter_sdk before export-pkg. "
                f"{exc}"
            ) from exc
        except Exception as exc:
            conanfile.output.warning(f"Failed processing {slc_file}: {exc}")
            continue
        if related:
            collected.update(_files_from_assistant_paths(root, related))
    conanfile.output.info(f"Gathered {len(collected)} app files for {conanfile.name}")
    return collected


@dataclass
class PackagePlan:
    """Repo-relative files for one recipe, plus its filter-repo path mappings."""

    files: set[str]
    pathmap: list[str]


def _files_for_promoted_internal(
    root: Path, promote_internal_to_experimental: tuple[str, ...]
) -> set[str]:
    """Force-include temp-promoted ``.slcc`` paths and their known assets."""
    collected: set[str] = set()
    for slcc in promote_internal_to_experimental:
        collected.add(slcc)
        for asset in _PROMOTE_INTERNAL_ASSETS.get(slcc, ()):
            collected.add(asset)
    return _existing_relative(root, collected)


def collect_files(
    conanfile,
    *,
    for_filelist: bool,
    kind: str,
    required_root_files: tuple[str, ...],
    extra_filename: str | None,
    skip_sample_apps: bool,
    path_mappings: tuple[str, ...],
    qualities: tuple[str, ...],
    promote_internal_to_experimental: tuple[str, ...] = (),
) -> PackagePlan:
    """Repo-relative files for ``package()``, or the filter-repo list from ``build()``.

    ``kind="stack"`` takes the extra manifest plus ``find_slc_files_to_release``.
    ``kind="app"`` takes the sample-app projects. ``License`` and
    ``required_root_files`` are always included. Excluded SDK trees are
    removed, then the required files are added back and checked so a required
    file cannot be dropped. ``for_filelist`` also keeps the git extra files
    and records ``source:dest`` path mappings.
    """
    root = packaging_root(conanfile)
    files: set[str] = {"License"}
    pathmap: list[str] = []

    if kind == "stack":
        extra_files, git_extra, git_pathmap = _read_stack_extra(
            conanfile,
            root,
            extra_filename=extra_filename,
            skip_sample_apps=skip_sample_apps,
        )
        files.update(extra_files)
        files.update(_matter_find_slc_files_to_release(conanfile, root, qualities))
        if for_filelist:
            files.update(_existing_relative(root, git_extra))
            pathmap.extend(git_pathmap)
    elif kind == "app":
        files.update(_matter_list_files_in_slc_file(conanfile, root, qualities))
    else:
        raise RuntimeError(f"Unknown package kind {kind!r} on {conanfile.name}")

    if promote_internal_to_experimental:
        files.update(
            _files_for_promoted_internal(root, promote_internal_to_experimental)
        )

    files.update(_required_present(root, required_root_files))
    files = _existing_relative(root, files)
    files = _drop_excluded_paths(conanfile, files)
    files.update(_required_present(root, required_root_files))
    _require_root_files(
        files, root=root, required=required_root_files, package_name=conanfile.name
    )

    if for_filelist:
        for src, dst in _path_pairs(path_mappings):
            if (root / src).is_file():
                files.add(src)
            pathmap.append(f"{src}:{dst}")
    return PackagePlan(files=files, pathmap=pathmap)


def _rewrite_wiseconnect(conanfile, files: set[str]) -> None:
    """Rename the ``wiseconnect3_sdk`` sdk_extension id to ``wifi``.

    Runs on the already copied ``.slcp`` and ``.slcw`` files. A component
    line ``- id: wifi`` has no version and is left unchanged.
    """
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


def _rewrite_quality_to_experimental(
    conanfile, promote_internal_to_experimental: tuple[str, ...]
) -> None:
    """Temp: rewrite packaged ``.slcc`` quality from internal to experimental."""
    package_root = Path(conanfile.package_folder)
    changed = 0
    for rel in promote_internal_to_experimental:
        slc_file = package_root / rel
        if not slc_file.is_file():
            conanfile.output.warning(
                f"Temp promote: packaged .slcc missing, skip quality rewrite: {rel}"
            )
            continue
        text = slc_file.read_text(encoding="utf-8")
        new_text, count = _QUALITY_INTERNAL_LINE.subn(r"\1experimental", text)
        if count:
            slc_file.write_text(new_text, encoding="utf-8")
            changed += count
    conanfile.output.info(
        f"Temp: rewrote quality internal->experimental in {changed} packaged .slcc"
    )


def matter_package_files(
    conanfile,
    *,
    kind: str,
    required_root_files: tuple[str, ...],
    extra_filename: str | None = None,
    skip_sample_apps: bool = False,
    path_mappings: tuple[str, ...] = (),
    rewrite_wiseconnect: bool = False,
    qualities: tuple[str, ...],
    promote_internal_to_experimental: tuple[str, ...] = (),
) -> None:
    """Build the Conan package for one recipe.

    ``collect_files`` chooses the files. ``trim_paths`` relocates paths that
    match ``path_mappings``, and ``copy_files`` writes them into the package
    folder. After the copy, the WiseConnect rewrite runs when requested and
    ``conan-<name>.lock`` is copied when it exists. ``generate_metadata``
    runs last, on the final file list.
    """
    root = packaging_root(conanfile)
    plan = collect_files(
        conanfile,
        for_filelist=False,
        kind=kind,
        required_root_files=required_root_files,
        extra_filename=extra_filename,
        skip_sample_apps=skip_sample_apps,
        path_mappings=path_mappings,
        qualities=qualities,
        promote_internal_to_experimental=promote_internal_to_experimental,
    )
    files = set(plan.files)
    for src, _dst in _path_pairs(path_mappings):
        if not (root / src).is_file():
            raise FileNotFoundError(f"missing {root / src}")
        files.add(src)

    assistant = _assistant(conanfile)
    file_list = list(files)
    mapping = None
    if path_mappings:
        trimmed = assistant.trim_paths(file_list, list(path_mappings))
        mapping = dict(zip(file_list, trimmed))
    assistant.copy_files(
        files_to_package=file_list,
        src_folder=str(root),
        dst_folder=os.path.join(conanfile.package_folder, "."),
        trims_mapping=mapping,
    )
    if rewrite_wiseconnect:
        _rewrite_wiseconnect(conanfile, files)
    if promote_internal_to_experimental:
        _rewrite_quality_to_experimental(conanfile, promote_internal_to_experimental)

    lock_name = f"conan-{conanfile.name}.lock"
    if (root / lock_name).is_file():
        _copy(conanfile, lock_name, str(root), os.path.join(conanfile.package_folder, "."))
    assistant.generate_metadata(conanfile, files)


def write_filelists(
    conanfile,
    *,
    kind: str,
    required_root_files: tuple[str, ...],
    extra_filename: str | None = None,
    skip_sample_apps: bool = False,
    path_mappings: tuple[str, ...] = (),
    qualities: tuple[str, ...],
    promote_internal_to_experimental: tuple[str, ...] = (),
) -> None:
    """Write the filter-repo lists at the checkout root.

    ``<name>-filter-repo-filelist.txt`` is the sorted file list.
    ``<name>-filter-repo-pathmap.txt`` is the ``source:dest`` mappings.
    ``build()`` calls this and does not compile anything.
    """
    root = packaging_root(conanfile)
    plan = collect_files(
        conanfile,
        for_filelist=True,
        kind=kind,
        required_root_files=required_root_files,
        extra_filename=extra_filename,
        skip_sample_apps=skip_sample_apps,
        path_mappings=path_mappings,
        qualities=qualities,
        promote_internal_to_experimental=promote_internal_to_experimental,
    )
    list_path = root / f"{conanfile.name}-filter-repo-filelist.txt"
    map_path = root / f"{conanfile.name}-filter-repo-pathmap.txt"
    list_path.write_text("".join(f"{path}\n" for path in sorted(plan.files)), encoding="utf-8")
    map_path.write_text("".join(f"{line}\n" for line in plan.pathmap), encoding="utf-8")
