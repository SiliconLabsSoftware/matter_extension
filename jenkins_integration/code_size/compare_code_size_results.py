#!/usr/bin/env python3
"""Compare stored code-size analyzer results between two Jenkins builds."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import urllib3

from code_size_analyzer_client import ApiClient, Configuration, ResultsApi


@dataclass(frozen=True)
class CodeSizeTarget:
    application_name: str
    board: str
    target_part: str
    compiler: str = "gcc"
    stack: str = "matter"


@dataclass(frozen=True)
class SizeRecord:
    target: CodeSizeTarget
    build_number: str
    code_size: int
    ram_size: int


BOARD_METADATA = {
    "brd4187c": ("BRD4187C", "MG24", "efr32mg24b210f1536im48"),
    "brd4407a": ("BRD4407A", "MG301", "simg301m114lih"),
    "brd4338a": ("BRD4338A", "Si917", "siwg917m111mgtba"),
}


def normalize_build_number(build_number: str) -> str:
    build_number = str(build_number).strip()
    return build_number if build_number.startswith("b") else f"b{build_number}"


def build_number_value(build_number: str | None) -> int | None:
    if not build_number:
        return None
    build_number = str(build_number).strip()
    if build_number.startswith("b"):
        build_number = build_number[1:]
    return int(build_number) if build_number.isdigit() else None


def extract_solution_dir(path: Path) -> str | None:
    for part in path.parts:
        if part.endswith("_solution") or part.endswith("_solution_lto"):
            return part
    return None


def extract_app_from_solution(solution_dir: str) -> str | None:
    base_name = solution_dir
    if base_name.endswith("_solution_lto"):
        base_name = base_name[: -len("_solution_lto")]
    elif base_name.endswith("_solution"):
        base_name = base_name[: -len("_solution")]

    if "zigbee_light" in base_name:
        return "zigbee-matter-light"
    if "lighting_app" in base_name:
        return "lighting-app"
    if "lock_app" in base_name:
        return "lock-app"
    return None


def board_metadata_from_path(path: Path) -> tuple[str, str, str] | None:
    path_parts = [part.lower() for part in path.parts]
    for board_id, metadata in BOARD_METADATA.items():
        if board_id in path_parts:
            return metadata
    return None


def target_from_map_file(map_file_path: Path) -> CodeSizeTarget | None:
    solution_dir = extract_solution_dir(map_file_path)
    if solution_dir is None:
        return None

    app = extract_app_from_solution(solution_dir)
    board_metadata = board_metadata_from_path(map_file_path)
    if app is None or board_metadata is None:
        return None

    board, family, target_part = board_metadata
    if board == "BRD4338A":
        if app.endswith("-app"):
            app = f"SiWx917-{app.removesuffix('-app')}"
        else:
            app = f"SiWx917-{app}"

    application_name = f"slc-{app}-release-{family}"
    if not solution_dir.endswith("_solution_lto"):
        application_name = f"{application_name}-nolto"

    return CodeSizeTarget(application_name, board, target_part)


def discover_code_size_targets(map_root: str) -> list[CodeSizeTarget]:
    targets: set[CodeSizeTarget] = set()
    for map_file_path in Path(map_root).rglob("*.map"):
        if "sqa-artifacts" in {part.lower() for part in map_file_path.parts}:
            continue

        target = target_from_map_file(map_file_path)
        if target is not None:
            targets.add(target)

    return sorted(
        targets,
        key=lambda target: (target.board, target.application_name, target.target_part),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare code-size analyzer summary results between two builds."
    )
    parser.add_argument("--branch-name", required=True)
    parser.add_argument("--current-build", required=True)
    parser.add_argument("--previous-build", required=True)
    parser.add_argument(
        "--service-url",
        default="https://code-size-analyzer.silabs.net",
        help="Code size analyzer service endpoint.",
    )
    parser.add_argument(
        "--verify-ssl",
        action="store_true",
        help="Verify SSL certificate when calling the service.",
    )
    parser.add_argument(
        "--map-root",
        default=".",
        help=(
            "Root directory used to discover successfully built Dev Apps .map files. "
            "Discovered files define the code-size targets to compare."
        ),
    )
    parser.add_argument(
        "--data-wait-retries",
        type=int,
        default=10,
        help="Number of retries while waiting for current build records to appear.",
    )
    parser.add_argument(
        "--data-wait-seconds",
        type=int,
        default=60,
        help="Seconds to wait between current build record retries.",
    )
    parser.add_argument(
        "--flash-threshold-pct",
        type=float,
        default=0.2,
        help="Allowed flash/code size increase percentage.",
    )
    parser.add_argument(
        "--ram-threshold-pct",
        type=float,
        default=1.0,
        help="Allowed RAM size increase percentage.",
    )
    return parser.parse_args()


def value_from_size_entry(entry: Any, *names: str) -> int | None:
    if entry is None:
        return None
    if hasattr(entry, "to_dict"):
        entry = entry.to_dict()
    if not isinstance(entry, dict):
        return None

    for name in names:
        value = entry.get(name)
        if value is not None:
            return int(value)
    return None


def extract_size_pair(summary: dict[str, Any]) -> tuple[int, int]:
    direct_code = value_from_size_entry(summary, "code_size", "codeSize")
    direct_ram = value_from_size_entry(summary, "RAM_size", "RAMSize", "ram_size")
    if direct_code is not None and direct_ram is not None:
        return direct_code, direct_ram

    preferred_keys = (
        "total",
        "Total",
        "TOTAL",
        "application",
        "Application",
        "all",
        "ALL",
    )
    for key in preferred_keys:
        if key in summary:
            code = value_from_size_entry(summary[key], "code_size", "codeSize")
            ram = value_from_size_entry(summary[key], "RAM_size", "RAMSize", "ram_size")
            if code is not None and ram is not None:
                return code, ram

    code_total = 0
    ram_total = 0
    found = False
    for value in summary.values():
        code = value_from_size_entry(value, "code_size", "codeSize")
        ram = value_from_size_entry(value, "RAM_size", "RAMSize", "ram_size")
        if code is not None and ram is not None:
            code_total += code
            ram_total += ram
            found = True

    if not found:
        raise ValueError(f"Could not extract code/RAM sizes from summary: {summary}")
    return code_total, ram_total


def create_results_api(service_url: str, verify_ssl: bool) -> ResultsApi:
    if not verify_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    config = Configuration(host=service_url)
    config.proxy = os.environ.get("https_proxy")
    config.verify_ssl = verify_ssl
    return ResultsApi(ApiClient(config))


def result_to_dict(result: Any) -> dict[str, Any]:
    if hasattr(result, "to_dict"):
        return result.to_dict()
    if isinstance(result, dict):
        return result
    raise TypeError(f"Unsupported result type: {type(result)!r}")


def result_timestamp(result: dict[str, Any]) -> datetime:
    timestamp = result.get("row_create_date_time")
    if isinstance(timestamp, datetime):
        return timestamp
    if isinstance(timestamp, str):
        return datetime.fromisoformat(timestamp)
    return datetime.min


def query_target_records(
    client: ResultsApi,
    branch_name: str,
    target: CodeSizeTarget,
) -> list[dict[str, Any]]:
    results = client.get_app_summary_records(
        stack=target.stack,
        application_name=target.application_name,
        branch=[branch_name],
        sdk_commit_hash=None,
    )
    if not results:
        return []

    matching_results = []
    for result in results:
        result_dict = result_to_dict(result)
        if result_dict.get("compiler") != target.compiler:
            continue
        if result_dict.get("target") != target.target_part:
            continue
        if str(result_dict.get("board", "")).lower() != target.board.lower():
            continue
        matching_results.append(result_dict)
    return matching_results


def record_to_size_record(target: CodeSizeTarget, result: dict[str, Any]) -> SizeRecord:
    code_size, ram_size = extract_size_pair(result.get("summary_json") or {})
    return SizeRecord(target, result["build_number"], code_size, ram_size)


def select_exact_record(
    target: CodeSizeTarget, records: list[dict[str, Any]], build_number: str
) -> SizeRecord | None:
    matching_records = [
        record for record in records if record.get("build_number") == build_number
    ]
    if not matching_records:
        return None

    result = max(matching_records, key=result_timestamp)
    return record_to_size_record(target, result)


def select_baseline_record(
    target: CodeSizeTarget,
    records: list[dict[str, Any]],
    current: SizeRecord,
    preferred_build_number: str,
) -> SizeRecord | None:
    exact_baseline = select_exact_record(target, records, preferred_build_number)
    if exact_baseline is not None:
        return exact_baseline

    current_build_value = build_number_value(current.build_number)
    candidates = []
    for record in records:
        record_build_number = record.get("build_number")
        if record_build_number == current.build_number:
            continue

        record_build_value = build_number_value(record_build_number)
        if (
            current_build_value is not None
            and record_build_value is not None
            and record_build_value < current_build_value
        ):
            candidates.append(record)

    if not candidates:
        return None

    result = max(
        candidates,
        key=lambda record: (
            build_number_value(record.get("build_number")) or -1,
            result_timestamp(record),
        ),
    )
    return record_to_size_record(target, result)


def pct_change(current: int, previous: int) -> float:
    if previous <= 0:
        return 0.0
    return (current - previous) / previous * 100


def format_delta(current: int, previous: int) -> str:
    delta = current - previous
    pct = pct_change(current, previous)
    sign = "+" if delta > 0 else ""
    return f"{sign}{delta} bytes ({sign}{pct:.2f}%)"


def compare_records(
    current: SizeRecord,
    previous: SizeRecord,
    flash_threshold_pct: float,
    ram_threshold_pct: float,
) -> bool:
    code_pct = pct_change(current.code_size, previous.code_size)
    ram_pct = pct_change(current.ram_size, previous.ram_size)
    code_failed = current.code_size > previous.code_size and code_pct > flash_threshold_pct
    ram_failed = current.ram_size > previous.ram_size and ram_pct > ram_threshold_pct
    return code_failed or ram_failed


def collect_target_data(
    client: ResultsApi,
    branch_name: str,
    targets: list[CodeSizeTarget],
    current_build: str,
    previous_build: str,
) -> tuple[list[tuple[CodeSizeTarget, SizeRecord | None, SizeRecord | None]], int]:
    target_data = []
    current_missing_count = 0

    for target in targets:
        target_records = query_target_records(client, branch_name, target)
        current = select_exact_record(target, target_records, current_build)
        previous = (
            select_baseline_record(target, target_records, current, previous_build)
            if current is not None
            else None
        )
        if current is None:
            current_missing_count += 1
        target_data.append((target, current, previous))

    return target_data, current_missing_count


def main() -> int:
    args = parse_args()
    current_build = normalize_build_number(args.current_build)
    previous_build = normalize_build_number(args.previous_build)
    code_size_targets = discover_code_size_targets(args.map_root)

    if not code_size_targets:
        print(f"WARNING: No successfully built Dev Apps .map files found in {args.map_root}.")
        return 0

    client = create_results_api(args.service_url, args.verify_ssl)

    print(
        f"Comparing code size results for branch {args.branch_name}: "
        f"{current_build} vs preferred baseline {previous_build}"
    )
    print(f"Discovered {len(code_size_targets)} code size target(s) from {args.map_root}")
    print(
        f"Thresholds: flash/code > {args.flash_threshold_pct:.2f}%, "
        f"RAM > {args.ram_threshold_pct:.2f}%"
    )

    target_data = []
    current_missing_count = 0
    max_retries = max(args.data_wait_retries, 0)
    wait_seconds = max(args.data_wait_seconds, 0)
    for attempt in range(max_retries + 1):
        target_data, current_missing_count = collect_target_data(
            client,
            args.branch_name,
            code_size_targets,
            current_build,
            previous_build,
        )
        if current_missing_count < len(code_size_targets) or attempt == max_retries:
            break

        print(
            f"No current build records are available yet. Waiting {wait_seconds}s "
            f"before retry {attempt + 1}/{max_retries}..."
        )
        time.sleep(wait_seconds)

    print("=" * 160)
    print(
        f"{'Application':<48} {'Board':<10} {'Target':<24} {'Baseline':<10} "
        f"{'Flash Change':<28} {'RAM Change':<28} {'Status':<8}"
    )
    print("-" * 160)

    failures = []
    missing = []
    compared_count = 0

    for target, current, previous in target_data:
        if current is None or previous is None:
            missing.append(
                (
                    target,
                    "current" if current is None else "",
                    "previous" if previous is None else "",
                )
            )
            print(
                f"{target.application_name:<48} {target.board:<10} {target.target_part:<24} "
                f"{'N/A':<10} {'MISSING DATA':<28} {'MISSING DATA':<28} {'WARN':<8}"
            )
            continue

        compared_count += 1
        failed = compare_records(
            current,
            previous,
            args.flash_threshold_pct,
            args.ram_threshold_pct,
        )
        status = "WARN" if failed else "PASS"
        if failed:
            failures.append((current, previous))

        print(
            f"{target.application_name:<48} {target.board:<10} {target.target_part:<24} "
            f"{previous.build_number:<10} "
            f"{format_delta(current.code_size, previous.code_size):<28} "
            f"{format_delta(current.ram_size, previous.ram_size):<28} {status:<8}"
        )

    print("=" * 160)

    if missing:
        print("WARNING: Some target results were missing and were not compared.")
        for target, current_missing, previous_missing in missing:
            missing_parts = ", ".join(
                part for part in (current_missing, previous_missing) if part
            )
            print(
                f"  - {target.application_name} {target.board}: "
                f"missing {missing_parts}"
            )

    if compared_count == 0:
        print("WARNING: No comparable code size records were found.")
        return 0

    if failures:
        print("WARNING: Code size increase threshold exceeded.")
        return 0

    print("All available code size results are within thresholds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
