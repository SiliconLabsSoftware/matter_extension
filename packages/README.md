# Package Generation and Helper Scripts

The contents of these folders are used for generation of packages. This document describes how to create packages and the helper scripts used to maintain package manager metadata.

---

## Dependency model

Packages **declare** dependencies; SLT pulls them from Conan at install time. The `matter` package bundles SLCC extension content and the full `third_party/matter_sdk` tree (copied at export from the `matter_sdk` git clone via `MATTER_SDK_SOURCE_ROOT`).

| Package | Conan `requires()` | `pkg.slt` (apps / publish) |
|---------|-------------------|----------------------------|
| **matter** | All stack deps from `dependency_versions.yaml` (simplicity-sdk, wiseconnect, thread + wifi platform packages) | `packages/matter/pkg.slt` declares `matter` only |
| **matter_app** | `matter` only | Sample app `pkg.slt` files declare `matter_app` only |

**Package chain:** `matter_app` → `matter` → stack SDKs (simplicity-sdk, wiseconnect, …). There is no separate `matter_sdk` Conan package.

Stack SDKs (Simplicity SDK, WiseConnect) are **not** git submodules. They are installed via SLT/Conan and exposed as `SISDK_ROOT` / `WISECONNECT_ROOT` in `slc/tools/.env`.

---

## Setup

Follow the documentation on Confluence:

- [Install SLT](https://confluence.silabs.com/spaces/MATTER/pages/725302792/How+to+work+with+Package+Manager#HowtoworkwithPackageManager-InstallSLT)
- [Conan (via SLT)](https://confluence.silabs.com/spaces/MATTER/pages/725302792/How+to+work+with+Package+Manager#HowtoworkwithPackageManager-Conan(viaSLT))

**Prerequisites:** Artifactory VPN and `conan remote login` on remotes listed in `packages/remotes.json`.

From repo root:

```bash
# One-time / after version bump
python3 slc/sl_setup_env.py
source slc/tools/.env
```

`sl_setup_env.py` will:

1. Initialize Matter git submodules (not SiSDK/WiFi)
2. Install SLT tools (slc-cli, gcc, etc.)
3. Configure Conan remotes from `packages/`
4. Export local `matter` and `matter_app` packages (`conan export-pkg`)
5. `slt install matter/<version>` (pulls full stack transitively)
6. Write `slc/tools/.env` with `SISDK_ROOT` and `WISECONNECT_ROOT` pointing at SLT cache paths

---

## Build an app

```bash
source slc/tools/.env
# dev mode (default): export + build from git tree
./slc/build.sh slc/apps/lighting_app/thread/matter_thread_soc_lighting_app_freertos.slcp brd4187c

# SQA/CI: installed packages only
./slc/build.sh --sqa slc/apps/lighting_app/thread/matter_thread_soc_lighting_app_freertos.slcp brd4187c
```

End users who install from Artifactory use `slc/apps/build-app.sh` (see `docs/LOCAL_PACKAGE_BUILD.md` Part B).

Dev mode runs `ensure_local_packages` then `slc generate` with filtered `autogen/slc-sdk.slconf`.

---

## After changing extension or app sources

```bash
./slc/script/refresh_local_packages.sh
# optional: reinstall a specific app manifest
./slc/script/refresh_local_packages.sh slc/apps/lighting_app/thread/pkg.slt
```

---

## How to Create Packages (manual)

Starting from the **root** directory:

```bash
python3 slc/script/generate_pkg_slt.py -d slc
conan export-pkg packages/matter/conanfile.py --name matter --version 2.9.0-0.dev
conan export-pkg packages/matter_app/conanfile.py --name matter_app --version 2.9.0-0.dev
slt install matter/2.9.0-0.dev
slt install -f slc/apps/lighting_app/thread/pkg.slt
```

---

## Helper Scripts

Helper scripts are stored under `slc/script/`.

### `slc/script/stack_tooling.py`

Shared SLT/Conan helpers: remote setup, `export_local_packages`, `slt where`, stack root resolution.

### `slc/script/generate_pkg_slt.py`

Generates `pkg.slt` files used by SLT to resolve dependencies.

### `slc/script/refresh_local_packages.sh`

Re-exports local Conan packages and regenerates `pkg.slt` manifests after source edits.

### `slc/script/dependency_versions.yaml`

Single source of truth for stack dependency Conan version ranges consumed by the `matter` Conan recipe.

### `slc/script/get_slce_extra_paths.py`

Regenerates managed path sections in `packages/matter/matter.slce.extra` deterministically. Must be run for every `matter_sdk` submodule update.

---

## File Descriptions

- **`packages/matter/conanfile.py`** – Matter SDK package; declares stack Conan dependencies; packages SLCC extension content and copies `third_party/matter_sdk` from `MATTER_SDK_SOURCE_ROOT`.
- **`packages/matter/matter.slce.extra`** – Extra files included in the matter package.
- **`packages/matter_app/conanfile.py`** – Sample app package; depends on `matter` only; packages `.slcp`/`.slcw` projects.
- **`packages/_shared/base_recipe.py`** – Shared recipe helpers and dependency version loading.
- **`packages/remotes.json`** – Conan remote URLs for SLT.

---

## Directory Layout

```
root/
├── packages/
│   ├── _shared/
│   │   └── base_recipe.py
│   ├── matter/
│   │   ├── conanfile.py
│   │   ├── pkg.slt
│   │   └── matter.slce.extra
│   ├── matter_app/
│   │   ├── conanfile.py
│   │   └── pkg.slt
│   └── README.md
└── slc/
    └── script/
        ├── dependency_versions.yaml
        ├── generate_pkg_slt.py
        ├── stack_tooling.py
        └── stack_deps.py
```
