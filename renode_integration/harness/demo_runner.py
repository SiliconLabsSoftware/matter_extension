"""
@file demo_runner.py
@brief Run Matter Renode demo flows (checkpoint, commission, chip-tool / shell steps).

Loads demo_flows.yaml for post-commission verification and drives MatterSim UART
sessions against the bundled linux-booted-thread checkpoint.
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path
from typing import Any

from demo_config import DEMO_FLOWS

from matter_sim import DEFAULT_BUNDLE, DEFAULT_UART_TIMEOUT_S, MatterSim, run_shell

import test_lib

NODE_ID = 101
PASSCODE = "20202021"
DISCRIMINATOR = "3840"
COMMISSION_TIMEOUT_S = 1200
STEP_TIMEOUT_S = 300


def _commission(hub: object, node_id: int, timeout_s: float = COMMISSION_TIMEOUT_S) -> None:
    pair_cmd = (
        f"chip-tool pairing ble-thread {node_id} "
        f'"hex:$(cat /tmp/thread-dataset.hex)" {PASSCODE} {DISCRIMINATOR}'
    )
    print(f"Running: {pair_cmd}")
    pair_rc, pair_out = run_shell(hub, pair_cmd, timeout_s=timeout_s)
    if pair_rc != 0:
        raise RuntimeError(f"commissioning node {node_id} failed (rc={pair_rc})\n{pair_out[-2000:]}")


def _chip_tool_subject_from_acl(report: str) -> int | None:
    match = re.search(r"Subjects:\s*\d+\s+entries.*?\[1\]:\s*(\d+)", report, re.DOTALL | re.I)
    return int(match.group(1)) if match else None


def _grant_switch_acl_on_light(hub: object, light_node: int, switch_node: int) -> None:
    read_cmd = f"chip-tool accesscontrol read acl {light_node} 0"
    print(f"Running: {read_cmd}")
    read_rc, report = run_shell(hub, read_cmd, timeout_s=STEP_TIMEOUT_S)
    if read_rc != 0:
        raise RuntimeError(f"ACL read failed (rc={read_rc})\n{report[-2000:]}")
    chip_tool_id = _chip_tool_subject_from_acl(report)
    if chip_tool_id is None:
        raise RuntimeError(f"could not parse chip-tool subject from ACL\n{report[-2000:]}")
    acl_json = (
        f'[{{"fabricIndex": 1, "privilege": 5, "authMode": 2, "subjects": [{chip_tool_id}], '
        f'"targets": null}},{{"fabricIndex": 1, "privilege": 3, "authMode": 2, '
        f'"subjects": [{switch_node}], "targets": null}}]'
    )
    write_cmd = f"chip-tool accesscontrol write acl '{acl_json}' {light_node} 0"
    print(f"Running: {write_cmd}")
    write_rc, write_out = run_shell(hub, write_cmd, timeout_s=STEP_TIMEOUT_S)
    if write_rc != 0:
        raise RuntimeError(f"ACL write failed (rc={write_rc})\n{write_out[-2000:]}")


def _onoff_value_from_report(report: str) -> str | None:
    values = re.findall(r"\b(?:OnOff|value):\s*(TRUE|FALSE|1|0)\b", report, re.I)
    if not values:
        return None
    return "1" if values[-1].upper() in ("TRUE", "1") else "0"


def _wait_for_onoff_change(
    hub: object, command: str, prior_onoff: str | None, timeout_s: float
) -> str:
    if prior_onoff is None:
        raise RuntimeError("missing on-off baseline for toggle comparison")
    deadline = time.monotonic() + timeout_s
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError(f"on-off value did not change (still {prior_onoff})")
        rc, report = run_shell(hub, command, timeout_s=remaining)
        if rc != 0:
            raise RuntimeError(f"on-off read failed with exit code {rc}\n{report[-2000:]}")
        after = _onoff_value_from_report(report)
        if after is None:
            raise RuntimeError(f"could not parse on-off read\n{report[-2000:]}")
        if after != prior_onoff:
            return after
        time.sleep(min(1.0, max(0.0, deadline - time.monotonic())))


def _run_step(
    step: dict[str, Any],
    hub: object,
    soc: object | None,
    soc_light: object | None,
    prior_onoff: str | None,
) -> str | None:
    command = step["command"]
    uart = step.get("uart", "hub")
    expect = step.get("expect")
    expect_onoff_change = step.get("expect_onoff_change", False)
    timeout_s = float(step.get("timeout_s", STEP_TIMEOUT_S))

    if uart == "hub":
        print(f"Running: {command}")
        if expect_onoff_change:
            return _wait_for_onoff_change(hub, command, prior_onoff, timeout_s)
        rc, report = run_shell(hub, command, timeout_s=timeout_s)
        if expect is not None and not re.search(expect, report):
            raise RuntimeError(f"step failed: pattern {expect!r} not found\n{report[-2000:]}")
        if rc != 0:
            raise RuntimeError(f"step failed with exit code {rc}\n{report[-2000:]}")
        return prior_onoff

    if uart not in ("soc", "soc_light"):
        raise ValueError(f"unknown UART {uart!r}")
    tester = soc if uart == "soc" else soc_light
    if tester is None:
        raise RuntimeError(f"no UART tester for {uart}")
    print(f"SoC command: {command}")
    test_lib.write_line(tester, command)
    report = str(tester.GetReport())
    if expect is not None:
        matched = test_lib.wait_for(tester, expect, timeout=timeout_s)
        if matched is None:
            raise RuntimeError(f"step failed: pattern {expect!r} not found\n{report[-2000:]}")
    else:
        if test_lib.wait_for(tester, r"chip>\s*$|>\s*$", timeout=timeout_s) is None:
            raise RuntimeError("step failed: SoC command prompt not received")
    return prior_onoff


def _interactive_hub(hub: object) -> None:
    print("Device commissioned. Enter hub shell commands. exit, Ctrl-D, or Ctrl-C to close.")
    try:
        while True:
            command = input("hub> ").strip()
            if command in ("exit", "quit"):
                return
            if not command:
                continue
            try:
                _run_step({"command": command}, hub, None, None, None)
            except RuntimeError as exc:
                print(f"Command failed: {exc}", file=sys.stderr)
    except (EOFError, KeyboardInterrupt):
        print()


def run_demo(
    elf: Path,
    app: str | None,
    *,
    extra_elf: Path | None = None,
    board: str = "brd4187c",
    interactive: bool = False,
) -> None:
    """Commission, then run the demo flow or an interactive hub session."""
    elf = elf.resolve()
    flow = DEMO_FLOWS[app] if app else None
    if flow is None and not interactive:
        raise ValueError("nothing to run: pass --app or --interactive")

    dual = bool(flow and flow.get("extra_app"))
    if dual and extra_elf is None:
        raise ValueError(f"{app} requires its companion ELF ({flow['extra_app']})")
    if extra_elf is not None and not dual:
        raise ValueError("companion ELF supplied for an app without a companion")
    if dual:
        light_node = int(flow["light_node"])
        switch_node = int(flow["switch_node"])

    sim = MatterSim(DEFAULT_BUNDLE, socket_consoles=interactive)
    try:
        sim.load_thread_checkpoint()
        hub = sim.hub_uart()

        test_lib.write_line(hub, "")
        test_lib.wait_for(hub, r"#\s*$", timeout=DEFAULT_UART_TIMEOUT_S)

        if dual:
            # Both ELFs use the same commissioning identity. Pair the light
            # before attaching the switch so discovery has a single candidate.
            sim.attach_matter_soc(
                board, extra_elf.resolve(), machine_name="matter_soc_light", cli_port=3453
            )
            sim.soc_uart(machine_name="matter_soc_light")
            _commission(hub, light_node)

        sim.attach_matter_soc(board, elf)
        soc = sim.soc_uart()
        _commission(hub, switch_node if dual else NODE_ID)
        if dual:
            _grant_switch_acl_on_light(hub, light_node, switch_node)

        steps = flow["steps"] if flow and not interactive else []
        if dual:
            onoff_before = None
            for step in steps:
                if step.get("command") == "switch onoff toggle":
                    baseline_cmd = f"chip-tool onoff read on-off {light_node} 1"
                    read_rc, read_out = run_shell(hub, baseline_cmd, STEP_TIMEOUT_S)
                    if read_rc != 0:
                        raise RuntimeError(f"on-off baseline read failed\n{read_out[-2000:]}")
                    onoff_before = _onoff_value_from_report(read_out)
                    if onoff_before is None:
                        raise RuntimeError(f"could not parse on-off baseline\n{read_out[-2000:]}")
                onoff_before = _run_step(step, hub, soc, None, onoff_before)
        else:
            for step in steps:
                _run_step(step, hub, None, None, None)

        if interactive:
            _interactive_hub(hub)
    finally:
        sim.close()
