#!/usr/bin/env python3
"""Helpers for Matter package-manager (SLT/Conan) build flows.

Repo-dev package model (matches slc/build.sh):
  1. Run `slt install` in the app directory (uses pkg.slt).
  2. Prepend the local Matter checkout into autogen/pkg.slconf.
  3. Run `slc generate` without CLI --sdk-package-path for platform SDKs.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, List, Optional


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_slt_executable() -> str:
    """Locate the SLT CLI (env, PATH, or slc/tools fallback)."""
    candidates = [
        os.environ.get("SLT_EXECUTABLE", "").strip(),
        shutil.which("slt") or "",
        str(repo_root_from_here() / "slc" / "tools" / ("slt.exe" if os.name == "nt" else "slt")),
    ]
    for candidate in candidates:
        if candidate and (os.path.isfile(candidate) or shutil.which(candidate)):
            return candidate
    raise FileNotFoundError(
        "slt not found. Run slc/sl_setup_env.py (installs slc/tools/slt) "
        "or add slt to PATH / set SLT_EXECUTABLE."
    )


def read_matter_package_version(root: Optional[Path] = None) -> str:
    """Read slc/script/matter_package_version (single source of truth)."""
    root = root or repo_root_from_here()
    version_file = root / "slc" / "script" / "matter_package_version"
    try:
        version = version_file.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise FileNotFoundError(f"Missing package version file: {version_file}") from exc
    if not version:
        raise ValueError(f"Empty package version file: {version_file}")
    return version


def use_package_model(force: Optional[bool] = None) -> bool:
    """Return True when builds should use SLT packages instead of third_party SDK trees.

    Priority:
      1. Explicit force argument
      2. USE_PACKAGE / USE_SUBMODULES environment variables
      3. Default True (package model)
    """
    if force is not None:
        return force
    if _env_truthy("USE_SUBMODULES"):
        return False
    if "USE_PACKAGE" in os.environ:
        return _env_truthy("USE_PACKAGE")
    return True


def _env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def ensure_conan_home() -> str:
    """Return absolute CONAN_HOME, defaulting to the SLT Conan install tree."""
    home = os.environ.get("CONAN_HOME", "").strip()
    if not home:
        home = str(Path.home() / ".silabs" / "slt" / "installs" / "conan")
    home = os.path.expanduser(home)
    os.environ["CONAN_HOME"] = home
    return home


def resolve_conan_executable() -> str:
    """Locate the Conan CLI (env, PATH, or SLT engine install)."""
    slt_home = Path(os.environ.get("SLT_HOME", Path.home() / ".silabs" / "slt")).expanduser()
    engine = slt_home / "engines" / "conan" / "conan" / ("conan.exe" if os.name == "nt" else "conan")
    candidates = [
        os.environ.get("CONAN_EXECUTABLE", "").strip(),
        shutil.which("conan") or "",
        str(engine),
    ]
    for candidate in candidates:
        if candidate and (os.path.isfile(candidate) or shutil.which(candidate)):
            return candidate
    raise FileNotFoundError(
        "conan not found. Run slc/sl_setup_env.py (slt install conan) "
        "or add conan to PATH / set CONAN_EXECUTABLE."
    )


DEFAULT_CONAN_PRERELEASE_REMOTE = "https://conan-prerelease.silabs.net/"


def configure_conan_remotes(
    root: Optional[Path] = None,
    *,
    conan: Optional[str] = None,
    prerelease_url: str = DEFAULT_CONAN_PRERELEASE_REMOTE,
) -> None:
    """Apply packages/ remotes and ensure the Silabs prerelease remote exists."""
    root = root or repo_root_from_here()
    conan_exe = conan or resolve_conan_executable()
    packages_dir = root / "packages"
    if packages_dir.is_dir():
        logging.info("Configuring Conan remotes from %s", packages_dir)
        subprocess.run(
            [conan_exe, "config", "install", str(packages_dir)],
            check=True,
        )
    if prerelease_url:
        logging.info("Ensuring Conan remote conan-prerelease=%s", prerelease_url)
        subprocess.run(
            [conan_exe, "remote", "add", "-f", "conan-prerelease", prerelease_url],
            check=True,
        )


def export_matter_packages(
    version: str,
    root: Optional[Path] = None,
    *,
    conan: Optional[str] = None,
) -> None:
    """Export local matter and matter_app recipes into the Conan cache."""
    root = root or repo_root_from_here()
    conan_exe = conan or resolve_conan_executable()
    os.environ["MATTER_PACKAGE_VERSION"] = version
    ensure_conan_home()

    for name in ("matter", "matter_app"):
        recipe = root / "packages" / name / "conanfile.py"
        if not recipe.is_file():
            raise FileNotFoundError(f"Missing Conan recipe: {recipe}")
        # Best-effort cleanup so re-exports replace prior content.
        subprocess.run(
            [conan_exe, "remove", f"{name}/{version}@silabs", "-c"],
            check=False,
        )
        logging.info("Exporting %s/%s@silabs from %s", name, version, recipe)
        subprocess.run(
            [
                conan_exe,
                "export-pkg",
                str(recipe),
                f"--name={name}",
                f"--version={version}",
                "--user=silabs",
            ],
            check=True,
            cwd=str(root),
        )


def install_matter_app_package(
    version: str,
    *,
    slt: Optional[str] = None,
) -> None:
    """Install matter_app (and transitive matter / platform deps) via SLT."""
    slt_exe = slt or resolve_slt_executable()
    ref = f"matter_app/{version}@silabs"
    os.environ["MATTER_PACKAGE_VERSION"] = version
    ensure_conan_home()
    logging.info("Installing %s via SLT", ref)
    subprocess.run([slt_exe, "install", ref, "-e", "conan"], check=True)


def ensure_local_matter_packages(
    root: Optional[Path] = None,
    version: Optional[str] = None,
    *,
    slt: Optional[str] = None,
    conan: Optional[str] = None,
) -> str:
    """Export local matter/matter_app packages then install matter_app via SLT.

    Mirrors slc/build-pkg.sh --create-package-version for package-model setup.
    Returns the package version used.
    """
    root = Path(root) if root else repo_root_from_here()
    version = (
        version
        or os.environ.get("MATTER_PACKAGE_VERSION", "").strip()
        or read_matter_package_version(root)
    ).strip()
    if not version:
        raise ValueError("MATTER_PACKAGE_VERSION is empty")

    ensure_conan_home()
    os.environ["MATTER_PACKAGE_VERSION"] = version
    conan_exe = conan or resolve_conan_executable()
    slt_exe = slt or resolve_slt_executable()

    configure_conan_remotes(root, conan=conan_exe)
    export_matter_packages(version, root=root, conan=conan_exe)
    install_matter_app_package(version, slt=slt_exe)
    logging.info("Local Matter packages ready: matter_app/%s@silabs", version)
    return version


def slt_install(project_dir: str | Path) -> None:
    """Run `slt install` so platform SDK paths land in autogen/pkg.slconf."""
    project_dir = Path(project_dir)
    pkg_slt = project_dir / "pkg.slt"
    if not pkg_slt.is_file():
        raise FileNotFoundError(
            f"pkg.slt not found in {project_dir}. Package-model builds require pkg.slt."
        )
    slt = resolve_slt_executable()
    logging.info("Running slt install in %s", project_dir)
    subprocess.run([slt, "install"], cwd=str(project_dir), check=True)


def prepend_matter_root_to_slconf(project_dir: str | Path, matter_root: str | Path) -> None:
    """Prepend the local Matter checkout into sdk-package-path in pkg.slconf."""
    project_dir = Path(project_dir)
    matter_root = str(Path(matter_root).resolve())
    slconf = project_dir / "autogen" / "pkg.slconf"
    if not slconf.is_file():
        raise FileNotFoundError(f"missing {slconf} after slt install")

    text = slconf.read_text(encoding="utf-8")
    needle = "sdk-package-path = [\n"
    if needle not in text:
        raise RuntimeError(f"sdk-package-path not found in {slconf}")
    if f'"{matter_root}"' in text:
        return

    insertion = f'  "{matter_root}",    # local sdk path\n'
    slconf.write_text(text.replace(needle, needle + insertion, 1), encoding="utf-8")
    logging.info("Prepended Matter root into %s", slconf)


def prepare_package_generate(project_dir: str | Path, matter_root: str | Path) -> None:
    """Install SLT deps and inject the local Matter tree for generate."""
    ensure_conan_home()
    slt_install(project_dir)
    prepend_matter_root_to_slconf(project_dir, matter_root)


def sdk_package_path_args(
    sisdk_root: Optional[str],
    wiseconnect_root: Optional[str],
    matter_root: str,
    *,
    use_package: Optional[bool] = None,
) -> List[str]:
    """Build optional --sdk-package-path args.

    Package model relies on pkg.slconf (no CLI platform paths).
    Submodule model passes third_party SiSDK / Wi-Fi / Matter roots.
    """
    if use_package_model(use_package):
        return []

    missing = [name for name, path in (
        ("SISDK_ROOT", sisdk_root),
        ("WISECONNECT_ROOT", wiseconnect_root),
        ("silabs_chip_root", matter_root),
    ) if not path]
    if missing:
        raise ValueError(
            "Submodule build requires " + ", ".join(missing) +
            ". Run slc/sl_setup_env.py or enable package model (USE_PACKAGE=1)."
        )

    args: List[str] = []
    for path in (sisdk_root, wiseconnect_root, matter_root):
        args.extend(["--sdk-package-path", path])
    return args


def submodule_sync_paths(*, use_package: Optional[bool] = None) -> Iterable[str]:
    """Submodules to sync for the selected build model."""
    matter_deps = (
        "third_party/matter_sdk",
        "third_party/matter_support",
        "third_party/mbedtls",
        "third_party/QR-Code-generator",
        "third_party/nlio",
        "third_party/nlassert",
    )
    if use_package_model(use_package):
        return matter_deps
    return matter_deps + (
        "third_party/simplicity_sdk",
        "third_party/wifi_sdk",
    )
