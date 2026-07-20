#!/usr/bin/env python3
"""Validate Matter sample app builds against the CI matrix."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


# Platform specs mirror .github/workflows/platform-builder.yaml
PLATFORM_SPECS: dict[str, dict[str, str | list[str]]] = {
    "mg24": {
        "json": "silabs-builds-mg24.json",
        "stack": "thread",
        "slcw": "slc/apps/{app}/thread/matter_thread_soc_{app}_series_2_freertos.slcw",
    },
    "mg24-internal": {
        "json": "silabs-builds-mg24-internal.json",
        "stack": "thread",
        "slcw": "slc/apps/{app}/thread/matter_thread_soc_{app}_series_2_internal_freertos.slcw",
    },
    "mg24-trustzone": {
        "json": "silabs-builds-mg24-trustzone.json",
        "stack": "thread",
        "slcw": (
            "slc/apps/{app}/thread/trustzone/"
            "matter_thread_soc_{app}_trustzone_series_2_freertos.slcw"
        ),
    },
    "mgm24": {
        "json": "silabs-builds-mgm24.json",
        "stack": "thread",
        "slcw": "slc/apps/{app}/thread/matter_thread_soc_{app}_series_2_freertos.slcw",
    },
    "mgm24-internal": {
        "json": "silabs-builds-mgm24-internal.json",
        "stack": "thread",
        "slcw": "slc/apps/{app}/thread/matter_thread_soc_{app}_series_2_internal_freertos.slcw",
    },
    "mg26": {
        "json": "silabs-builds-mg26.json",
        "stack": "thread",
        "slcw": "slc/apps/{app}/thread/matter_thread_soc_{app}_series_2_freertos.slcw",
    },
    "mg26-internal": {
        "json": "silabs-builds-mg26-internal.json",
        "stack": "thread",
        "slcw": "slc/apps/{app}/thread/matter_thread_soc_{app}_series_2_internal_freertos.slcw",
    },
    "mgm26-internal": {
        "json": "silabs-builds-mgm26-internal.json",
        "stack": "thread",
        "slcw": "slc/apps/{app}/thread/matter_thread_soc_{app}_series_2_internal_freertos.slcw",
    },
    "sixg301": {
        "json": "silabs-builds-sixg301.json",
        "stack": "thread",
        "slcw": "slc/apps/{app}/thread/matter_thread_soc_{app}_series_3_freertos.slcw",
    },
    "siwx-soc": {
        "json": "silabs-builds-siwx.json",
        "stack": "wifi",
        "slcw": "slc/apps/{app}/wifi/matter_wifi_soc_{app}_freertos.slcw",
    },
    "ncp-917": {
        "json": "silabs-builds-917-ncp.json",
        "stack": "wifi",
        "slcw": "slc/apps/{app}/wifi/matter_wifi_917_ncp_{app}_freertos.slcw",
    },
    "series-3-bootloader": {
        "json": "silabs-builds-series-3-bootloader.json",
        "stack": "bootloader",
        "slcw": (
            "slc/apps/bootloaders/bootloader_storage_single_4096k_series_3/"
            "matter_bootloader_internal_series_3.slcw"
        ),
        "apps": ["bootloader"],
    },
}

# Mirrors dev-apps-builder.yaml platform flags per app.
APP_PLATFORM_FLAGS: dict[str, dict[str, bool]] = {
    "lighting_app": {"trustzone": True},
    "lock_app": {"ncp_917": True},
    "thermostat": {"ncp_917": True},
    "window_app": {"ncp_917": True},
    "fan_control_app": {"ncp_917": True},
    "oven_app": {"thread": False},
    "evse_app": {"wifi_soc": True},
    "performance_test_app": {"wifi_soc": False},
    "zigbee_light": {
        "mg24_internal": False,
        "mgm24": False,
        "mgm24_internal": False,
        "wifi_soc": False,
    },
}

SKIP_APP_DIRS = frozenset({"bootloaders", "openthread_border_router_doc"})


@dataclass
class BuildJob:
    job_id: str
    app: str
    platform: str
    board: str
    variant: str
    slcw: str
    extra_args: list[str]
    json_file: str
    status: str = "pending"
    duration_s: float = 0.0
    log_path: str = ""
    error: str = ""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def discover_apps(root: Path) -> list[str]:
    apps_dir = root / "slc" / "apps"
    return sorted(
        path.name
        for path in apps_dir.iterdir()
        if path.is_dir() and path.name not in SKIP_APP_DIRS
    )


def parse_output_suffix(arguments: list[str]) -> str:
    for arg in arguments:
        if "--output_suffix" in arg:
            parts = shlex.split(arg)
            for index, part in enumerate(parts):
                if part == "--output_suffix" and index + 1 < len(parts):
                    return parts[index + 1].split(",")[0]
    return "base"


def parse_extra_args(arguments: list[str]) -> list[str]:
    extra: list[str] = []
    for arg in arguments:
        if arg.strip():
            extra.extend(shlex.split(arg))
    return extra


def is_copy_sources_build(variant: str, extra: list[str]) -> bool:
    return "--copy-sources" in extra or "copy-sources" in variant


def app_enabled_for_platform(app: str, platform: str) -> bool:
    flags = APP_PLATFORM_FLAGS.get(app, {})
    if platform == "mg24-trustzone":
        return flags.get("trustzone", False)
    if platform == "ncp-917":
        return flags.get("ncp_917", False)
    if platform == "siwx-soc":
        return flags.get("wifi_soc", True)
    if platform in ("mg24-internal", "mgm24-internal", "mg26-internal", "mgm26-internal"):
        return flags.get("mg24_internal", True)
    if platform == "mgm24":
        return flags.get("mgm24", True)
    if platform == "mgm24-internal":
        return flags.get("mgm24_internal", True)
    if platform.startswith("mg") or platform == "sixg301":
        return flags.get("thread", True)
    return True


def expand_jobs(
    *,
    apps: list[str],
    platforms: list[str],
    boards: set[str],
    build_type: str,
    variants: set[str],
    include_copy_sources: bool,
    github_dir: Path,
    root: Path,
) -> list[BuildJob]:
    jobs: list[BuildJob] = []

    for platform in platforms:
        spec = PLATFORM_SPECS.get(platform)
        if spec is None:
            continue

        json_path = github_dir / str(spec["json"])
        if not json_path.is_file():
            continue

        config = json.loads(json_path.read_text(encoding="utf-8")).get(build_type, {}) or {}
        platform_apps = spec.get("apps", apps)
        slcw_template = str(spec["slcw"])

        for app in platform_apps:
            if app not in apps:
                continue
            if not app_enabled_for_platform(app, platform):
                continue

            slcw_rel = slcw_template.format(app=app)
            if not (root / slcw_rel).is_file():
                continue

            entries = config.get(app, config.get("default", []))
            for entry in entries:
                arguments = entry.get("arguments", [])
                variant = parse_output_suffix(arguments)
                if variants and variant not in variants:
                    continue
                extra = parse_extra_args(arguments)
                if is_copy_sources_build(variant, extra) and not include_copy_sources:
                    if not variants or variant not in variants:
                        continue
                for board in entry.get("boards", []):
                    board_l = board.lower().split(",")[0]
                    if boards and board_l not in boards:
                        continue
                    job_id = f"{app}__{platform}__{board_l}__{variant}"
                    jobs.append(
                        BuildJob(
                            job_id=job_id,
                            app=app,
                            platform=platform,
                            board=board_l,
                            variant=variant,
                            slcw=slcw_rel,
                            extra_args=extra,
                            json_file=str(spec["json"]),
                        )
                    )
    return jobs


def resolve_slt_exe(root: Path) -> str:
    from shutil import which

    candidates = (
        os.environ.get("SLT_EXE", ""),
        str(root / "slc" / "tools" / "slt"),
    )
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    found = which("slt")
    if found:
        return found
    raise RuntimeError("slt not found (install SLT CLI or set SLT_EXE)")


def install_app_deps_for_sqa(root: Path, slcw: str, slt_exe: str) -> None:
    """Install per-app pkg.slt and write slconf under the installed matter_app tree."""
    rel_slcw = Path(slcw)
    pkg_slt = root / rel_slcw.parent / "pkg.slt"
    if not pkg_slt.is_file():
        raise FileNotFoundError(f"pkg.slt not found: {pkg_slt}")

    subprocess.run(
        [slt_exe, "install", "-f", str(pkg_slt), "--non-interactive"],
        check=True,
        cwd=root,
    )

    sys.path.insert(0, str(root / "slc"))
    from script.matter_slconf.slconf_io import write_filtered_app_slconf
    from script.stack_tooling import slt_where

    matter_app = slt_where(slt_exe, "matter_app")
    if not matter_app:
        raise RuntimeError("matter_app package is not installed")

    installed_app_dir = Path(matter_app) / rel_slcw.parent
    slcp_name = ""
    for slcp in sorted(installed_app_dir.glob("*.slcp")):
        slcp_name = slcp.name
        break
    if not slcp_name:
        raise FileNotFoundError(f"No .slcp found in installed app dir: {installed_app_dir}")

    write_filtered_app_slconf(installed_app_dir, slcp_name=slcp_name)


def run_job(
    job: BuildJob,
    *,
    root: Path,
    logs_dir: Path,
    build_script: Path,
    sqa: bool = False,
    slt_exe: str = "",
) -> BuildJob:
    log_file = logs_dir / f"{job.job_id}.log"
    job.log_path = str(log_file.relative_to(root))
    if sqa:
        if not slt_exe:
            slt_exe = resolve_slt_exe(root)
        install_app_deps_for_sqa(root, job.slcw, slt_exe)
        command = [str(build_script), "--sqa", job.slcw, job.board, *job.extra_args]
    else:
        command = [str(build_script), job.slcw, job.board, *job.extra_args]
    started = datetime.now(timezone.utc)
    with log_file.open("w", encoding="utf-8") as log:
        log.write(f"# command: {shlex.join(command)}\n\n")
        log.flush()
        proc = subprocess.run(
            command,
            cwd=root,
            stdout=log,
            stderr=subprocess.STDOUT,
            env={**os.environ, "MATTER_ROOT": str(root)},
        )
    job.duration_s = (datetime.now(timezone.utc) - started).total_seconds()
    if proc.returncode == 0:
        job.status = "passed"
    else:
        job.status = "failed"
        job.error = f"exit code {proc.returncode}"
    return job


def write_report(run_dir: Path, jobs: list[BuildJob], *, build_type: str) -> None:
    passed = [job for job in jobs if job.status == "passed"]
    failed = [job for job in jobs if job.status == "failed"]

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "build_type": build_type,
        "total": len(jobs),
        "passed": len(passed),
        "failed": len(failed),
        "jobs": [asdict(job) for job in jobs],
    }
    (run_dir / "report.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Validate builds report",
        "",
        f"- **Build type:** `{build_type}`",
        f"- **Total:** {len(jobs)}",
        f"- **Passed:** {len(passed)}",
        f"- **Failed:** {len(failed)}",
        "",
        "## Failed builds",
        "",
    ]
    if failed:
        lines.append("| App | Platform | Board | Variant | Log |")
        lines.append("|-----|----------|-------|---------|-----|")
        for job in sorted(failed, key=lambda item: (item.app, item.platform, item.board)):
            lines.append(
                f"| `{job.app}` | `{job.platform}` | `{job.board}` | `{job.variant}` | "
                f"[log]({job.log_path}) |"
            )
    else:
        lines.append("_None_")

    lines.extend(["", "## Passed builds", ""])
    lines.append("| App | Platform | Board | Variant | Duration (s) |")
    lines.append("|-----|----------|-------|---------|--------------|")
    for job in sorted(passed, key=lambda item: (item.app, item.platform, item.board)):
        lines.append(
            f"| `{job.app}` | `{job.platform}` | `{job.board}` | `{job.variant}` | "
            f"{job.duration_s:.1f} |"
        )

    (run_dir / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_latest_link(validate_root: Path, run_dir: Path) -> None:
    latest = validate_root / "latest"
    if latest.is_symlink() or latest.exists():
        latest.unlink()
    latest.symlink_to(run_dir.name, target_is_directory=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Matter app builds against the CI matrix",
    )
    parser.add_argument(
        "--build-type",
        choices=["standard", "full"],
        default="standard",
        help="CI matrix tier (default: standard)",
    )
    parser.add_argument("--app", action="append", default=[], help="Filter by app (repeatable)")
    parser.add_argument("--board", action="append", default=[], help="Filter by board (repeatable)")
    parser.add_argument(
        "--platform",
        action="append",
        default=[],
        help="Filter by platform (repeatable), e.g. mg24, siwx-soc",
    )
    parser.add_argument(
        "--stack",
        choices=["thread", "wifi", "bootloader"],
        help="Filter by stack type",
    )
    parser.add_argument(
        "--variant",
        action="append",
        default=[],
        help="Filter by --output_suffix variant (repeatable)",
    )
    parser.add_argument(
        "--include-copy-sources",
        action="store_true",
        help="Include CI matrix entries that pass --copy-sources (excluded by default)",
    )
    parser.add_argument("-j", "--jobs", type=int, default=1, help="Parallel builds (default: 1)")
    parser.add_argument("--dry-run", action="store_true", help="List planned builds only")
    parser.add_argument("--list-platforms", action="store_true", help="List known platforms")
    parser.add_argument(
        "--sqa",
        action="store_true",
        help="Build from installed SLT packages (slt install per app, build.sh --sqa)",
    )
    args = parser.parse_args()

    root = repo_root()
    github_dir = root / ".github"

    if args.list_platforms:
        for name, spec in PLATFORM_SPECS.items():
            print(f"{name:20} {spec['json']:40} {spec['stack']}")
        return 0

    apps = args.app or discover_apps(root)
    platforms = args.platform or list(PLATFORM_SPECS.keys())
    if args.stack:
        platforms = [name for name in platforms if PLATFORM_SPECS[name]["stack"] == args.stack]
    boards = {board.lower() for board in args.board}
    variants = set(args.variant)

    jobs = expand_jobs(
        apps=apps,
        platforms=platforms,
        boards=boards,
        build_type=args.build_type,
        variants=variants,
        include_copy_sources=args.include_copy_sources,
        github_dir=github_dir,
        root=root,
    )
    if not jobs:
        print("No matching build jobs.", file=sys.stderr)
        return 1

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    validate_root = root / "out" / "validate_builds"
    run_dir = validate_root / run_id
    logs_dir = run_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    build_script = root / "slc" / "build.sh"

    print(f"Planned {len(jobs)} build(s) -> {run_dir}")
    if args.dry_run:
        sqa_flag = " --sqa" if args.sqa else ""
        for job in jobs:
            extra = " ".join(job.extra_args)
            print(
                f"  {job.job_id}: ./slc/build.sh{sqa_flag} {job.slcw} "
                f"{job.board} {extra}".rstrip()
            )
        return 0

    slt_exe = resolve_slt_exe(root) if args.sqa else ""
    parallel_jobs = 1 if args.sqa else args.jobs

    if parallel_jobs == 1:
        results = [
            run_job(
                job,
                root=root,
                logs_dir=logs_dir,
                build_script=build_script,
                sqa=args.sqa,
                slt_exe=slt_exe,
            )
            for job in jobs
        ]
    else:
        results: list[BuildJob] = []
        with ThreadPoolExecutor(max_workers=parallel_jobs) as pool:
            futures = {
                pool.submit(
                    run_job,
                    job,
                    root=root,
                    logs_dir=logs_dir,
                    build_script=build_script,
                    sqa=args.sqa,
                    slt_exe=slt_exe,
                ): job
                for job in jobs
            }
            for future in as_completed(futures):
                results.append(future.result())

    write_report(run_dir, results, build_type=args.build_type)
    update_latest_link(validate_root, run_dir)
    print(f"Report: {run_dir / 'REPORT.md'}")
    print(f"Latest: {validate_root / 'latest' / 'REPORT.md'}")
    failed = sum(1 for job in results if job.status == "failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
