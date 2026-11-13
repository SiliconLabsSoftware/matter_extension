#!/usr/bin/env python3
"""
@file demo_test.py
@brief Matter Renode demo CLI (CI and local): checkpoint, ELF, demo flow or interactive hub commands.

Entry point for renode-demo-tests: argument parsing and delegation to demo_runner.run_demo.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from demo_config import DEMO_APPS, EXTRA_DEMO_APP
from demo_runner import run_demo


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Matter Renode demo (loads linux-booted-thread.save via pyrenode3)",
    )
    parser.add_argument(
        "--app",
        choices=DEMO_APPS,
        default=None,
        help="Run post-commission steps from demo_flows.yaml",
    )
    parser.add_argument("--matter-elf", type=Path, required=True)
    parser.add_argument(
        "--extra-elf",
        default="",
        metavar="PATH",
        help="Second SoC ELF (required when --app has a paired demo binary)",
    )
    parser.add_argument("--board", default="brd4187c", help="SoC board repl name, e.g. brd4187c")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Commission, then open a hub command prompt instead of running demo steps",
    )
    args = parser.parse_args()

    if args.app is None and not args.interactive:
        parser.error("specify --app or --interactive")

    matter_elf = args.matter_elf.resolve()
    if not matter_elf.is_file():
        raise FileNotFoundError(matter_elf)

    extra_elf: Path | None = None
    if args.extra_elf.strip():
        extra_elf = Path(args.extra_elf).resolve()
        if not extra_elf.is_file():
            raise FileNotFoundError(extra_elf)
    app = args.app
    if app in EXTRA_DEMO_APP and extra_elf is None:
        raise FileNotFoundError(f"{app} requires --extra-elf ({EXTRA_DEMO_APP[app]})")
    elif extra_elf is not None and app not in EXTRA_DEMO_APP:
        raise FileNotFoundError("--extra-elf requires a dual-device --app")

    try:
        run_demo(
            matter_elf,
            app,
            extra_elf=extra_elf,
            board=args.board,
            interactive=args.interactive,
        )
        label = app or "custom"
        print(f"Demo session for {label} succeeded")
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"Demo session failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
