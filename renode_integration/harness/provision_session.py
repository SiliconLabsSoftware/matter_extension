#!/usr/bin/env python3
"""
@file provision_session.py
@brief Open a manual provisioning session through the shared pyrenode3 harness.

Opens an interactive shell inside the simulated hub before Matter commissioning.
Provisioning commands and verification are performed manually by the operator.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matter-elf", type=Path, required=True)
    parser.add_argument("--nvm3-hex", type=Path, required=True)
    parser.add_argument("--board", default="brd4187c")
    parser.add_argument("--bundle-dir", type=Path, help="Override the default out/bundle directory")
    parser.add_argument("--provision-image", type=Path, help="Override the bundle provisioning disk")
    parser.add_argument("--timeout", type=float, default=600, help="Per-operation UART timeout in seconds")
    args = parser.parse_args()
    if not sys.stdin.isatty():
        parser.error("manual provisioning requires an interactive terminal")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    for name in ("matter_elf", "nvm3_hex", "provision_image"):
        value = getattr(args, name)
        if value is not None:
            value = value.resolve()
            if not value.is_file():
                parser.error(f"{name.replace('_', '-')}: file not found: {value}")
            setattr(args, name, value)

    # Parse arguments before importing the runtime so --help and input errors
    # remain usable without an installed Renode bundle.
    try:
        # matter_sim imports test_lib, which initializes pyrenode3. Configure a
        # custom bundle before that import, just as its default bootstrap does.
        if args.bundle_dir is not None:
            renode_root = args.bundle_dir.resolve() / "renode"
            binary = renode_root / "renode"
            if not binary.is_file():
                raise FileNotFoundError(f"renode binary not found: {binary}")
            os.environ["PYRENODE_PATH"] = str(binary)
            os.environ["RENODE_BASE_PATH"] = str(renode_root) + os.sep
        from matter_sim import DEFAULT_BUNDLE, MatterSim, configure_renode_env, run_shell

        bundle = (args.bundle_dir or DEFAULT_BUNDLE).resolve()
        configure_renode_env(bundle)
        import test_lib

        sim = MatterSim(bundle, socket_consoles=True)
        try:
            sim.load_thread_checkpoint()
            hub = sim.hub_uart(args.timeout)
            test_lib.write_line(hub, "")
            if test_lib.wait_for(hub, r"#\s*$", timeout=args.timeout) is None:
                raise RuntimeError("hub shell did not become ready")
            sim.attach_provision_image(args.provision_image)
            sim.mount_provision(hub, args.timeout)

            sim.pause()
            sim.attach_matter_soc(args.board, args.matter_elf, extra_hex=args.nvm3_hex)
            sim.soc_uart(args.timeout)
            sim.start()
            print(
                "Manual provisioning session; device has not been commissioned.\n"
                "Wait for provisioning readiness and read the BLE address from the SoC UART log.\n"
                "Enter non-interactive guest shell commands; exit, Ctrl-D or Ctrl-C closes."
            )
            while True:
                try:
                    command = input("hub> ").strip()
                except EOFError:
                    break
                if command in ("exit", "quit"):
                    break
                if command:
                    try:
                        rc, report = run_shell(hub, command, args.timeout)
                        if rc != 0:
                            print(f"Guest command failed (rc={rc})\n{report[-2000:]}", file=sys.stderr)
                    except RuntimeError as exc:
                        print(f"Command failed: {exc}", file=sys.stderr)
        finally:
            sim.close()
        print("Provisioning session completed")
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"Provisioning session failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
