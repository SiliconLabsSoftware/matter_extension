#!/usr/bin/env python3
"""Shared helpers for SLT/Conan stack setup and local package export."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

MATTER_SUBMODULES = [
    "third_party/matter_support",
    "third_party/QR-Code-generator",
    "third_party/third_party_hw_drivers_extension",
    "third_party/matter_sdk",
]

MATTER_SDK_NESTED_SUBMODULES = (
    "third_party/nlio/repo",
    "third_party/nlassert/repo",
    "third_party/mbedtls/repo",
)

FORBIDDEN_SDK_PATHS = (
    "third_party/simplicity_sdk",
    "third_party/wifi_sdk",
)

from script.matter_slconf import (  # noqa: E402
    SLC_SDK_PATH_DENYLIST,
    THREAD_EXCLUDE_PACKAGES,
    WIFI_NCP_ONLY_PACKAGES,
    WIFI_SOC_EXCLUDE_PACKAGES,
    detect_app_stack_type,
    exclude_packages_for_app_type,
    filter_slc_sdk_paths,
    parse_pkg_slconf,
    parse_pkg_slconf_sdk_paths,
    parse_slconf_path_comment_package,
    path_is_slc_extension_root,
    slconf_sdk_path_lines,
    write_filtered_app_slconf,
)

# Legacy .env aliases for scripts that still read a single MCU / Wi-Fi root.
PLATFORM_ROOT_KEY = "SISDK_ROOT"
WIFI_PLATFORM_ROOT_KEY = "WISECONNECT_ROOT"


def repo_root_from_script(script_file: str | Path) -> Path:
    return Path(script_file).resolve().parents[2]


def default_matter_sdk_source_root(repo_root: Path) -> Path:
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
        "matter_sdk sources not found. Set MATTER_SDK_SOURCE_ROOT to a matter_sdk clone."
    )


def resolve_matter_package_version(repo_root: Path) -> str:
    slce_path = repo_root / "matter.slce"
    if not slce_path.exists():
        raise FileNotFoundError(f"SLCE file not found: {slce_path}")
    with slce_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    version = str(data.get("version", "")).strip()
    if not version:
        raise RuntimeError(f"Version field missing or empty in {slce_path}")
    return version


def resolve_conan_exe() -> str:
    env_exe = os.environ.get("CONAN_EXE")
    if env_exe and Path(env_exe).is_file():
        return env_exe

    slt_conan = Path.home() / ".silabs/slt/engines/conan/conan/conan"
    if slt_conan.is_file():
        return str(slt_conan)

    from shutil import which

    path_conan = which("conan")
    if path_conan:
        return path_conan

    raise RuntimeError(
        "Conan executable not found. Install SLT (slt update --self) or set CONAN_EXE."
    )


def configure_conan_remotes(repo_root: Path, conan_exe: Optional[str] = None) -> None:
    packages_dir = repo_root / "packages"
    if not packages_dir.is_dir():
        raise FileNotFoundError(f"Packages directory not found: {packages_dir}")

    conan = conan_exe or resolve_conan_exe()
    conan_home = os.path.expanduser("~/.silabs/slt/installs/conan")
    os.environ["CONAN_HOME"] = conan_home
    logger.info("Configuring Conan remotes (CONAN_HOME=%s)", conan_home)

    result = subprocess.run(
        [conan, "config", "install", str(packages_dir)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to configure Conan remotes: {result.stderr or result.stdout}"
        )


def parse_slt_where_output(stdout: str) -> Optional[str]:
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("/"):
            return line
        q_idx = line.rfind("?")
        if q_idx != -1:
            after = line[q_idx + 1 :].lstrip()
            if after.startswith("/"):
                return after
    return None


def slt_where(slt_exe: str, package: str) -> Optional[str]:
    try:
        result = subprocess.run(
            [slt_exe, "where", "--non-interactive", package],
            capture_output=True,
            text=True,
            check=False,
        )
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logger.error("Failed to run 'slt where %s': %s", package, e)
        return None
    if result.returncode != 0:
        return None
    return parse_slt_where_output(result.stdout)


def slt_install_qualified(slt_exe: str, qualified: str) -> None:
    logger.info("Installing %s via SLT", qualified)
    subprocess.run(
        [slt_exe, "install", qualified, "--non-interactive"],
        check=True,
    )


def slt_install_pkg_slt(slt_exe: str, pkg_slt_path: str | Path) -> None:
    pkg_slt_path = Path(pkg_slt_path)
    if not pkg_slt_path.is_file():
        raise FileNotFoundError(f"pkg.slt not found: {pkg_slt_path}")
    logger.info("Installing from %s", pkg_slt_path)
    subprocess.run(
        [slt_exe, "install", "-f", str(pkg_slt_path), "--non-interactive"],
        check=True,
    )


def export_local_packages(
    repo_root: Path,
    version: Optional[str] = None,
    conan_exe: Optional[str] = None,
    matter_sdk_source_root: Optional[Path] = None,
) -> str:
    """Export matter and matter_app to the local Conan cache (2-package model)."""
    conan = conan_exe or resolve_conan_exe()
    pkg_version = version or resolve_matter_package_version(repo_root)
    sdk_root = matter_sdk_source_root or default_matter_sdk_source_root(repo_root)
    os.environ["MATTER_SDK_SOURCE_ROOT"] = str(sdk_root)
    os.environ["MATTER_PACKAGE_VERSION"] = pkg_version
    os.chdir(repo_root)

    exports = (
        ("matter", "packages/matter/conanfile.py"),
        ("matter_app", "packages/matter_app/conanfile.py"),
    )
    for name, conanfile in exports:
        logger.info("Exporting %s/%s@silabs", name, pkg_version)
        subprocess.run(
            [
                conan,
                "export-pkg",
                conanfile,
                f"--name={name}",
                f"--version={pkg_version}",
            ],
            check=True,
            cwd=repo_root,
        )
    return pkg_version


def _technology_where_spec(name: str, version: str) -> str:
    if version.startswith("[") or ">=" in version:
        return name
    return f"{name}/{version}"


def resolve_technology_paths(
    slt_exe: str,
    dep_versions: dict[str, str],
) -> dict[str, str]:
    """Resolve installed technology package install paths keyed by Conan name."""
    paths: dict[str, str] = {}
    missing: list[str] = []

    for name, version in dep_versions.items():
        spec = _technology_where_spec(name, version)
        path = slt_where(slt_exe, spec) or slt_where(slt_exe, name)
        if path and os.path.isdir(path):
            paths[name] = path
            logger.info("Technology %s -> %s", name, path)
        else:
            missing.append(f"{name} ({version})")

    if missing:
        raise RuntimeError(
            "Technology package(s) not found after slt install: "
            + ", ".join(missing)
            + ". Run: ./slc/script/refresh_local_packages.sh"
        )
    return paths


def technology_paths_ordered(
    slt_exe: str,
    dep_versions: dict[str, str],
) -> list[str]:
    """Return technology install paths in dependency declaration order."""
    resolved = resolve_technology_paths(slt_exe, dep_versions)
    return [resolved[name] for name in dep_versions if name in resolved]


def resolve_stack_roots(
    slt_exe: str,
    dep_versions: dict[str, str],
) -> dict[str, str]:
    """Resolve stack paths for .env (legacy single-root keys + full technology list)."""
    tech_paths = resolve_technology_paths(slt_exe, dep_versions)
    platform_root = (
        tech_paths.get("platform")
        or slt_where(slt_exe, "platform")
        or tech_paths.get("platform_efr32xg2b", "")
    )
    wifi_root = tech_paths.get("platform_siwx91x") or tech_paths.get("wifi", "")

    if not platform_root:
        raise RuntimeError(
            "No platform technology package found after slt install. "
            "Ensure dependency_versions.yaml declares stack packages that pull platform."
        )

    roots = {
        PLATFORM_ROOT_KEY: platform_root,
        "STACK_SDK_PATHS": os.pathsep.join(tech_paths.values()),
        "TECHNOLOGY_PATHS_JSON": json.dumps(tech_paths),
    }
    if wifi_root:
        roots[WIFI_PLATFORM_ROOT_KEY] = wifi_root
    else:
        roots[WIFI_PLATFORM_ROOT_KEY] = ""
    return roots


def sdk_package_paths_for_build(
    repo_root: Path,
    slt_exe: str,
    *,
    matter_pkg: Optional[str] = None,
    slconf_path: Optional[Path] = None,
    app_type: str = "unified",
) -> list[str]:
    """Build ordered --sdk-package-path roots for slc generate."""
    from script.stack_deps import load_flattened_stack_deps

    candidates: list[str] = []
    path_lines: dict[str, str] = {}

    slconf = slconf_path or (repo_root / "packages" / "matter" / "autogen" / "pkg.slconf")
    if slconf.is_file():
        candidates.extend(parse_pkg_slconf_sdk_paths(slconf))
        path_lines = slconf_sdk_path_lines(slconf)

    if not candidates:
        dep_versions = load_flattened_stack_deps(repo_root)
        candidates.extend(technology_paths_ordered(slt_exe, dep_versions))

    if matter_pkg and matter_pkg not in candidates:
        candidates.append(matter_pkg)

    filtered = filter_slc_sdk_paths(
        candidates,
        app_type=app_type,
        raw_slconf_lines=path_lines or None,
    )

    base_sdk: Optional[str] = None
    if slt_exe:
        base_sdk = slt_where(slt_exe, "base_sdk")
        if base_sdk and base_sdk not in filtered and path_is_slc_extension_root(base_sdk):
            filtered.insert(0, base_sdk)

    if matter_pkg and matter_pkg not in filtered and path_is_slc_extension_root(matter_pkg):
        if base_sdk and matter_pkg != base_sdk:
            insert_at = 1 if filtered and filtered[0] == base_sdk else 0
            filtered.insert(insert_at, matter_pkg)
        else:
            filtered.insert(0, matter_pkg)

    return filtered


def sync_matter_sdk_nested_submodules(sdk_root: Path) -> None:
    """Init nlio, nlassert, and mbedtls inside a matter_sdk tree (no --recursive)."""
    sdk_root = sdk_root.resolve()
    if not (sdk_root / "src").is_dir():
        raise FileNotFoundError(f"matter_sdk root not found: {sdk_root}")
    logger.info("Initializing matter_sdk nested submodules under %s", sdk_root)
    for nested in MATTER_SDK_NESTED_SUBMODULES:
        subprocess.run(
            ["git", "submodule", "update", "--init", nested],
            check=True,
            cwd=sdk_root,
        )


def sync_matter_submodules(repo_root: Path) -> None:
    logger.info("Initializing Matter extension submodules")
    for subpath in MATTER_SUBMODULES:
        subprocess.run(
            ["git", "submodule", "update", "--init", subpath],
            check=True,
            cwd=repo_root,
        )
    sync_matter_sdk_nested_submodules(default_matter_sdk_source_root(repo_root))


def assert_no_legacy_sdk_paths(repo_root: Path) -> None:
    for rel in FORBIDDEN_SDK_PATHS:
        path = repo_root / rel
        if path.exists():
            raise RuntimeError(
                f"Legacy SDK path must not exist: {path}. "
                "Remove it; stack SDKs come from SLT/Conan only."
            )


def run_generate_pkg_slt(repo_root: Path, verbose: bool = False) -> None:
    script = repo_root / "slc" / "script" / "generate_pkg_slt.py"
    cmd = [sys.executable, str(script), "-d", "slc"]
    if verbose:
        cmd.append("--verbose")
    subprocess.run(cmd, check=True, cwd=repo_root)


def load_dotenv_if_present(repo_root: Path) -> None:
    env_path = repo_root / "slc" / "tools" / ".env"
    if not env_path.is_file():
        return
    with env_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())


def require_platform_root(repo_root: Optional[Path] = None) -> str:
    if repo_root:
        load_dotenv_if_present(repo_root)
    platform_root = os.environ.get(PLATFORM_ROOT_KEY, "").strip()
    if not platform_root or not os.path.isdir(platform_root):
        raise RuntimeError(
            f"{PLATFORM_ROOT_KEY} is not set or invalid. "
            "Run: python3 slc/sl_setup_env.py && source slc/tools/.env"
        )
    return platform_root


def require_sisdk_root(repo_root: Optional[Path] = None) -> str:
    """Backward-compatible alias for require_platform_root."""
    return require_platform_root(repo_root)


def trust_stack_sdk(slc_exe: str, platform_root: str) -> None:
    data_dir = os.path.join(platform_root, "out", "dmp_uc.data")
    os.makedirs(os.path.dirname(data_dir), exist_ok=True)
    subprocess.run(
        [slc_exe, "configuration", "--sdk", platform_root, "-data", data_dir],
        check=True,
    )
    subprocess.run(
        [slc_exe, "signature", "trust", "--sdk", platform_root],
        check=True,
    )


def trust_simplicity_sdk(slc_exe: str, sisdk_root: str) -> None:
    """Backward-compatible alias for trust_stack_sdk."""
    trust_stack_sdk(slc_exe, sisdk_root)


def _cli_print_sdk_paths(slt_exe: str, repo_root: Path, app_dir: Optional[str] = None) -> int:
    matter_pkg = slt_where(slt_exe, "matter")
    slconf_path = None
    app_type = "unified"
    if app_dir:
        app_path = Path(app_dir).resolve()
        slc_sdk = app_path / "autogen" / "slc-sdk.slconf"
        if slc_sdk.is_file():
            slconf_path = slc_sdk
        else:
            slconf_path = app_path / "autogen" / "pkg.slconf"
        app_type = detect_app_stack_type(app_path)
    try:
        paths = sdk_package_paths_for_build(
            repo_root,
            slt_exe,
            matter_pkg=matter_pkg,
            slconf_path=slconf_path,
            app_type=app_type,
        )
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1
    for path in paths:
        print(f"--sdk-package-path\t{path}")
    return 0


def _cli_write_app_slconf(app_dir: str, slcp_name: str = "") -> int:
    try:
        out = write_filtered_app_slconf(Path(app_dir), slcp_name=slcp_name)
    except (FileNotFoundError, RuntimeError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(out)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Matter stack tooling helpers")
    parser.add_argument(
        "--print-sdk-paths",
        action="store_true",
        help="Print --sdk-package-path lines for build.sh",
    )
    parser.add_argument(
        "--write-app-slconf",
        metavar="APP_DIR",
        help="Write filtered autogen/slc-sdk.slconf for an app directory",
    )
    parser.add_argument(
        "--slcp-name",
        default="",
        help="Optional .slcp basename for app-type detection (with --write-app-slconf)",
    )
    parser.add_argument("slt_exe", nargs="?", help="Path to slt executable")
    parser.add_argument("repo_root", nargs="?", help="Matter extension repo root")
    args = parser.parse_args()

    if args.write_app_slconf:
        sys.path.insert(0, str(Path(args.repo_root or ".").resolve() / "slc"))
        return _cli_write_app_slconf(args.write_app_slconf, slcp_name=args.slcp_name)

    if args.print_sdk_paths:
        if not args.slt_exe or not args.repo_root:
            parser.error("--print-sdk-paths requires slt_exe and repo_root")
        repo_root = Path(args.repo_root).resolve()
        sys.path.insert(0, str(repo_root / "slc"))
        app_dir = os.environ.get("MATTER_APP_SLCONF_DIR", "")
        return _cli_print_sdk_paths(args.slt_exe, repo_root, app_dir=app_dir or None)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
