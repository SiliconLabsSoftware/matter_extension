# Matter Renode Simulation Artifacts

This directory builds and publishes the non-Matter assets required to run the
Matter Renode simulation in CI and locally. Matter application ELFs come from 
`dev-apps-builder` or a local build, they are not part of this bundle.

## Overview

The simulation runs:

- **matter_hub** - ZynqMP Buildroot Linux guest (OTBR, BlueZ, chip-tool)
- **thread_rcp** - EFR32 Thread RCP (Spinel over UART)
- **ble_rcp** - EFR32 BLE RCP (HCI over UART)
- **matter_soc** - EFR32 Matter device (added at runtime from checkpoint)

## Directory layout

| Path | Purpose |
|------|---------|
| `sim-manifest.json` | Pinned versions (Renode, base rootfs, ot-br-posix, RCPs, GHCR package) |
| `resc/` | Renode startup scripts |
| `guest/dts/` | ZynqMP device tree source |
| `guest/rootfs-overlay/` | Matter-specific files injected into the boot rootfs |
| `scripts/` | Python scripts that build, assemble, fetch, and publish the bundle |
| `harness/` | pyrenode3 harness (`MatterSim`, `demo_runner`), checkpoint generation |
| `out/bundle/` | Assembled artifact tree (gitignored) |

## Common vs runtime artifacts

Artifacts are split into GHCR packages sharing the same version `N`:

| Tag | Contents |
|-----|----------|
| `vN-common` | rootfs, tools image, DTB, RCP ELFs, resc files |
| `vN-runtime-linux-x64` | Renode build + checkpoint (CI, Linux, WSL2) |
| `vN-runtime-osx-arm64` | Renode build + checkpoint (macOS for local development) |

Checkpoints are tied to the Renode build that created them. Each host runtime
is built independently from the same common inputs.

## Local development

The expected workflow is to pull published artifacts from GHCR, not to rebuild
rootfs, tools image, RCPs, or Renode locally. The **common** bundle includes
`matter-rootfs.ext2`, `matter-tools.ext2`, DTB, RCP ELFs, and resc files. The
**runtime** bundle for your host adds portable Renode and the checkpoint.

### Prerequisites

- Python 3.11+, `.NET` 8 SDK (for pyrenode3 / commissioning harness), `oras`, `gh auth login`

Fetch the bundle once before either workflow below:

```sh
cd renode_integration
brew install oras    # macOS
gh auth login
python3 scripts/fetch_bundle.py
```

Use an ELF built for the SoC board you pass to `--board` (default `brd4187c`). **MG24**, **MG26**, and **SixG301** have been exercised in this simulation.

### Demo test (local and CI)

`harness/demo_test.py` is the single entry point: it loads `linux-booted-thread.save` via pyrenode3, attaches the Matter SoC for `--board`, commissions node **101**, then runs README steps from `harness/demo_flows.yaml` (same path CI uses).

The harness always uses the bundle fetched into `renode_integration/out/bundle`. From the repository root (after `fetch_bundle.py`):

```sh
python3 -m pip install -r renode_integration/harness/requirements.txt
python3 -m pip install --no-deps -e renode_integration/out/bundle/test_lib

./renode_integration/harness/demo_test.py \
  --app lighting_app \
  --board brd4187c \
  --matter-elf /path/to/matter_thread_soc_lighting_app_freertos.out
```

While the harness runs you can still attach with `nc localhost 4540` (hub) and `nc localhost 3452` (SoC). UART output is tagged in the harness log (`[matter_hub]:[CLI]:`, `[matter_soc]:[CLI]:`, etc.).

Use `--interactive` to commission the device and control it from a hub shell prompt. This skips the predefined demo steps and keeps the same commissioned simulation running until you exit:

```sh
./renode_integration/harness/demo_test.py \
  --matter-elf /path/to/matter_thread_soc_lighting_app_freertos.out \
  --interactive
```

At the `hub>` prompt, enter commands such as:

```text
hub> chip-tool onoff on 101 1
hub> chip-tool onoff read on-off 101 1
hub> chip-tool onoff off 101 1
hub> exit
```

Use `exit`, `quit`, Ctrl-D, or Ctrl-C to close the session and simulation. A failed command is reported and returns you to the prompt. State is retained during the session, a new invocation starts a fresh simulation and commissions again. Interactive mode is for non-interactive hub shell commands such as `chip-tool`, not programs that require their own input prompt.

You can also supply `--app` in interactive mode to select its device setup. For `--app light_switch_app`, provide `--extra-elf` with the lighting ELF. The light is node **102** and the switch is node **101**. Without `--interactive`, `--app` runs its predefined demo flow and exits, as CI does. Edit `demo_flows.yaml` for per-app CI steps.

CI: [`.github/workflows/renode-demo-tests.yaml`](../.github/workflows/renode-demo-tests.yaml) runs via `workflow_run` after a successful **Build Dev apps** or **Packages Validation** on `main` / `release_*`, using `renode-demo-full-*` artifacts from that workflow run. To form a new Thread network from the hub console, run `matter-thread-init --force` (e.g. via `nc` during a long-running session).

Cold boot (no checkpoint) remains `resc/matter-sim-full.resc` for maintainers regenerating the bundle checkpoint.

### Rebuilding artifacts (maintainers)

Use workflow [renode-sim-artifacts](../.github/workflows/renode-sim-artifacts.yaml)
(`publish=true` after bumping `BUNDLE_VERSION`). Individual scripts under `scripts/`
are for CI and pipeline development. `build_tools_image.py` requires the
`ubuntu-24.04-arm` runner.

### Cold boot (no checkpoint)

```sh
cd renode_integration/out/bundle
./renode/renode resc/matter-sim-full.resc
```

## CI

Workflow: [`.github/workflows/renode-sim-artifacts.yaml`](../.github/workflows/renode-sim-artifacts.yaml)

Triggered manually via `workflow_dispatch`. Set `publish=true` to push to GHCR.

```
build-rcps ─────────────┐
build-rootfs-dtb ───────┼─► assemble-common ─► publish-common (optional)
build-tools-image ──────┘         │
                                  ▼
                          build-runtime matrix
                          (linux-x64 and osx-arm64)
                                  │
                                  ▼
                          publish-runtime (optional)
```

### CI demo tests

Workflow [`.github/workflows/renode-demo-tests.yaml`](../.github/workflows/renode-demo-tests.yaml) drives `harness/demo_test.py` against `harness/demo_flows.yaml` (thread README `chip-tool` steps after commissioning).

| Trigger | Scope |
|---------|--------|
| `workflow_run` after **Build Dev apps** or **Packages Validation** | Parent workflow succeeded on `main` or `release_*`. All Matter-over-Thread demo apps × boards in `harness/demo_config.py` |

Jobs run in parallel (`fail-fast: false`), one per app and board: 13 apps × nine boards (117 jobs). Demos expect `renode-demo-full-*` artifacts from the triggering run. The boards are `brd4187c`, `brd4116a`, `brd4407a`, `brd4186c`, `brd4117a`, `brd4118a`, `brd4120a`, `brd4121a`, and `brd1019a`. Each job loads `platforms/boards/silabs/<board>.repl`. ELFs come from `renode-demo-<build-type>-<app>-<platform>` artifacts (tree paths under `out/<board>/…`, downloaded with `actions/download-artifact` and located by board in the workflow). Hub and SoC UART output is streamed to the job log via Renode `test_lib`.

## Updating the bundle

1. Edit `sim-manifest.json`, overlays, or resc files.
2. Validate with a CI run or targeted script changes on the appropriate runner
3. Bump `BUNDLE_VERSION` in `scripts/common.py` when publishing a new GHCR tag.
4. Dispatch `renode-sim-artifacts` with `publish=true`.

Regenerate the checkpoint after any change to Renode, rootfs, tools, DTB, or RCPs.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Checkpoint won't load | Renode build mismatch, rebuild Renode and run `harness/generate_checkpoint.py` |
| `oras pull` auth failure | `gh auth login` and ensure GHCR package access |
| `matter-services` timeout | Check guest logs at `/tmp/*.log` on hub console |
| New Thread network needed | `matter-thread-init --force` on hub console |

## Implementation notes

- **Rootfs:** Antmicro ZynqMP rootfs (`base_rootfs`, sha256-checked). The build adds 
  `guest/rootfs-overlay/` through `debugfs -w`.
- **Tools image:** built on Ubuntu arm64 (`tools_image.ubuntu_version`):
  - `otbr-agent`, `ot-ctl` and `otbr-agent.conf`: ot-br-posix at `ot_br_posix.commit`, built with
    its own `script/bootstrap` and `script/cmake-build` plus `ot_br_posix.cmake_args`.
  - `bluetoothd`, `btattach`, `btmgmt`, `dbus-*`, `system.conf` and `bluetooth.conf`: the Ubuntu
    `bluez` and `dbus` packages.
  - Shared libraries and the loader: resolved with `ldd` from the build host.

  The guest is Buildroot, so `S99matter-services` runs these binaries through the bundled loader
  and copies the D-Bus configs into place at boot.
- **Checkpoint:** `harness/generate_checkpoint.py` drives Renode through pyrenode3 (`MatterSim`). It includes `matter-sim-full.resc`, waits for `matter-services: READY`, logs in, runs `matter-thread-init`, and saves `linux-booted-thread.save`. The macOS smoke test loads that checkpoint with the same harness. Dependencies are pinned in `harness/requirements.txt`.
- **Storage:** ORAS artifacts on `ghcr.io/siliconlabssoftware/matter-renode-sim`.
