# Developer README — Package Generation and Helper Scripts

Developer guide for creating and maintaining Matter Conan/SLT packages (not end-user docs).

---

## Setup

Follow the documentation on Confluence:

- [Install SLT](https://confluence.silabs.com/spaces/MATTER/pages/725302792/How+to+work+with+Package+Manager#HowtoworkwithPackageManager-InstallSLT)
- [Conan (via SLT)](https://confluence.silabs.com/spaces/MATTER/pages/725302792/How+to+work+with+Package+Manager#HowtoworkwithPackageManager-Conan(viaSLT))

---

## How to Create Packages

Starting from the **root** directory.

Channel defaults to `packages/_shared/release_stream_channel` (or env `MATTER_PACKAGE_CHANNEL`).
Pass `--channel` only when you need a non-default channel.

### Recommended: `slc/build-pkg.sh`
```bash
# Channel defaults from packages/_shared/release_stream_channel (or MATTER_PACKAGE_CHANNEL).
./slc/build-pkg.sh --create-package-version 2.10.0-0.dev
./slc/build-pkg.sh --create-package-version 2.10.0-0.dev --channel 2026-12
./slc/build-pkg.sh --create-package-version 2.10.0-0.dev --channel 2026-12 --clean

# Export then build a sample via packages/build_app.sh
./slc/build-pkg.sh --build-from-package-version 2.10.0-0.dev --channel 2026-12 \
  matter_wifi_soc_lock_app_freertos.slcw brd4338a
```

### Direct Conan export-pkg
```bash
CHANNEL="$(tr -d '[:space:]' < packages/_shared/release_stream_channel)"
# or: CHANNEL=2026-12

conan export-pkg packages/matter/conanfile.py \
  --name=matter --version=<matter_extension_version> \
  --user=silabs --channel="${CHANNEL}"

conan export-pkg packages/matter_app/conanfile.py \
  --name=matter_app --version=<matter_extension_version> \
  --user=silabs --channel="${CHANNEL}"
```

---

## Helper Scripts

Helper scripts are stored under:
```
root/slc/script/
```

### `slc/script/generate_pkg_slt.py`
Generates `pkg.slt`, which is used by SLT to determine dependencies to download for development.

- Centralized utility to generate consistent `pkg.slt` files across SLC projects and solutions.
- Removes manual maintenance and prevents version drift in dependencies.
- Supports switching between single- or multi-dependency models for sample apps (option 2 or 3 in [Matter Package Manager design doc](https://confluence.silabs.com/spaces/MATTER/pages/594744893/Matter+Package+Manager), decision still pending).
- Generates `pkg.slt` for all directories containing a `.slcp` or `.slcw` file (Design option 3).
- Matter package version comes from `slc/script/matter_package_version` (fallback: `matter.slce` + `-0.dev`).
- Release-stream comes from `packages/_shared/release_stream_channel`.

---

### `slc/script/get_slce_extra_paths.py`
- Regenerates managed path sections in `packages/matter/matter.slce.extra` deterministically.
- Ensures only required files (e.g., ZAP templates) are packaged, minimizing package size.
- Must be run for every `matter_sdk` submodule update.

---

### Version and channel sources
- **`slc/script/matter_package_version`** – Conan/SLT package version pin used by `generate_pkg_slt` / CI when unset.
- **`matter.slce`** – Line version (`X.Y.Z`); Conan recipes also derive package version via `get_version`.
- **`packages/_shared/release_stream_channel`** – One-liner Conan channel / `pkg.slt` release-stream (SoT for channel).
- **`MATTER_PACKAGE_VERSION`** – Optional runtime version override (Jenkins/CI).
- **`MATTER_PACKAGE_CHANNEL`** – Optional runtime channel override; CI defaults from `release_stream_channel`.

---

## File Descriptions

- **`packages/matter/conanfile.py`** – Defines the Matter component package and its dependencies, including OpenThread, Zigbee, Wi-Fi, and required tooling (SLC, ZAP, etc.). Incorporates `matter.slce.extra`, which lists all Matter components and source files not directly referenced by a component.
- **`packages/matter/matter.slce.extra`** – Contains references to all components under `matter.slce`, and sample apps. Also intended to include all source files required for development.
- **`packages/matter_app/conanfile.py`** – Used to package Matter sample applications and workspaces as seen in Studio.
- **`packages/remotes.json`** – File containing URLs needed for Conan to search packages.
- **`slc/script/dependency_versions.yaml`** – Used as a single source of truth for dependencies
- **`slc/script/matter_package_version`** – Conan/SLT Matter package version pin
- **`packages/_shared/release_stream_channel`** – One-liner Conan channel / pkg.slt release-stream
- **`pkg.slt`** – Exists in multiple locations with identical contents, dictating dependency on the Matter component/stack package.
- **`sample_app_pkg.slt`** – Dictates dependency on the Matter app package.

---

## Directory Layout

```
root/
├── matter.slce
├── packages
│   ├── _shared
│   │   ├── base_recipe.py
│   │   └── release_stream_channel
│   ├── matter
│   │   ├── conanfile.py
│   │   └── matter.slce.extra
│   ├── matter_app
│   │   ├── conanfile.py
│   ├── DEVELOPER_README.md
└── slc/
    └── script/
```
