#!/usr/bin/env python3
"""
@file renode_config.py
@brief Renode demo matrix: Matter example apps, boards, and CI artifact naming.

Loads app metadata from demo_flows.yaml and emits the parallel demo job matrix.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

with Path(__file__).with_name("demo_flows.yaml").open(encoding="utf-8") as handle:
    DEMO_FLOWS = yaml.safe_load(handle)

with Path(__file__).with_name("sanity_flows.yaml").open(encoding="utf-8") as handle:
    SANITY_FLOWS = yaml.safe_load(handle)

SANITY_MATRIX_TESTS = tuple(
    name for name in SANITY_FLOWS if name != "test_tc_commission"
)

DEMO_APPS = tuple(DEMO_FLOWS)
EXTRA_DEMO_APP = {
    app: flow["extra_app"] for app, flow in DEMO_FLOWS.items() if flow.get("extra_app")
}


@dataclass(frozen=True, slots=True)
class DemoTarget:
    platform: str
    board: str


# EFR32xG24 / EFR32xG26 / SixG301 boards exercised in parallel demo jobs.
DEMO_TARGETS: tuple[DemoTarget, ...] = (
    DemoTarget("mg24", "brd4187c"),
    DemoTarget("mg24", "brd4186c"),
    DemoTarget("mg26", "brd4116a"),
    DemoTarget("mg26", "brd4117a"),
    DemoTarget("mg26", "brd4118a"),
    DemoTarget("mg26", "brd4120a"),
    DemoTarget("mg26", "brd4121a"),
    DemoTarget("sixg301", "brd4407a"),
    DemoTarget("sixg301", "brd1019a"),
)


def matrix_include() -> list[dict[str, str]]:
    """Run every demo app on every full-build target."""
    return [
        {
            "example-app": app,
            "extra-app": EXTRA_DEMO_APP.get(app, ""),
            "board": target.board,
            "platform": target.platform,
        }
        for target in DEMO_TARGETS
        for app in DEMO_APPS
    ]


def write_job_github_outputs(
    github_output: str,
    cells: list[dict[str, str]],
) -> None:
    payload = json.dumps(cells)
    print(f"matrix cells: {len(cells)}")
    with open(github_output, "a", encoding="utf-8") as handle:
        handle.write(f"include={payload}\n")


def sanity_matrix_include() -> list[dict[str, str]]:
    return [{"sanity-test": name} for name in SANITY_MATRIX_TESTS]


def main() -> None:
    if "--sanity-matrix" in sys.argv:
        write_job_github_outputs(os.environ["GITHUB_OUTPUT"], sanity_matrix_include())
        return
    write_job_github_outputs(os.environ["GITHUB_OUTPUT"], matrix_include())


if __name__ == "__main__":
    main()
