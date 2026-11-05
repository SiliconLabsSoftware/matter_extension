---
name: slab-matter-hub
description: >-
  Commission and control Silicon Labs Matter over Thread or Wi-Fi end devices through
  the Matter Hub (Raspberry Pi OTBR + chip-tool) via SSH from the developer machine
  (Windows, Linux, or macOS). Requires one-time user Matter Hub SSH setup before
  the agent can run hub.py. Use when the user asks to commission, pair, or control
  a Matter device with chip-tool, mattertool, or the Matter Hub after build/flash.
---

# Matter Hub chip-tool

## Agent: hub must be configured first (non-negotiable)

Matter Hub access is a **one-time manual setup by the user**. The agent does **not** discover the Raspberry Pi.

**Never** run ping, ARP tables, mDNS browse tools (`dns-sd`, `avahi-browse`, etc.), nmap, subnet scans, or other LAN probes to find the Pi.

**Only** use `hub.py` subcommands (see [Executor](#executor)).

Before commissioning or `run`, call `hub.py check` once. If it fails (non-zero exit) with messages such as `No Matter Hub host in ~/.silabs/matter-hub.json` or `Permission denied`:

1. Stop the chip-tool workflow (no commission, no `run`, no retries with network tools).
2. Give the user the [one-time setup](#one-time-hub-setup-user-not-agent) steps verbatim. Do not improvise discovery or guess HOST.
3. Wait until the user confirms setup is done, then run `check` again.

Only the **user** writes the hub config: `hub.py discover --host HOST` after SSH key setup. The agent sends the user **HOST** only inside the setup instructions, it does not run `discover` itself.

Treat hub setup as **complete** only after `hub.py check` succeeds. Until then, do not run `dataset`, `commission-thread`, `commission-wifi`, `run`, or `logs`.

## Purpose

Run chip-tool on the user's [Matter Hub](https://docs.silabs.com/matter/latest/matter-thread/raspi-img) over SSH. Each command is one SSH session that exits when chip-tool or `ot-ctl` finishes. Fabric state lives on the Pi under `/tmp`, not on the developer machine.

Out of scope:

- Building or flashing firmware (use other Silicon Labs agent skills)
- Installing chip-tool on the developer machine
- `chip-tool interactive start`, tmux, or long-lived SSH shells
- Sourcing [mattertool](tools/matter_rpi_image/scripts/matterTool.sh) over SSH (shell variables do not persist)

In scope:

- Hub connectivity check after user configuration (`check`)
- Thread dataset read and optional new network formation
- BLE-Thread and BLE-Wi-Fi commissioning
- Arbitrary chip-tool cluster commands
- Bounded OTBR journal logs

## Resolve Matter transport (Thread vs Wi-Fi)

Do **not** guess `commission-thread` vs `commission-wifi`. Pick exactly one pairing mode before commissioning in the [default workflow](#default-workflow).

**Do not infer transport.** If it is not abundantly clear (below), **ask the user** and wait for an answer before any `commission-thread` or `commission-wifi` call.

### Abundantly clear (proceed without asking)

Use **Thread** when any of these is true:

- The user states Thread, OTBR, operational dataset, or `ble-thread`.
- The user names or points to a **Thread sample application** as the image they built or flashed.

Use **Wi-Fi** when any of these is true:

- The user states Wi-Fi, WLAN, or `ble-wifi`, or supplies infrastructure **SSID and password** for commissioning.
- The user names or points to a **Wi-Fi sample application** as the image they built or flashed.

When transport is abundantly clear, state it in one line and continue. Skip asking.

### Not abundantly clear (ask, do not infer)

If none of the above applies, ask once:

**“Should I commission over Matter Thread (`commission-thread` + hub dataset) or Matter Wi-Fi (`commission-wifi` + your SSID/password)?”**

Do not run `commission-thread` or `commission-wifi` until the user answers.

If the user later references both transports or an ambiguous app, ask which operational network to use (Thread dataset vs Wi-Fi credentials).

Record the chosen transport in the session (for example `transport=thread`) so later `run` and `show-node-id` stay consistent. Do not store transport in `matter-hub.json`.

## Executor

Run from the workspace root with **Python 3**. Use `python3` on Linux/macOS or `python` on Windows if that is how Python 3 is installed:

```bash
python3 .agents/skills/slab-matter-hub/scripts/hub.py <subcommand> [args]
```

`hub.py` uses the system `ssh` client. Stdlib only. SSH targets the LAN. If the sandbox blocks the Pi, rerun with unrestricted network permissions.

Hub constants (on the Raspberry Pi image, not overridden in config):

- User: `ubuntu`
- chip-tool: `/home/ubuntu/connectedhomeip/out/standalone/chip-tool`

Hub address: sole source is `matter-hub.json` under the Silabs config directory (`~/.silabs/` on Unix, `%USERPROFILE%\.silabs\` on Windows), field `host`. **Only** `discover --host HOST` writes this file (user action). All other subcommands read it. No environment overrides and no `--host` on agent commands.

## One-time hub setup (user, not agent)

Canonical step text is `HUB_SETUP_STEPS` in [scripts/hub.py](scripts/hub.py). The agent must **not** paraphrase it or paste Python source (no `f"""`, `{HUB_SCRIPT}`, or escapes).

**How to give setup steps to the user:** Run `hub.py check` (or any hub command that fails for missing config or SSH auth). Send the setup section from **stderr** verbatim (after the one-line reason). `print_user_setup` in `hub.py` emits the same text as `HUB_SETUP_STEPS`.

The user replaces `HOST` with their Matter Hub IP. The agent does **not** run `discover` or choose HOST.

Dedicated SSH key for the hub only (not GitHub/corporate defaults). `hub.py` uses `BatchMode=yes` (no password prompts). On `Permission denied`, stop after sending setup text. No `sshpass`, no password in chat.

`discover` without `--host` only prints the saved host from JSON (user convenience). It does not update the file.

`check` also runs `sudo -n ot-ctl state`. It does not write `matter-hub.json`. If sudo needs a password, stop and tell the user. Do not commission.

## Subcommands

| Subcommand | Purpose |
|------------|---------|
| `discover` | **User only:** `discover --host HOST` writes JSON, `discover` alone prints saved host. Agent must not run `discover` |
| `check` | Agent: verify hub from JSON (key auth, chip-tool, `sudo -n ot-ctl state`) |
| `dataset` | Print active Thread operational dataset (hex) |
| `start-thread` | Factory-reset OTBR and form a new Thread network (destructive, user must ask) |
| `commission-thread` | BLE-Thread pair. Writes last node id on the Pi |
| `commission-wifi` | BLE-Wi-Fi pair. Writes last node id on the Pi |
| `run` | Pass remaining args to chip-tool |
| `show-node-id` | Read last node id from `/tmp/last-node-id` on the hub |
| `logs` | Last 200 lines of `otbr-agent` journal |

### `commission-thread`

Defaults: pin `20202021`, discriminator `3840`. Options: `--node-id`, `--pin`, `--discriminator`, `--dataset` (hex without `hex:` prefix).

Uses dataset from `--dataset`, else `dataset` subcommand output. Blocks until chip-tool exits (up to 180s). Saves node id to `/tmp/last-node-id` on the Pi.

### `commission-wifi`

Required: `--ssid`, `--password` (infrastructure Wi-Fi, device and hub must reach the same network). Defaults: pin `20202021`, discriminator `3840`. Options: `--node-id`, `--pin`, `--discriminator`.

Blocks until chip-tool exits (up to 180s). Saves node id to `/tmp/last-node-id` on the Pi.

### `run`

Forwards argv to chip-tool. Example:

```bash
python3 .agents/skills/slab-matter-hub/scripts/hub.py run onoff on 1 1
```

If the user omits node id, read last id from the Pi with `hub.py show-node-id` or reuse the node id from `commission-thread` or `commission-wifi`.

## Consent

- Run `start-thread` only when the user explicitly wants a new Thread network.
- Do not factory-reset OTBR to fix a failed commission without asking.

## Default workflow

After the Matter app is built, flashed, and advertising:

1. `check` (if it fails, send stderr setup text verbatim and stop)
2. [Resolve Matter transport](#resolve-matter-transport-thread-vs-wi-fi). Ask when it is not abundantly clear.

**Thread end device:**

3. `dataset` (or `start-thread` only if requested)
4. `commission-thread` with `--pin` / `--discriminator` from the user when not using hub defaults (`20202021`, `3840`)

**Wi-Fi end device:**

3. `commission-wifi --ssid SSID --password PASSWORD` with `--pin` / `--discriminator` from the user when not using hub defaults

**Both:**

5. `run` for cluster commands
6. `logs` if OTBR-side diagnosis is needed (Thread only)

## Pairing reference

Thread BLE (hub runs chip-tool):

```text
pairing ble-thread <node_id> hex:<dataset> <pin> <discriminator>
```

`hub.py commission-thread` builds the Thread command. 

Wi-Fi BLE (hub runs chip-tool):

```text
pairing ble-wifi <node_id> <ssid> <password> <pin> <discriminator>
```

`hub.py commission-wifi` builds the Wi-Fi command.

## Logs

- chip-tool output: stdout of `run`, `commission-thread`, and `commission-wifi`
- OTBR: `logs` subcommand (`journalctl -u otbr-agent --no-pager -n 200`)
- Do not run `journalctl -f` or `tail -f`
