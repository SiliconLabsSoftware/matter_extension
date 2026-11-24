# Matter Renode Simulation Artifacts

This directory builds and publishes the non-Matter assets required to run the
Matter Renode simulation in CI and locally. Matter application ELFs come from
`dev-apps-builder` or a local build, they are not part of this bundle.

## Overview

The simulation runs:

- **matter_hub** - ZynqMP Buildroot Linux guest (OTBR, BlueZ, chip-tool, provision)
- **thread_rcp** - EFR32 Thread RCP (Spinel over UART)
- **ble_rcp** - EFR32 BLE RCP (HCI over UART)
- **matter_soc** - EFR32 Matter device (added at runtime from checkpoint)

## Directory layout

| Path | Purpose |
|------|---------|
| `sim-manifest.json` | Pinned versions (Renode, base rootfs, ot-br-posix, RCPs, GHCR package) |
| `guest/dts/` | ZynqMP device tree source |
| `guest/rootfs-overlay/` | Matter-specific files injected into the boot rootfs |
| `scripts/` | Python scripts that build, assemble, fetch, and publish the bundle |
| `harness/` | pyrenode3 harness (`MatterSim`, `demo_runner`), checkpoint generation |
| `out/bundle/` | Assembled artifact tree (gitignored) |

## Common vs runtime artifacts

Artifacts are split into two GHCR packages. Both use `COMMON_VERSION` `N`. Runtime tags
also carry the first 7 characters of `renode.commit` so a Renode bump needs no version bump:

| Tag | Contents |
|-----|----------|
| `vN-common` | rootfs, tools image, DTB, RCP ELFs |
| `vN-runtime-<renode>-linux-x64` | Renode build + test_lib + checkpoint (CI, Linux, WSL2) |
| `vN-runtime-<renode>-osx-arm64` | Renode build + test_lib + checkpoint (macOS for local development) |
| `vN-provision` | `matter_support/provision`, python dependencies |
| `<tag>-pr-<PR-NUM>` | Any of the above, built by a PR that changes that bundle's inputs (see [CI](#ci)) |

Checkpoints are tied to the Renode build that created them. Each host runtime
is built independently from the same common inputs.

`scripts/fetch_bundle.py` prefers the `-pr-<PR-NUM>` tag of each bundle and falls back
to the base tag. The PR comes from `-p PR-NUM`, or from the pull request in CI. PR tags
are deleted when the PR closes.

## Local development

The expected workflow is to pull published artifacts from GHCR, not to rebuild
rootfs, tools image, RCPs, or Renode locally. The **common** bundle includes
`matter-rootfs.ext2`, `matter-tools.ext2`, DTB, and RCP ELFs. The
**runtime** bundle for your host adds portable Renode and the checkpoint. The
**provision** bundle includes `matter-provision.ext2` with dependencies to
provision simulated devices.

### Prerequisites

- Python 3.11+, `.NET` 8 SDK (for pyrenode3 / commissioning harness), `oras`, `gh auth login`

Fetch the bundle once before either workflow below:

```sh
cd renode_integration
brew install oras    # macOS
gh auth login
python3 scripts/fetch_bundle.py
```

Use an ELF built for the SoC board you pass to `--board`. **MG24**, **MG26**, and **SixG301** have been exercised in this simulation.

### Demo test (local and CI)

`harness/demo_test.py` is the single entry point. In demo and commissioned interactive modes, it loads `linux-booted-thread.save` via pyrenode3, attaches the Matter SoC for `--board`, commissions node **101**, then runs README steps from `harness/demo_flows.yaml` (same path CI uses).

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

If no runtime exists for your host on GHCR, `scripts/fetch_bundle.py` downloads the common
artifact only. Dispatch `renode-runtime` to publish a runtime, or build one locally (below).

### Local runtime (custom Renode)

Builds the runtime exactly as CI does, from the pinned commit or a local Renode checkout
(`--src`, must contain `tests/test_lib`):

```sh
cd renode_integration
python3 scripts/fetch_bundle.py
python3 scripts/build_renode.py --src ~/src/renode
python3 scripts/assemble_bundle.py
python3 -m pip install -r harness/requirements.txt
python3 -m pip install --no-deps -e out/bundle/test_lib
PYTHONPATH=harness python3 harness/generate_checkpoint.py
```

### Manual provisioning test

`harness/demo_test.py --provision` reuses `MatterSim` and Renode `test_lib` to attach a
provisioning disk and a provisioning-enabled SoC to the Thread hub checkpoint.
It opens a manual provisioning prompt inside the simulated hub before commissioning.
`--provision` requires `--nvm3-hex` and cannot be combined with `--app`,
`--extra-elf`, or `--interactive`. The `--nvm3-hex` and `--provision-image`
options require `--provision`.
The harness uses the bundle at `renode_integration/out/bundle`.

From the repository root, fetch the bundle with `--require-provision` so a missing
provisioning image fails immediately. Add `-p PR-NUM` to prefer bundles built by a PR:

```sh
python3 renode_integration/scripts/fetch_bundle.py --require-provision
# Or: python3 renode_integration/scripts/fetch_bundle.py --require-provision -p PR-NUM
python3 -m pip install -r renode_integration/harness/requirements.txt
python3 -m pip install --no-deps -e ./renode_integration/out/bundle/test_lib
```

Use a Matter build containing `matter_provision_channel`. Generate an NVM3 image
setting key `0x87228=1` from that same build's linker map. Specify `--board` to
resolve the part from the Simplicity SDK submodule's board metadata.
`--board` is required, with no default. Use the same
board and matching map for image generation and the provisioning session:

```sh
python3 renode_integration/scripts/make_provision_nvm3.py \
  --map /path/to/matter_app.map \
  --board brd4187c \
  --output renode_integration/out/nvm3-provision.hex

python3 renode_integration/harness/demo_test.py --provision \
  --matter-elf /path/to/matter_app.out \
  --board brd4187c \
  --nvm3-hex renode_integration/out/nvm3-provision.hex
```

The harness loads the disk through `provision_virtio`, runs `matter-provision-mount`,
and attaches the SoC UART tester while emulation is paused, before the SoC starts.
Use `--provision-image PATH` to override the provisioning disk.

In interactive mode, wait for provisioning readiness in the streamed SoC UART log
and note its BLE address before issuing commands. You can also attach to hub port
4540 and SoC port 3452. At the `hub>` prompt, for example:

```text
hub> provision read vendor_id -c bt:BLE-ADDRESS -o /tmp/provision-read.json
hub> cat /tmp/provision-read.json
hub> exit
```

This is a manual session requiring an interactive terminal. Provisioning commands,
readiness checks, and readback verification are performed by the operator.

### Rebuilding artifacts (maintainers)

Individual scripts under `scripts/` are for CI and pipeline development,
`build_tools_image.py` requires the `ubuntu-24.04-arm` runner.

## CI

- [`renode-matter-hub.yaml`](../.github/workflows/renode-matter-hub.yaml): common bundle, then
  calls `renode-runtime` with the common bundle artifact from the same run. Runs on pull
  requests and pushes to `main` and `release_*` that change `guest/`
  or `scripts/build_rootfs_image.py`, and via `workflow_dispatch` with `publish=true`.
  RCP and chip-tool updates are published by dispatch.
- [`renode-runtime.yaml`](../.github/workflows/renode-runtime.yaml): runtime only, fetches
  common from GHCR when not called by `renode-matter-hub`. Runs on pull requests and pushes
  that change `sim-manifest.json` or `scripts/build_renode.py`, and via `workflow_dispatch`.
- [`renode-pr-artifacts-cleanup.yaml`](../.github/workflows/renode-pr-artifacts-cleanup.yaml):
  deletes the `-pr-<PR-NUM>` tags of every bundle when the PR closes.

Publishing follows `common.publish_tag`: a pull request against an active branch
(`ACTIVE_BRANCHES` in `scripts/common.py`) publishes `<tag>-pr-<PR-NUM>`, a push or dispatch
on an active branch publishes the base tag, and any other branch skips publishing.
CI jobs in the same PR fetch the PR tags only once they are published, rerun them
after the bundle workflow finishes.

```
build-rcps ─────────────┐
build-rootfs-dtb ───────┼─► assemble-common ─► publish-common (optional)
build-tools-image ──────┘         │
                                  ▼
                          renode-runtime: build-runtime matrix
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

### CI provisioning test
Will be implemented in future PRs.

## Updating the bundle

1. Edit `sim-manifest.json`, overlays, or the hub topology in `harness/matter_sim.py`.
2. Guest or RCP changes: bump `COMMON_VERSION` in `scripts/common.py`.
   Renode changes: update `renode.commit` in `sim-manifest.json`.
3. Open a PR. The workflows above publish the rebuilt bundles as `-pr-<PR-NUM>` tags,
   which CI tests in the PR and `fetch_bundle.py -p PR-NUM` pick up. Merging publishes
   the base tags. A `renode.commit` bump rebuilds only the runtime.
4. Other changes: dispatch `renode-matter-hub` or `renode-runtime` with `publish=true`
   on an active branch.

The provisioning bundle is automatically updated with any updates to `third_party/matter_support`. Can also manually update by dispatching `renode-provisioning-artifacts` with `publish=true`.

Regenerate the checkpoint after any change to Renode, rootfs, tools, DTB, or RCPs.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Checkpoint won't load | Renode build mismatch, rebuild Renode and run `harness/generate_checkpoint.py` |
| `oras pull` auth failure | `gh auth login` and ensure GHCR package access |
| `matter-services` timeout | Check guest logs at `/tmp/*.log` on hub console |
| `provision: matter-provision disk is not mounted` | Use `harness/demo_test.py --provision`, which attaches and mounts the provisioning disk. Verify checkpoint compatibility |
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
- **Provision image:** built on Linux aarch64 with `build_provision_image.py`: `matter_support/provision`
  as `tool/`, pinned `requirements.txt`, pip wheels under `opt/provision/site-packages`, and a bundled
  arm64 `python3` plus stdlib and shared libraries on the same ext2.
- **Checkpoint:** `harness/generate_checkpoint.py` drives Renode through pyrenode3 (`MatterSim`). `MatterSim.boot()` creates the hub and RCP machines, waits for `matter-services: READY`, logs in, runs `matter-thread-init`, and saves `linux-booted-thread.save`. The macOS smoke test loads that checkpoint with the same harness. Dependencies are pinned in `harness/requirements.txt`.
- **Storage:** ORAS artifacts on `ghcr.io/siliconlabssoftware/matter-renode-sim`.
