#!/usr/bin/env python3
"""
@file renode_test.py
@brief Matter Renode demo CLI (CI and local): checkpoint, ELF, demo flow or interactive hub commands.

Entry point for demo tests, commissioned interactive sessions, and manual provisioning.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from renode_config import DEMO_APPS, EXTRA_DEMO_APP, SANITY_MATRIX_TESTS


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
    parser.add_argument("--matter-elf", type=Path, default=None)
    parser.add_argument(
        "--extra-elf",
        default="",
        metavar="PATH",
        help="Second SoC ELF (required when --app has a paired demo binary)",
    )
    parser.add_argument("--board", default=None, help="SoC board repl name, e.g. brd4187c")
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
    parser.add_argument(
        "--sanity-commission",
        action="store_true",
        help="Commission lighting app and save a checkpoint for sanity tests",
    )
    parser.add_argument("--save", type=Path, help="Checkpoint path for --sanity-commission")
    parser.add_argument(
        "--sanity-test", choices=SANITY_MATRIX_TESTS,
        help="Run one sanity test from sanity_flows.yaml",
    )
    parser.add_argument("--checkpoint", type=Path, help="Commissioned checkpoint for --sanity-test")
    args = parser.parse_args()

    sanity_mode = args.sanity_commission or args.sanity_test is not None
    if sanity_mode:
        if args.app or args.interactive or args.provision:
            parser.error("sanity modes cannot combine with --app, --interactive, or --provision")
        if args.sanity_commission and None in (args.matter_elf, args.board, args.save):
            parser.error("--sanity-commission requires --matter-elf, --board, and --save")
        if args.sanity_test and args.checkpoint is None:
            parser.error("--sanity-test requires --checkpoint")

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

    if not sanity_mode and args.app is None and not args.interactive and not args.provision:
        parser.error("specify --app, --interactive, --provision, or a sanity mode")
    if not sanity_mode and (args.matter_elf is None or args.board is None):
        parser.error("demo and provision modes require --matter-elf and --board")

    matter_elf: Path | None = None
    if args.matter_elf is not None:
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

    if args.sanity_commission:
        mode = "Sanity commission"
    elif args.sanity_test:
        mode = f"Sanity test {args.sanity_test}"
    elif args.provision:
        mode = "Provisioning session"
    else:
        mode = f"Demo session for {app or 'custom'}"

    try:
        if args.sanity_commission:
            from renode_runner import run_sanity_commission

            run_sanity_commission(matter_elf, board=args.board, save_path=args.save)
        elif args.sanity_test:
            from renode_runner import run_sanity_test

            run_sanity_test(args.sanity_test, args.checkpoint)
        elif args.provision:
            from renode_runner import run_provision

            run_provision(
                matter_elf, args.nvm3_hex, board=args.board,
                provision_image=args.provision_image,
            )
        else:
            from renode_runner import run_demo

            run_demo(
                matter_elf,
                app,
                extra_elf=extra_elf,
                board=args.board,
                interactive=args.interactive,
            )
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"{mode} failed: {exc}", file=sys.stderr)
        return 1

    result = "completed" if args.provision else "succeeded"
    print(f"{mode} {result}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
