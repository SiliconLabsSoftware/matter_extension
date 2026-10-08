---
name: slab-chip-tool
description: >-
  Commission and control Silicon Labs Matter over Thread end devices through the
  Matter Hub (Raspberry Pi OTBR + chip-tool) via SSH from the developer machine
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
2. Give the user the [one-time setup](#one-time-hub-setup-user-not-agent) block below. Do not improvise discovery.
3. Wait until the user confirms setup is done, then run `check` again.

Only the **user** writes the hub config: `hub.py discover --host HOST` after SSH key setup. The agent sends the user **HOST** only inside the setup instructions, it does not run `discover` itself.

Treat hub setup as **complete** only after `hub.py check` succeeds. Until then, do not run `dataset`, `commission-thread`, `run`, or `logs`.

## Purpose

Run chip-tool on the user's [Matter Hub](https://docs.silabs.com/matter/latest/matter-thread/raspi-img) over SSH. Each command is one SSH session that exits when chip-tool or `ot-ctl` finishes. Fabric state lives on the Pi under `/tmp`, not on the developer machine.

Out of scope:

- Building or flashing firmware (use SLC / SDM skills)
- Installing chip-tool on the developer machine
- `chip-tool interactive start`, tmux, or long-lived SSH shells
- Sourcing [mattertool](tools/matter_rpi_image/scripts/matterTool.sh) over SSH (shell variables do not persist)

In scope:

- Hub connectivity check after user configuration (`check`)
- Thread dataset read and optional new network formation
- BLE-Thread commissioning
- Arbitrary chip-tool cluster commands
- Bounded OTBR journal logs

End-device UART logs stay on the kit via the SDM skill.

## Executor

Run from the workspace root with **Python 3**. Use `python3` on Linux/macOS or `python` on Windows if that is how Python 3 is installed:

```bash
python3 .cursor/skills/chip-tool/scripts/hub.py <subcommand> [args]
```

`hub.py` uses the system `ssh` client. Stdlib only. SSH targets the LAN. If the sandbox blocks the Pi, rerun with unrestricted network permissions.

Hub constants (on the Raspberry Pi image, not overridden in config):

- User: `ubuntu`
- chip-tool: `/home/ubuntu/connectedhomeip/out/standalone/chip-tool`

Hub address: sole source is `matter-hub.json` under the Silabs config directory (`~/.silabs/` on Unix, `%USERPROFILE%\.silabs\` on Windows), field `host`. **Only** `discover --host HOST` writes this file (user action). All other subcommands read it. No environment overrides and no `--host` on agent commands.

## One-time hub setup (user, not agent)

Copy this block to the user when `hub.py` reports the hub is not configured or auth fails:

```text
Matter Hub one-time setup (run in your terminal):

  1. ssh ubuntu@HOST
  2. Install your SSH public key on the hub (same HOST), for example:
       Linux/macOS: ssh-copy-id ubuntu@HOST
       Windows (OpenSSH): ssh-copy-id ubuntu@HOST if available, or add your
       public key to ~ubuntu/.ssh/authorized_keys on the Pi
  3. python3 .cursor/skills/chip-tool/scripts/hub.py discover --host HOST
     (use python instead of python3 on Windows if needed)

HOST = Pi IP
```

The agent never types the hub password (`BatchMode=yes`). On `Permission denied`, send the block above and stop. No `sshpass`, no password in chat.

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
| `run` | Pass remaining args to chip-tool |
| `show-node-id` | Read last node id from `/tmp/last-node-id` on the hub |
| `logs` | Last 200 lines of `otbr-agent` journal |

### `commission-thread`

Defaults: pin `20202021`, discriminator `3840`. Options: `--node-id`, `--pin`, `--discriminator`, `--dataset` (hex without `hex:` prefix).

Uses dataset from `--dataset`, else `dataset` subcommand output. Blocks until chip-tool exits (up to 180s). Saves node id to `/tmp/last-node-id` on the Pi.

### `run`

Forwards argv to chip-tool. Example:

```bash
python3 .cursor/skills/chip-tool/scripts/hub.py run onoff on 1 1
```

If the user omits node id, read last id from the Pi with `hub.py show-node-id` or reuse the node id from `commission-thread`.

## Consent

- Run `start-thread` only when the user explicitly wants a new Thread network.
- Do not factory-reset OTBR to fix a failed commission without asking.

## Default workflow

After the Matter app is built, flashed, and advertising:

1. `check` (if it fails, send one-time setup block and stop)
2. `dataset` (or `start-thread` only if requested)
3. `commission-thread` with credentials from device logs if not defaults
4. `run` for cluster commands
5. `logs` if OTBR-side diagnosis is needed

## Pairing reference

Thread BLE (hub runs chip-tool):

```text
pairing ble-thread <node_id> hex:<dataset> <pin> <discriminator>
```

`hub.py commission-thread` builds this command. Matter over Wi-Fi (`pairing ble-wifi`) is not implemented yet. A `commission-wifi` subcommand will be implemented in a follow-up.

## Logs

- chip-tool output: stdout of `run` and `commission-thread`
- OTBR: `logs` subcommand (`journalctl -u otbr-agent --no-pager -n 200`)
- Do not run `journalctl -f` or `tail -f`
