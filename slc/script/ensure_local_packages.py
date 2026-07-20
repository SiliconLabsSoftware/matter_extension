#!/usr/bin/env python3
"""Ensure local Matter packages, stack, and app SLT deps are up to date."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def _repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def _stamp_dir(repo_root: Path) -> Path:
    return repo_root / ".matter_local"


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _git_head(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _tree_fingerprint(root: Path, patterns: tuple[str, ...]) -> str:
    root = root.resolve()
    if not root.is_dir():
        return ""
    hasher = hashlib.sha256()
    files: list[Path] = []
    for pattern in patterns:
        files.extend(root.glob(pattern))
    for path in sorted({p.resolve() for p in files if p.is_file()}):
        rel = str(path.relative_to(root))
        hasher.update(rel.encode())
        hasher.update(path.read_bytes())
    return hasher.hexdigest()


def compute_export_fingerprint(repo_root: Path) -> str:
    hasher = hashlib.sha256()
    inputs: list[Path] = [
        repo_root / "matter.slce",
        repo_root / "slc" / "script" / "matter_package_version",
        repo_root / "packages" / "matter" / "conanfile.py",
        repo_root / "packages" / "matter_app" / "conanfile.py",
    ]
    for path in inputs:
        if path.is_file():
            hasher.update(str(path).encode())
            hasher.update(path.read_bytes())

    sdk_root = repo_root / "third_party" / "matter_sdk"
    sdk_head = _git_head(sdk_root)
    if sdk_head:
        hasher.update(f"matter_sdk:{sdk_head}".encode())
    elif sdk_root.is_dir():
        hasher.update(_tree_fingerprint(sdk_root, ("src/**/*.h", "src/**/*.cpp")).encode())

    hasher.update(
        _tree_fingerprint(repo_root / "slc" / "component", ("**/*.slcc", "**/*.slce")).encode()
    )
    hasher.update(_tree_fingerprint(repo_root / "slc" / "apps", ("**/*.slcp",)).encode())
    shared = repo_root / "packages" / "_shared"
    if shared.is_dir():
        hasher.update(_tree_fingerprint(shared, ("**/*.py",)).encode())
    return hasher.hexdigest()


def compute_stack_fingerprint(repo_root: Path) -> str:
    hasher = hashlib.sha256()
    for rel in (
        "slc/script/dependency_versions.yaml",
        "packages/matter/pkg.slt",
        "matter.slce",
        "slc/script/matter_package_version",
    ):
        path = repo_root / rel
        if path.is_file():
            hasher.update(rel.encode())
            hasher.update(path.read_bytes())
    return hasher.hexdigest()


def _read_stamp(stamp_path: Path) -> str | None:
    if not stamp_path.is_file():
        return None
    try:
        data = json.loads(stamp_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return str(data.get("fingerprint", "")) or None


def _write_stamp(stamp_path: Path, fingerprint: str) -> None:
    stamp_path.parent.mkdir(parents=True, exist_ok=True)
    stamp_path.write_text(
        json.dumps({"fingerprint": fingerprint}, indent=2) + "\n",
        encoding="utf-8",
    )


def _stamp_stale(stamp_path: Path, fingerprint: str) -> bool:
    return _read_stamp(stamp_path) != fingerprint


def _newer_than(path: Path, *others: Path) -> bool:
    if not path.is_file():
        return True
    mtime = path.stat().st_mtime
    for other in others:
        if other.is_file() and other.stat().st_mtime > mtime:
            return True
    return False


def app_deps_stale(app_dir: Path, slcp_name: str) -> bool:
    pkg_slt = app_dir / "pkg.slt"
    pkg_slconf = app_dir / "autogen" / "pkg.slconf"
    slc_sdk_slconf = app_dir / "autogen" / "slc-sdk.slconf"
    slcp = app_dir / slcp_name if slcp_name else None

    if not pkg_slconf.is_file():
        return True
    if not pkg_slt.is_file():
        return False
    if _newer_than(pkg_slconf, pkg_slt):
        return True
    if slcp and slcp.is_file():
        if _newer_than(pkg_slconf, slcp):
            return True
        if not slc_sdk_slconf.is_file() or _newer_than(slc_sdk_slconf, slcp):
            return True
    return False


def _matter_packages_installed(slt_exe: str) -> bool:
    sys.path.insert(0, str(_repo_root_from_script() / "slc"))
    from script.stack_tooling import slt_where

    matter = slt_where(slt_exe, "matter")
    matter_app = slt_where(slt_exe, "matter_app")
    if not matter or not matter_app:
        return False
    return (Path(matter) / "third_party" / "matter_sdk").is_dir()


def _stack_installed(repo_root: Path) -> bool:
    return (repo_root / "packages" / "matter" / "autogen" / "pkg.slconf").is_file()


def write_package_stamps(repo_root: Path) -> None:
    """Record that export and stack installs match current repo inputs."""
    stamp_dir = _stamp_dir(repo_root)
    _write_stamp(stamp_dir / "export.stamp", compute_export_fingerprint(repo_root))
    _write_stamp(stamp_dir / "stack.stamp", compute_stack_fingerprint(repo_root))


def ensure_local_packages(
    repo_root: Path,
    slt_exe: str,
    *,
    app_dir: Path | None = None,
    slcp_name: str = "",
    skip_export: bool = False,
    skip_stack: bool = False,
    skip_app: bool = False,
    verbose: bool = False,
) -> None:
    repo_root = repo_root.resolve()
    sys.path.insert(0, str(repo_root / "slc"))
    from script.stack_tooling import (
        export_local_packages,
        run_generate_pkg_slt,
        slt_install_pkg_slt,
    )
    from script.matter_slconf.slconf_io import write_filtered_app_slconf

    stamp_dir = _stamp_dir(repo_root)
    export_stamp = stamp_dir / "export.stamp"
    stack_stamp = stamp_dir / "stack.stamp"

    export_fp = compute_export_fingerprint(repo_root)
    stack_fp = compute_stack_fingerprint(repo_root)

    need_export = (
        not skip_export
        and (not _matter_packages_installed(slt_exe) or _stamp_stale(export_stamp, export_fp))
    )
    if need_export:
        if verbose:
            print("Ensuring local matter/matter_app export (inputs changed or not installed)")
        run_generate_pkg_slt(repo_root)
        export_local_packages(repo_root)
        _write_stamp(export_stamp, export_fp)
    elif verbose:
        print("Local matter/matter_app export is up to date")

    need_stack = not skip_stack and (
        not _stack_installed(repo_root) or _stamp_stale(stack_stamp, stack_fp)
    )
    if need_stack:
        if verbose:
            print("Ensuring matter stack install (dependency_versions.yaml or pkg.slt changed)")
        stack_pkg = repo_root / "packages" / "matter" / "pkg.slt"
        slt_install_pkg_slt(slt_exe, stack_pkg)
        _write_stamp(stack_stamp, stack_fp)
    elif verbose:
        print("Matter stack install is up to date")

    if skip_app or app_dir is None:
        return

    app_dir = app_dir.resolve()
    pkg_slt = app_dir / "pkg.slt"
    if not pkg_slt.is_file():
        raise FileNotFoundError(f"pkg.slt not found: {pkg_slt}")

    if app_deps_stale(app_dir, slcp_name):
        if verbose:
            print(f"Installing app dependencies from {pkg_slt}")
        slt_install_pkg_slt(slt_exe, pkg_slt)

    write_filtered_app_slconf(app_dir, slcp_name=slcp_name)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ensure local Matter export, stack, and app SLT dependencies"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_repo_root_from_script(),
        help="Matter extension repository root",
    )
    parser.add_argument("--slt-exe", default="", help="Path to slt executable")
    parser.add_argument("--app-dir", type=Path, default=None, help="App directory with pkg.slt")
    parser.add_argument("--slcp-name", default="", help="Optional .slcp basename")
    parser.add_argument("--skip-export", action="store_true")
    parser.add_argument("--skip-stack", action="store_true")
    parser.add_argument("--skip-app", action="store_true")
    parser.add_argument(
        "--write-stamps-only",
        action="store_true",
        help="Update export/stack stamp files without installing",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if args.write_stamps_only:
        write_package_stamps(repo_root)
        return 0

    slt_exe = args.slt_exe.strip()
    if not slt_exe:
        slt_exe = str(repo_root / "slc" / "tools" / "slt")
        if not Path(slt_exe).is_file():
            from shutil import which

            found = which("slt")
            if not found:
                print("ERROR: slt not found (set --slt-exe or install SLT CLI)", file=sys.stderr)
                return 1
            slt_exe = found

    try:
        ensure_local_packages(
            repo_root,
            slt_exe,
            app_dir=args.app_dir,
            slcp_name=args.slcp_name,
            skip_export=args.skip_export,
            skip_stack=args.skip_stack,
            skip_app=args.skip_app,
            verbose=args.verbose,
        )
    except (FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
