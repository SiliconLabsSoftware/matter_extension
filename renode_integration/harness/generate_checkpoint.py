#!/usr/bin/env python3
"""Generate a Renode checkpoint with Linux booted and Thread network formed."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from renode_harness import RenodeHarness

SCRIPT_DIR = Path(__file__).resolve().parent
INTEGRATION_DIR = SCRIPT_DIR.parent
DEFAULT_BUNDLE = INTEGRATION_DIR / "out" / "bundle"


def resolve_renode(bundle_dir: Path) -> Path:
    override = os.environ.get("RENODE")
    if override:
        return Path(override)
    host = os.environ.get("HOST")
    if not host:
        uname = os.uname()
        if uname.sysname == "Darwin" and uname.machine == "arm64":
            host = "osx-arm64"
        elif uname.sysname == "Linux" and uname.machine in ("x86_64", "amd64"):
            host = "linux-x64"
        else:
            host = f"{uname.sysname.lower()}-{uname.machine}"
    candidate = bundle_dir / "renode" / "renode"
    if candidate.exists():
        return candidate
    built = INTEGRATION_DIR / "out" / "renode" / host / "renode"
    if built.exists():
        return built
    raise FileNotFoundError("renode binary not found, run scripts/build_renode.py or set RENODE=")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Matter Renode checkpoint")
    parser.add_argument("--bundle-dir", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="checkpoint path (default: <bundle>/linux-booted-thread.save)",
    )
    args = parser.parse_args()

    bundle_dir = args.bundle_dir.resolve()
    checkpoint = args.output or (bundle_dir / "linux-booted-thread.save")
    # $root in the resc is the parent of the script, so this must be the bundle copy.
    resc = bundle_dir / "resc" / "matter-sim-full.resc"
    if not resc.is_file():
        raise FileNotFoundError(f"{resc} not found, assemble the bundle or run scripts/fetch_bundle.py")
    renode_bin = resolve_renode(bundle_dir)

    harness = RenodeHarness(renode_bin=renode_bin, resc=resc, bundle_dir=bundle_dir)
    console = None
    try:
        print(f"Starting Renode: {renode_bin}")
        harness.start()
        console = harness.hub_console_session()
        console.wait_for_line(r"matter-services: READY", timeout_s=600)
        console.login_root()
        console.run_and_wait("matter-thread-init", r"matter-thread-init: READY", timeout_s=180)
        harness.monitor_command("pause")
        harness.monitor_command(f"Save @{checkpoint}")
        print(f"Saved checkpoint: {checkpoint}")

        runtime_manifest = bundle_dir / "runtime-manifest.json"
        manifest = {
            "checkpoint": str(checkpoint.name),
            "renode": str(renode_bin),
        }
        if (bundle_dir / "renode" / "manifest.json").exists():
            manifest["renode_build"] = json.loads(
                (bundle_dir / "renode" / "manifest.json").read_text(encoding="utf-8")
            )
        runtime_manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return 0
    finally:
        if console is not None:
            console.close()
        harness.stop()


if __name__ == "__main__":
    sys.exit(main())
