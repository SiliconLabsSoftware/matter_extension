#!/usr/bin/env python3
"""Compare stored code-size analyzer results between two Jenkins builds."""

from __future__ import annotations

import argparse
import os
import sys
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


CODE_SIZE_TARGETS = [
    CodeSizeTarget(
        "slc-lighting-app-release-MG24",
        "BRD4187C",
        "efr32mg24b210f1536im48",
    ),
    CodeSizeTarget(
        "slc-lighting-app-release-MG24-nolto",
        "BRD4187C",
        "efr32mg24b210f1536im48",
    ),
    CodeSizeTarget(
        "slc-lock-app-release-MG24",
        "BRD4187C",
        "efr32mg24b210f1536im48",
    ),
    CodeSizeTarget(
        "slc-lock-app-release-MG24-nolto",
        "BRD4187C",
        "efr32mg24b210f1536im48",
    ),
    CodeSizeTarget(
        "slc-zigbee-matter-light-release-MG24",
        "BRD4187C",
        "efr32mg24b210f1536im48",
    ),
    CodeSizeTarget(
        "slc-zigbee-matter-light-release-MG24-nolto",
        "BRD4187C",
        "efr32mg24b210f1536im48",
    ),
    CodeSizeTarget(
        "slc-lighting-app-release-MG301",
        "BRD4407A",
        "simg301m114lih",
    ),
    CodeSizeTarget(
        "slc-lighting-app-release-MG301-nolto",
        "BRD4407A",
        "simg301m114lih",
    ),
    CodeSizeTarget(
        "slc-lock-app-release-MG301",
        "BRD4407A",
        "simg301m114lih",
    ),
    CodeSizeTarget(
        "slc-lock-app-release-MG301-nolto",
        "BRD4407A",
        "simg301m114lih",
    ),
    CodeSizeTarget(
        "slc-zigbee-matter-light-release-MG301",
        "BRD4407A",
        "simg301m114lih",
    ),
    CodeSizeTarget(
        "slc-zigbee-matter-light-release-MG301-nolto",
        "BRD4407A",
        "simg301m114lih",
    ),
    CodeSizeTarget(
        "slc-SiWx917-lighting-release-Si917",
        "BRD4338A",
        "siwg917m111mgtba",
    ),
    CodeSizeTarget(
        "slc-SiWx917-lighting-release-Si917-nolto",
        "BRD4338A",
        "siwg917m111mgtba",
    ),
    CodeSizeTarget(
        "slc-SiWx917-lock-release-Si917",
        "BRD4338A",
        "siwg917m111mgtba",
    ),
    CodeSizeTarget(
        "slc-SiWx917-lock-release-Si917-nolto",
        "BRD4338A",
        "siwg917m111mgtba",
    ),
]


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


def main() -> int:
    args = parse_args()
    current_build = normalize_build_number(args.current_build)
    previous_build = normalize_build_number(args.previous_build)
    client = create_results_api(args.service_url, args.verify_ssl)

    print(
        f"Comparing code size results for branch {args.branch_name}: "
        f"{current_build} vs preferred baseline {previous_build}"
    )
    print(
        f"Thresholds: flash/code > {args.flash_threshold_pct:.2f}%, "
        f"RAM > {args.ram_threshold_pct:.2f}%"
    )
    print("=" * 160)
    print(
        f"{'Application':<48} {'Board':<10} {'Target':<24} {'Baseline':<10} "
        f"{'Flash Change':<28} {'RAM Change':<28} {'Status':<8}"
    )
    print("-" * 160)

    failures = []
    missing = []
    compared_count = 0

    for target in CODE_SIZE_TARGETS:
        target_records = query_target_records(client, args.branch_name, target)
        current = select_exact_record(target, target_records, current_build)
        previous = (
            select_baseline_record(target, target_records, current, previous_build)
            if current is not None
            else None
        )

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
        status = "FAIL" if failed else "PASS"
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
        print("ERROR: No comparable code size records were found.")
        return 1

    if failures:
        print("Code size increase threshold exceeded.")
        return 1

    print("All available code size results are within thresholds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
