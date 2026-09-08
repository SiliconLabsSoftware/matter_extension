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
import subprocess
from pathlib import Path
from typing import Iterable, List, Optional


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


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


def slt_install(project_dir: str | Path) -> None:
    """Run `slt install` so platform SDK paths land in autogen/pkg.slconf."""
    project_dir = Path(project_dir)
    pkg_slt = project_dir / "pkg.slt"
    if not pkg_slt.is_file():
        raise FileNotFoundError(
            f"pkg.slt not found in {project_dir}. Package-model builds require pkg.slt."
        )
    logging.info("Running slt install in %s", project_dir)
    subprocess.run(["slt", "install"], cwd=str(project_dir), check=True)


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
