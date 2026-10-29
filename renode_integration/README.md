# Matter Renode Simulation Artifacts

This directory builds and publishes the non-Matter assets required to run the
Matter Renode simulation in CI and locally. Matter application ELFs come from 
`dev-apps-builder` or a local build, they are not part of this bundle.

## Overview

The simulation models:

- **matter_hub** - ZynqMP Buildroot Linux guest (OTBR, BlueZ, chip-tool, provision)
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
| `harness/` | pyrenode3 harness (`MatterSim`), commissioning smoke test, checkpoint generation |
| `out/bundle/` | Assembled artifact tree (gitignored) |

## Common vs runtime artifacts

Artifacts are split into two GHCR packages sharing the same version `N`:

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

The lighting ELF must match the SoC platform loaded in `resc/matter-sim.resc` (default `brd4187c`). For another board, change
the `LoadPlatformDescription` line in that resc file locally and use the matching app binary.
Only **MG24**, **MG26**, and **SixG301** have been tested in this simulation so far.

### Manual test with Renode CLI (resc)

Copy your app binary into the bundle as `matter.out`, then start Renode:

```sh
cp /path/to/matter/app/binaries/<app>.out out/bundle/matter.out
cd out/bundle
./renode/renode -e '$matter_elf=@'"$(pwd)"'/matter.out' resc/matter-sim.resc
```

Connect to the hub console and the Matter app CLI.

```sh
# Matter Hub
nc localhost 4540

# Matter SoC
nc localhost 3452
```

`matter-sim.resc` starts from a checkpoint with booted Linux machine and pre-initialized
Thread network. On the simulated Matter Hub you can commission with:

```sh
chip-tool pairing ble-thread 101 "hex:$(cat /tmp/thread-dataset.hex)" 20202021 3840
```

Then you can control the device through chip-tool. For example, to toggle a lighting app:
```sh
chip-tool onoff toggle 101 1
```

To form a new Thread network instead, run `matter-thread-init --force` on the hub console.

### Manual commissioning test (pyrenode3 harness)

Same simulation as `matter-sim.resc`, driven in-process by `harness/commissioning_test.py`
(pairing + on/off toggle). UART output is printed with `test_lib` tags (`[matter_hub]:[CLI]:`,
`[matter_soc]:[CLI]:`, `[SND]:`, `[EXP]:`).

From the repository root (after `fetch_bundle.py`):

```sh
python3 -m pip install -r renode_integration/harness/requirements.txt
python3 -m pip install --no-deps -e renode_integration/out/bundle/test_lib

python3 renode_integration/harness/commissioning_test.py \
  --matter-elf /path/to/matter_thread_soc_lighting_app_freertos.out
```

The harness uses the assembled bundle at `renode_integration/out/bundle`. Exit code `0` means commissioning and
toggle succeeded. Device logs are on stdout from `test_lib`.

### Rebuilding artifacts (maintainers)

Use workflow [renode-sim-artifacts](../.github/workflows/renode-sim-artifacts.yaml)
(`publish=true` after bumping `BUNDLE_VERSION`). Individual scripts under `scripts/`
are for CI and pipeline development; `build_tools_image.py` requires the
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

### CI commissioning test

Workflow [`.github/workflows/renode-commissioning-tests.yaml`](../.github/workflows/renode-commissioning-tests.yaml) runs from [dev-apps-builder](../.github/workflows/dev-apps-builder.yaml) after the mg24 lighting app build. It fetches the published Renode bundle from GHCR, loads the PR lighting app ELF (`brd4187c`), and runs:

```sh
chip-tool pairing ble-thread 101 "hex:$(cat /tmp/thread-dataset.hex)" 20202021 3840
chip-tool onoff toggle 101 1
```

The job is non-blocking (`continue-on-error`) during the pilot. Hub and SoC UART
output is streamed to the job log via Renode `test_lib`.

## Provision tool disk

The hub exposes a second VirtIO block device (`provision_virtio`) for `matter_support/provision`. The published bundle ships a checkpoint with that device. It does not ship `matter-provision.ext2`. Build and attach the image with workflow [`.github/workflows/renode-provisioning-artifacts.yaml`](../.github/workflows/renode-provisioning-artifacts.yaml) when running provisioning tests.

| Artifact | Role |
|----------|------|
| `matter-tools.ext2` | OTBR, BlueZ, chip-tool |
| `matter-provision.ext2` | `tool/`, arm64 Python, `requirements.txt` wheels, `MATTER_SUPPORT_REVISION` |

After the hub mounts the provision disk at `/root/matter-provision`, `/usr/bin/provision` runs `tool/provision.py` using the interpreter and wheels on that same disk.

**Run provision against a bundle locally**:

Use a provisioning-enabled Matter build (`matter_provision_channel`).

SoC must boot with NVM3 key `0x87228=1` to put the device in provisioning mode. Build hex from the app linker map:

```sh
cp path/to/matter.out renode_integration/out/bundle/matter.out
python3 renode_integration/scripts/make_provision_nvm3.py \
  --map path/to/matter_thread_soc_lighting_app_freertos.map \
  --output renode_integration/out/bundle/nvm3-provision.hex
```

Fetch the runtime bundle with a checkpoint that includes `provision_virtio`.

Build `matter-provision.ext2` in CI, download, and copy it under `out/bundle/guest-rootfs/`.

Run simulation using `matter-sim-prov.resc` (`LoadImage` on `provision_virtio`, provision-enabled SoC + NVM3 hex):

```sh
cd renode_integration/out/bundle && ./renode/renode resc/matter-sim-prov.resc
# 4540: matter-provision-mount  |  3452: BLE address  |  provision read vendor_id -c bt:...
```

Run `matter-provision-mount` in hub console after load to mount provisioning disk.

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
| `provision: matter-provision disk is not mounted` | Use `matter-sim-prov.resc`, then run `matter-provision-mount` on the hub console |
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
- **Checkpoint:** `harness/generate_checkpoint.py` drives Renode through pyrenode3 (`MatterSim`). It includes `matter-sim-full.resc`, waits for `matter-services: READY`, logs in, runs `matter-thread-init`, and saves `linux-booted-thread.save`. The macOS smoke test loads that checkpoint with the same harness. Dependencies are pinned in `harness/requirements.txt`.
- **Storage:** ORAS artifacts on `ghcr.io/siliconlabssoftware/matter-renode-sim`.
