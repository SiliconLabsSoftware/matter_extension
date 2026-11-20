"""
@file renode_runner.py
@brief Run Matter Renode demo flows and manual provisioning sessions.

Loads demo_flows.yaml for post-commission verification and drives MatterSim UART
sessions against the bundled linux-booted-thread checkpoint.
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

from renode_config import DEMO_FLOWS, SANITY_FLOWS

import matter_sim
from matter_sim import DEFAULT_BUNDLE, DEFAULT_UART_TIMEOUT_S, MatterSim, run_shell

import test_lib

NODE_ID = 101
PASSCODE = "20202021"
DISCRIMINATOR = "3840"
COMMISSION_TIMEOUT_S = 1200
STEP_TIMEOUT_S = 300


def commission(hub: object, node_id: int, timeout_s: float = COMMISSION_TIMEOUT_S) -> None:
    pair_cmd = (
        f"chip-tool pairing ble-thread {node_id} "
        f'"hex:$(cat /tmp/thread-dataset.hex)" {PASSCODE} {DISCRIMINATOR}'
    )
    print(f"Running: {pair_cmd}")
    pair_rc, pair_out = run_shell(hub, pair_cmd, timeout_s=timeout_s)
    if pair_rc != 0:
        raise RuntimeError(f"commissioning node {node_id} failed (rc={pair_rc})\n{pair_out[-2000:]}")


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def _response_fingerprint(report: str) -> str:
    payloads = []
    for line in _strip_ansi(report).splitlines():
        if "[TOO]" not in line:
            continue
        payload = line.split("[TOO]", 1)[1].strip()
        if re.match(r"^(?:Device|Endpoint|Cluster|Attribute|DataVersion):", payload):
            continue
        if payload:
            payloads.append(payload)
    return "\n".join(payloads)


def _read_fingerprint(rc: int, report: str) -> str:
    fingerprint = _response_fingerprint(report)
    if rc != 0 or not fingerprint or re.search(
        r"Run command failure|status\s*=\s*0x(?!0+\b)[0-9a-f]+", report, re.I
    ):
        raise RuntimeError(f"attribute read failed (rc={rc})\n{report[-2000:]}")
    return fingerprint


def _format_command(command: str, ctx: dict[str, str]) -> str:
    try:
        return command.format(**ctx)
    except KeyError as exc:
        raise RuntimeError(f"missing flow variable {exc} for command {command!r}") from exc


def _hub_uart(
    sim: MatterSim,
    timeout_s: float = DEFAULT_UART_TIMEOUT_S,
    *,
    require_prompt: bool = False,
) -> object:
    hub = sim.hub_uart(timeout_s)
    test_lib.write_line(hub, "")
    ready = test_lib.wait_for(hub, r"#\s*$", timeout=timeout_s)
    if require_prompt and ready is None:
        raise RuntimeError("hub shell did not become ready")
    return hub


def run_hub_step(
    step: dict[str, Any],
    hub: object,
    ctx: dict[str, str],
    *,
    timeout_s: float = STEP_TIMEOUT_S,
) -> None:
    step_type = step.get("type")
    if step_type == "readonly_pair":
        _run_readonly_pair(step, hub, ctx, timeout_s=timeout_s)
        return

    command = _format_command(step["command"], ctx)
    print(f"Running: {command}")
    rc, report = run_shell(hub, command, timeout_s)

    if step.get("skip_if_status") and re.search(step["skip_if_status"], report, re.I):
        print(f"Skipping step (matched {step['skip_if_status']!r})")
        return

    expect_status = step.get("expect_status")
    if expect_status:
        if not re.search(re.escape(expect_status), report, re.I):
            raise RuntimeError(f"expected status {expect_status!r} in output\n{report[-2000:]}")
        return

    if step.get("expect_failure"):
        if not re.search(r"UNSUPPORTED_WRITE|Run command failure", report):
            raise RuntimeError(f"expected command failure in output\n{report[-2000:]}")
        return

    cleaned_report = _strip_ansi(report)
    if expect := step.get("expect"):
        if not re.search(expect, cleaned_report):
            raise RuntimeError(f"pattern {expect!r} not found\n{report[-2000:]}")

    if extract := step.get("extract"):
        for key, pattern in extract.items():
            match = re.search(pattern, cleaned_report, re.DOTALL)
            if not match:
                raise RuntimeError(f"extract {key!r} failed for pattern {pattern!r}\n{report[-2000:]}")
            ctx[key] = match.group(1)

    if rc != 0 and not step.get("allow_nonzero_rc"):
        if "status = 0x00 (SUCCESS)" not in cleaned_report:
            raise RuntimeError(f"command failed with exit code {rc}\n{report[-2000:]}")


def _run_readonly_pair(
    step: dict[str, Any],
    hub: object,
    ctx: dict[str, str],
    *,
    timeout_s: float,
) -> None:
    read_cmd = _format_command(step["read"], ctx)
    write_cmd = _format_command(step["write"], ctx)
    print(f"Running: {read_cmd}")
    read_rc, read_out = run_shell(hub, read_cmd, timeout_s)
    if step.get("skip_if_unsupported") and re.search(r"UNSUPPORTED_ATTRIBUTE", read_out):
        print("Skipping optional attribute (unsupported on DUT)")
        return

    baseline = _read_fingerprint(read_rc, read_out)
    print(f"Running: {write_cmd}")
    write_rc, write_out = run_shell(hub, write_cmd, timeout_s)
    if not step.get("writable"):
        if not re.search(r"\bUNSUPPORTED_WRITE\b|status\s*=\s*0x0*88\b", write_out, re.I):
            raise RuntimeError(f"expected unsupported write\n{write_out[-2000:]}")

    elif write_rc != 0:
        raise RuntimeError(f"attribute write failed (rc={write_rc})\n{write_out[-2000:]}")

    print(f"Running: {read_cmd}")
    read_again_rc, read_again = run_shell(hub, read_cmd, timeout_s)
    again = _read_fingerprint(read_again_rc, read_again)
    if step.get("writable"):
        expect = step.get("expect_after_write", "")
        if expect and not re.search(re.escape(expect), _strip_ansi(read_again)):
            raise RuntimeError(f"expected {expect!r} after write\n{read_again[-2000:]}")
    else:
        if again != baseline:
            raise RuntimeError("attribute changed after unsupported write\n" f"before:\n{baseline}\nafter:\n{again}")


def run_sanity_steps(steps: list[dict[str, Any]], hub: object) -> None:
    ctx: dict[str, str] = {}
    for step in steps:
        run_hub_step(step, hub, ctx)


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


def run_demo(
    elf: Path,
    app: str | None,
    *,
    extra_elf: Path | None = None,
    board: str,
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
        hub = _hub_uart(sim)

        if dual:
            # Both ELFs use the same commissioning identity. Pair the light
            # before attaching the switch so discovery has a single candidate.
            sim.attach_matter_soc(
                board, extra_elf.resolve(), machine_name="matter_soc_light", cli_port=3453
            )
            sim.soc_uart(machine_name="matter_soc_light")
            commission(hub, light_node)

        sim.attach_matter_soc(board, elf)
        soc = sim.soc_uart()
        commission(hub, switch_node if dual else NODE_ID)
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
            print("Device commissioned. Enter hub shell commands. exit, Ctrl-D, or Ctrl-C to close.")
            matter_sim.interactive_hub(hub, STEP_TIMEOUT_S)
    finally:
        sim.close()


def run_provision(
    matter_elf: Path,
    nvm3_hex: Path,
    *,
    board: str = "brd4187c",
    provision_image: Path | None = None,
    timeout: float = DEFAULT_UART_TIMEOUT_S,
) -> None:
    """Mount provisioning tools and open the hub prompt with an uncommissioned SoC."""
    sim = MatterSim(DEFAULT_BUNDLE, socket_consoles=True)
    try:
        sim.load_thread_checkpoint()
        hub = _hub_uart(sim, timeout, require_prompt=True)
        sim.attach_provision_image(provision_image)
        sim.mount_provision(hub, timeout)

        sim.pause()
        sim.attach_matter_soc(board, matter_elf, extra_hex=nvm3_hex)
        sim.soc_uart(timeout)
        sim.start()
        print(
            "Manual provisioning session, device has not been commissioned.\n"
            "Wait for provisioning readiness and read the BLE address from the SoC UART log.\n"
            "Enter non-interactive guest shell commands. exit, Ctrl-D or Ctrl-C closes."
        )
        matter_sim.interactive_hub(hub, timeout)
    finally:
        sim.close()


def run_sanity_commission(
    elf: Path,
    *,
    board: str,
    save_path: Path,
) -> None:
    """Commission, run commission verification steps, and save a commissioned checkpoint."""
    elf = elf.resolve()
    save_path = save_path.resolve()
    flow = SANITY_FLOWS["test_tc_commission"]
    sim = MatterSim(DEFAULT_BUNDLE, socket_consoles=False)
    try:
        sim.load_thread_checkpoint()
        hub = _hub_uart(sim)
        sim.attach_matter_soc(board, elf)
        sim.soc_uart()
        commission(hub, NODE_ID)
        run_sanity_steps(flow["steps"], hub)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        sim.save(save_path)
        print(f"Saved commissioned checkpoint: {save_path}")
    finally:
        sim.close()


def run_sanity_test(name: str, checkpoint: Path) -> None:
    """Restore a commissioned checkpoint and run one sanity flow."""
    if name not in SANITY_FLOWS:
        raise ValueError(f"unknown sanity test {name!r}")
    if name == "test_tc_commission":
        raise ValueError("test_tc_commission runs only in --sanity-commission mode")
    checkpoint = checkpoint.resolve()
    if not checkpoint.is_file():
        raise FileNotFoundError(f"checkpoint not found: {checkpoint}")

    flow = SANITY_FLOWS[name]
    sim = MatterSim(DEFAULT_BUNDLE, socket_consoles=False)
    try:
        sim.load_thread_checkpoint(checkpoint=checkpoint)
        hub = _hub_uart(sim)
        sim.soc_uart()
        run_sanity_steps(flow["steps"], hub)
    finally:
        sim.close()
