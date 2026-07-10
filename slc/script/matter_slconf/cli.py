#!/usr/bin/env python3
"""CLI for matter-app-slconf and matter-validate-slcp."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _write_slconf(app_dir: Path, slcp_name: str) -> int:
    from .slconf_io import write_filtered_app_slconf

    try:
        out = write_filtered_app_slconf(app_dir, slcp_name=slcp_name)
    except (FileNotFoundError, RuntimeError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(out)
    return 0


def _validate_slcp(slcp_path: Path, slconf_path: Path) -> int:
    from .validate import validate_slcp_against_slconf

    errors = validate_slcp_against_slconf(slcp_path, slconf_path)
    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1
    print(f"OK: {slcp_path}")
    return 0


def _build_app(app_dir: Path, slcp_name: str, board: str, out_dir: Path) -> int:
    app_dir = app_dir.resolve()
    slcp_path = app_dir / slcp_name
    if not slcp_path.is_file():
        print(f"ERROR: slcp not found: {slcp_path}", file=sys.stderr)
        return 1

    pkg_slt = app_dir / "pkg.slt"
    if not pkg_slt.is_file():
        print(f"ERROR: pkg.slt not found: {pkg_slt}", file=sys.stderr)
        return 1

    slt = "slt"
    steps = [
        [slt, "install", "-f", str(pkg_slt), "--non-interactive"],
    ]
    for cmd in steps:
        print("Running:", " ".join(cmd))
        if subprocess.run(cmd, cwd=app_dir).returncode != 0:
            return 1

    if _write_slconf(app_dir, slcp_name) != 0:
        return 1

    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    gen_cmd = [
        "slc",
        "generate",
        "-p",
        slcp_name,
        "--with",
        board,
        "-d",
        str(out_dir),
        "-o",
        "makefile",
        "--generator-timeout=180",
    ]
    print("Running:", " ".join(gen_cmd), f"(cwd={app_dir})")
    if subprocess.run(gen_cmd, cwd=app_dir).returncode != 0:
        return 1

    if subprocess.run(["make", "-C", str(out_dir), "-j"], cwd=app_dir).returncode != 0:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Matter SLT slconf utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    p_slconf = sub.add_parser(
        "slconf",
        help="Write filtered autogen/slc-sdk.slconf for an app directory",
    )
    p_slconf.add_argument(
        "--app-dir",
        dest="app_dir",
        type=Path,
        help="App directory containing autogen/pkg.slconf",
    )
    p_slconf.add_argument("app_dir_pos", type=Path, nargs="?", default=None)
    p_slconf.add_argument("--slcp-name", "--slcp", default="", dest="slcp_name")

    p_validate = sub.add_parser(
        "validate-slcp",
        help="Validate .slcp sdk/extension versions against pkg.slconf paths",
    )
    p_validate.add_argument("slcp", type=Path)
    p_validate.add_argument(
        "--slconf",
        type=Path,
        default=None,
        help="Defaults to <slcp-dir>/autogen/pkg.slconf",
    )

    p_build = sub.add_parser(
        "build-app",
        help="slt install, write slconf, slc generate, and make",
    )
    p_build.add_argument("app_dir", type=Path)
    p_build.add_argument("slcp_name")
    p_build.add_argument("board")
    p_build.add_argument(
        "--out-dir",
        type=Path,
        default=Path("./out"),
        help="Output directory for slc generate / make",
    )

    args = parser.parse_args(argv)

    if args.command == "slconf":
        app_dir = args.app_dir or args.app_dir_pos
        if app_dir is None:
            p_slconf.error("app_dir is required (--app-dir or positional)")
        return _write_slconf(app_dir, args.slcp_name)
    if args.command == "validate-slcp":
        slconf = args.slconf or (args.slcp.parent / "autogen" / "pkg.slconf")
        return _validate_slcp(args.slcp.resolve(), slconf.resolve())
    if args.command == "build-app":
        return _build_app(args.app_dir, args.slcp_name, args.board, args.out_dir)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
