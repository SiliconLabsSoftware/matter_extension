# Matter Renode Simulation Artifacts

This directory builds and publishes the non-Matter assets required to run the
Matter Renode simulation in CI and locally. Matter application ELFs come from 
`dev-apps-builder` or a local build, they are not part of this bundle.

## Overview

The simulation models:

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
| `harness/` | Checkpoint generation harness |
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

- Python 3, `oras`, `gh auth login`

### Quickstart

```sh
cd renode_integration
brew install oras    # macOS
gh auth login
python3 scripts/fetch_bundle.py
cp /path/to/matter/app/binaries/<app>.out out/bundle/matter.out
cd out/bundle
./renode/renode --disable-gui -e '$matter_elf=@'"$(pwd)"'/matter.out' resc/matter-sim.resc
```

Connect to the hub console and the Matter app CLI.
```sh
# Matter Hub
nc localhost 4540

# Matter SoC
nc localhost 3452
```

After restoring a checkpoint, commission with:

```sh
chip-tool pairing ble-thread 101 "hex:$(cat /tmp/thread-dataset.hex)" 20202021 3840
```

To form a new Thread network instead, run `matter-thread-init --force` on the hub console.

### Overrides

| Variable | Effect |
|----------|--------|
| `RENODE=/path/to/renode` | Use an existing Renode binary |
| `BUNDLE_VERSION=v1` | Fetch or publish a specific bundle version |
| `HOST=linux-x64` | Force host runtime selection |

If no runtime exists for your host on GHCR, `scripts/fetch_bundle.py` downloads the common
artifact only. Dispatch `renode-sim-artifacts` to publish a runtime, or build Renode on
that host only when developing the pipeline itself.

### Rebuilding artifacts (maintainers)

Use workflow [renode-sim-artifacts](../.github/workflows/renode-sim-artifacts.yaml)
(`publish=true` after bumping `BUNDLE_VERSION`). Individual scripts under `scripts/`
are for CI and pipeline development; `build_tools_image.py` requires the
`ubuntu-24.04-arm` runner.

### Cold boot (no checkpoint)

```sh
cd renode_integration/out/bundle
./renode/renode --disable-gui resc/matter-sim-full.resc
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

The future Matter commissioning CI job will:

1. `python3 scripts/fetch_bundle.py` (linux-x64 runtime)
2. Download a Matter ELF from dev-apps-builder
3. Run `out/bundle/renode/renode` with `resc/matter-sim.resc` and drive tests via the harness

## Updating the bundle

1. Edit `sim-manifest.json`, overlays, or resc files (or bump submodules).
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
- **Checkpoint:** Boots `matter-sim-full.resc`, waits for `matter-services: READY`, runs `matter-thread-init`, saves `linux-booted-thread.save`.
- **Storage:** ORAS artifacts on `ghcr.io/siliconlabssoftware/matter-renode-sim`.
