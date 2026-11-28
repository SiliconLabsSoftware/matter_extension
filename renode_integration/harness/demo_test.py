#!/usr/bin/env python3
"""
@file demo_test.py
@brief Matter Renode demo CLI (CI and local): checkpoint, ELF, demo flow or interactive hub commands.

Entry point for demo tests, commissioned interactive sessions, and manual provisioning.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from demo_config import DEMO_APPS, EXTRA_DEMO_APP


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
    parser.add_argument("--board", required=True, help="SoC board repl name, e.g. brd4187c")
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Commission, then open a hub command prompt instead of running demo steps",
    )
    parser.add_argument(
        "--provision", action="store_true",
        help="Open a manual provisioning prompt before commissioning (requires --nvm3-hex)",
    )
    parser.add_argument("--nvm3-hex", type=Path, help="Initial NVM3 image for --provision")
    parser.add_argument("--provision-image", type=Path, help="Override the provisioning disk")
    args = parser.parse_args()

    if args.provision:
        if args.app or args.extra_elf or args.interactive:
            parser.error("--provision cannot be combined with --app, --extra-elf, or --interactive")
        if args.nvm3_hex is None:
            parser.error("--provision requires --nvm3-hex")
        if not sys.stdin.isatty():
            parser.error("manual provisioning requires an interactive terminal")
    elif args.nvm3_hex is not None or args.provision_image is not None:
        parser.error("--nvm3-hex and --provision-image require --provision")
    for name in ("nvm3_hex", "provision_image"):
        value = getattr(args, name)
        if value is not None:
            value = value.resolve()
            if not value.is_file():
                parser.error(f"--{name.replace('_', '-')}: file not found: {value}")
            setattr(args, name, value)

    if args.app is None and not args.interactive and not args.provision:
        parser.error("specify --app, --interactive, or --provision")

    matter_elf = args.matter_elf.resolve()
    if not matter_elf.is_file():
        parser.error(f"--matter-elf: file not found: {matter_elf}")

    extra_elf: Path | None = None
    if args.extra_elf.strip():
        extra_elf = Path(args.extra_elf).resolve()
        if not extra_elf.is_file():
            parser.error(f"--extra-elf: file not found: {extra_elf}")
    app = args.app
    if app in EXTRA_DEMO_APP and extra_elf is None:
        parser.error(f"{app} requires --extra-elf ({EXTRA_DEMO_APP[app]})")
    elif extra_elf is not None and app not in EXTRA_DEMO_APP:
        parser.error("--extra-elf requires a dual-device --app")

    try:
        if args.provision:
            from demo_runner import run_provision

            run_provision(
                matter_elf, args.nvm3_hex, board=args.board,
                provision_image=args.provision_image,
            )
            print("Provisioning session completed")
            return 0

        from demo_runner import run_demo

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
        print(f"{'Provisioning' if args.provision else 'Demo'} session failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
