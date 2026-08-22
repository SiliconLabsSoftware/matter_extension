# Packages folder — line-by-line explanation (beginner guide)

This document explains every file under `packages/` that was added or changed for Matter Package Manager work. It is written for someone new to **Matter**, **Conan packages**, and **Python**.

---

## Glossary (read this first)

| Term | Meaning |
|------|---------|
| **Matter** | Smart-home connectivity standard. This repo is Silicon Labs' Matter *extension* for Simplicity Studio / SLC. |
| **Conan** | Package manager for C/C++ (and SDK content). Similar idea to `pip`, but for native code and SDK trees. |
| **`conanfile.py`** | A Python *recipe*: tells Conan how to name, version, depend on, and copy files into a package. |
| **Recipe** | The `conanfile.py` + helpers that define one package. |
| **`matter` package** | The Matter *stack/extension* (components, ZAP metadata, sources). |
| **`matter_app` package** | Sample apps (`.slcp` projects) that depend on `matter`. |
| **SLT** | Silabs tool that installs Conan packages and configures paths for SLC. |
| **SLC** | Silabs CLI that *generates* build projects from `.slcp` files. |
| **`.slcp`** | Sample project definition (YAML). Lists sources, includes, boards, quality, etc. |
| **`.slce`** | Extension definition (e.g. `matter.slce`) — what components belong to Matter. |
| **`.slsdk`** | Marker file that tells Studio/SLC "this folder is an SDK package root". |
| **ZAP** | Code generator for Matter clusters/attributes. Needs Matter-specific JSON templates. |
| **Prerelease** | Version like `2.10.0-alpha.7` (not a final release). |
| **Export** | Conan step that stores the recipe (and sometimes package contents) into the local Conan cache. |
| **`export-pkg`** | Create a local package from the current source tree without a full remote publish. |
| **`@silabs`** | Conan *user* namespace: packages are named `matter/2.10.0@silabs`. |

### Mental model

```text
matter.slce  (+ .prerelease / MATTER_PACKAGE_VERSION)
        │
        ▼
  version: 2.10.0-0.dev  or  2.10.0-alpha.N
        │
   ┌────┴────┐
   ▼         ▼
 matter    matter_app ──requires──► matter/[>=2.10.0 <2.10.1,include_prerelease]
 (stack)   (samples + matter_sdk inputs)
        │
        ▼
  slt install → slc generate → make
```

---

## Files covered

| File | Status |
|------|--------|
| `packages/.prerelease` | **New** |
| `packages/_shared/prerelease_env.sh` | **New** |
| `packages/dev_build_app.sh` | **New** (checkout helper: export + build) |
| `packages/build_app.sh` | **New** (package-only builder; shipped in `matter_app`) |
| `packages/_shared/base_recipe.py` | **Changed** |
| `packages/matter/conanfile.py` | **Changed** (sample-app paths skipped from `matter.slce.extra`) |
| `packages/matter/matter.slce.extra` | **Changed** (`slc/apps/**` removed from `extra_files`) |
| `packages/matter_app/conanfile.py` | **Changed** |
| `packages/matter/pkg.slt` | **Changed** |
| `packages/matter_app/pkg.slt` | **Changed** |
| `packages/remotes.json` | **Changed** |
| `slc/script/get_slce_extra_paths.py` | **Changed** (outside `packages/`; regenerator excludes sample apps) |

---

## 1. `packages/.prerelease`

```text
1| alpha
```

| Line | What it does | Why it is needed |
|------|----------------|------------------|
| 1 | Single word: prerelease **label** (`alpha`, could be `beta` or `rc`). | CI / publish tooling reads this file (via `SL_PRERELEASE` path) to build versions like `2.10.0-alpha.7`. Both `matter` and `matter_app` must share the same label so their versions match. |

Whitespace/newlines are stripped by `prerelease_env.sh` before use.

---

## 2. `packages/_shared/prerelease_env.sh`

Bash helper: `source` it, then call `set_prerelease_env` before publishing both packages.

| Line(s) | Code / idea | What it does | Why |
|---------|-------------|--------------|-----|
| 1 | `#!/usr/bin/env bash` | Shebang: run with bash from `PATH`. | Portable bash invocation. |
| 2–22 | Comment block | Documents usage, env vars, version rules. | So engineers know local = `-0.dev`, CI = `-alpha.N`, override = `MATTER_PACKAGE_VERSION`. |
| 24–25 | Comments | Explain path resolution without `cd`. | Avoids broken paths when nested scripts change directory. |
| 26 | `_prerelease_env_file="${BASH_SOURCE[0]//$'\r'/}"` | Path of this script when sourced; strip CR. | Works on Windows-ish line endings; `BASH_SOURCE[0]` is this file. |
| 27 | Strip newlines from that path | Cleanup. | Defensive against odd path strings. |
| 28 | `_prerelease_env_dir="${_prerelease_env_file%/*}"` | Directory of this script (`.../packages/_shared`). | `%/*` = bash "remove last `/...`". |
| 29–31 | If dir is not absolute, prefix `$PWD` | Make absolute path. | Relative `BASH_SOURCE` can break after `cd`. |
| 32–33 | `_MATTER_SHARED_PRERELEASE=.../.prerelease` | Go up from `_shared` to `packages/.prerelease`. | One shared label file for both packages. |
| 34 | `unset` temp vars | Clean shell namespace. | Avoid leaking helper variables. |
| 36 | `set_prerelease_env()` | Function you call after sourcing. | Encapsulates setup. |
| 37 | `local prerelease_file label` | Local vars inside function. | Don't pollute global shell. |
| 39 | Assign prerelease file path | Use cached absolute path. | Stable even if cwd changes later. |
| 41–44 | Error if file missing | Fail early. | Publish without a label would create wrong versions. |
| 46 | `label="$(tr -d '[:space:]' < file)"` | Read file, strip all whitespace. | File may have trailing newline; label must be clean. |
| 47–50 | Error if label empty | Fail early. | Empty label → invalid version. |
| 52–53 | `export SL_PRERELEASE=...` | Env var = **path** to `.prerelease` (Silabs convention). | `silabs_package_assistant.get_version()` reads this. |
| 55–62 | Keep or unset `SL_PRERELEASE_NUMBER` | If Jenkins already set a number, keep it; else unset. | Unset lets publish action auto-pick next `alpha.N` from Artifactory. |
| 64–65 | Echo status | Human-readable confirmation. | Easy to verify both packages will share env. |

---

## 3. `packages/dev_build_app.sh`

Local developer script: export packages → install via SLT → generate → build.

For **package-only** builds (no export / submodules), use `packages/build_app.sh` instead (also shipped inside the `matter_app` package).

| Line(s) | What it does | Why |
|---------|--------------|-----|
| 1 | Bash shebang | Same as above. |
| 2–30 | Usage / options comments | Documents CLI for humans (`--slcp`, `--board`, `--export`, …). |
| 32 | `set -euo pipefail` | Exit on error; treat unset vars as errors; fail pipelines on any failure. | Safer scripts. |
| 34 | `ROOT=.../..` | Repo root = parent of `packages/`. | All paths are repo-relative from here. |
| 35 | `cd "${ROOT}"` | Work from repo root. | Consistent relative paths. |
| 37 | Default version `2.10.0-0.dev` | Local default when nothing else set. | Matches assistant local-dev versioning. |
| 38 | `MATTER_PACKAGE_VERSION=env or default` | Allow override from environment. | Same override recipes honor. |
| 39–44 | Init flags: `SLCP`, `BOARD`, `DO_EXPORT`, `CLEAN`, `UPDATE_SUBMODULES`, `JOBS` | Defaults for CLI parsing. | Clear starting state. |
| 46–49 | `usage()` | Print comment header as help (`sed` strips `#`). | `--help` without duplicating text. |
| 51–54 | `die()` | Print error to stderr and exit 1. | Consistent failure style. |
| 56–58 | `need_cmd` | Check command exists on `PATH`. | Fail before long work if `slt`/`slc` missing. |
| 60–102 | `while` / `case` argument parser | Parse `--slcp`, `--board`, `--version`, `--export`, `--clean`, `--update-submodules`, `-j`, `-h`. | Standard CLI. |
| 63–65 | Require value after `--slcp` | Avoid empty names. | |
| 67–70 | Same for `--board` | | |
| 72–75 | Same for `--version` | | |
| 77–79 | `--export` sets flag | Export is optional (default = install existing package only). | Faster iteration when package already exported. |
| 81–83 | `--clean` flag | Used with export to wipe old local Conan packages. | Avoid stale cache confusion. |
| 85–87 | `--update-submodules` | Init matter_sdk-related submodules only. | Needed for packaging external `.slcp` inputs; not wifi/simplicity SDK. |
| 89–92 | `-j N` parallel make jobs | Default 8. | Faster builds. |
| 94–96 | Help | | |
| 97–100 | Unknown arg → help + exit 1 | | |
| 104–113 | Validate arg combinations | Export-only (no slcp/board) OR both slcp+board for build. Auto-append `.slcp`. | Prevents half-configured runs. |
| 115–117 | `--clean` only with `--export` | Cleaning without re-export would leave you with nothing useful. | |
| 119 | `export MATTER_PACKAGE_VERSION` | Child processes / Conan see it. | Recipes' `set_version()` can use override. |
| 120 | `REF=matter_app/VERSION@silabs` | SLT install reference. | Installing `matter_app` also pulls `matter` via requires. |
| 121 | Echo version | Visibility. | |
| 123–134 | Load `slc/tools/.env` if present | Brings in tools from `sl_setup_env.py` (`PATH`, etc.). | Need `slc`, compilers, java without manual setup. |
| 125–128 | `set -a` / source / `set +a` | Auto-export all vars from `.env`. | Tools become available to subprocesses. |
| 129–131 | Prepend `TOOLS_PATH` | Prefer setup-env tools. | |
| 133 | Warn if `.env` missing | Hint to run `python3 slc/sl_setup_env.py`. | |
| 136–139 | Prefer repo-local `slc/tools/slt` | Put it first on `PATH`. | Match team’s checked-in/setup SLT. |
| 141 | Require `slt` | Always needed. | |
| 142–146 | If building, also require `slc`, `make`, `find` | Export-only does not need generate/build tools. | |
| 148–150 | SLT Conan engine paths | Use SLT-managed Conan, not random system Conan. | Silabs packages expect SLT Conan home. |
| 152–156 | `slt install conan` + verify binary | Ensure engine exists. | First-run friendly. |
| 158–165 | Optional submodule update | Only matter_sdk, nlio, nlassert, QR-Code-generator. | External inputs for sample packaging; wifi/simplicity SDK are packages now, not submodules. |
| 167–185 | If `--export`: optional clean, then `export-pkg` matter then matter_app | Build local Conan packages from recipes. | Same version string for both. |
| 170–171 | `conan remove ... \|\| true` | Best-effort clean. | Don't fail if nothing to remove. |
| 175–178 | Export `matter` | `--name`, `--version`, `--user=silabs`. | Explicit identity in cache. |
| 181–184 | Export `matter_app` | Same version. | App package must align with stack. |
| 187–188 | `slt install REF -e conan` | Install from Conan engine into SLT layout. | Customer-like path. |
| 190–195 | `slt where` + check non-empty | Resolve install folders. | Later generate runs against installed tree. |
| 197–205 | Warn if ZAP / `matter_app.slsdk` markers missing | Soft checks for common packaging bugs. | Catch broken packages early. |
| 207–210 | Export-only: exit after install | Skip generate/build. | |
| 212–213 | Find `.slcp` under installed `matter_app` | Locate sample in package, not only in git tree. | Tests the *packaged* layout. |
| 215–217 | Derive app dir and out dir | `out/<board>/<appname>`. | Predictable build output. |
| 222 | `cd` into app dir | Generate expects to run near project. | |
| 224–225 | `slt install` in project | Resolve project `pkg.slt` deps. | |
| 227–233 | `slc generate` | Create makefile project for board. | Core SLC step. |
| 235–236 | Check makefile exists | Fail if generate silently incomplete. | |
| 238–239 | `make -j` | Build firmware. | End-to-end proof. |
| 241 | Print done path | | |

---

## 3b. `packages/build_app.sh`

Package-only builder: install tools + `matter_app` → generate → build. **No** `--export` and **no** submodule updates. Repo path: `packages/build_app.sh`. Shipped in the `matter_app` package as **`<pkg>/build_app.sh`** (package root).

| Behavior | Why |
|----------|-----|
| Requires `--slcp` and `--board` | Always builds an app; nothing else. |
| `slt install conan`, `slc_cli`, `zap` | SLT tools needed for generate (matches `matter` `slt_requirements`). |
| `ensure_os_cmd make` / `find` | OS packages via `apt-get` when missing (`make`, `findutils`). |
| Prefers `slt where slc_cli` on `PATH` if `slc` not found | SLT install may not refresh this shell’s `PATH`. |
| `slt install matter_app/<ver>@silabs` | Pulls stack + samples; finds `.slcp` under installed package. |
| Optional load of checkout `slc/tools/.env` | Convenience when run from a repo; not required. |

Example:

```bash
./packages/build_app.sh \
  --slcp matter_wifi_soc_lighting_app_freertos.slcp \
  --board brd4338a \
  --version 2.10.0-alpha.8
```

From an installed package:

```bash
"$(slt where matter_app)/build_app.sh" --slcp ... --board ...
```

---

## 4. `packages/_shared/base_recipe.py`

Shared Python base class for both Conan recipes.

### Imports and module setup

| Line(s) | What | Why |
|---------|------|-----|
| 1 | `from pathlib import Path` | Object-oriented paths. | Safer than string `os.path` joins. |
| 2 | `from conan import ConanFile` | Base class for recipes. | Required for Conan 2. |
| 3 | `from conan.tools.files import copy` | Conan-aware file copy into export/package. | Used when exporting `_shared`. |
| 4–5 | `os`, `re` | Env vars; version regex. | |
| 6 | `yaml` | Parse `dependency_versions.yaml`. | |
| 8 | Comment | File purpose. | |
| 10 | `_RECIPE_PATH = Path(__file__).resolve()` | Absolute path of this file. | Anchor for finding repo root. |
| 11–14 | `SHARED_REPO_ROOT = parents[2]` | From `packages/_shared/base_recipe.py` go up: `_shared` → `packages` → **repo root**. | Fallback if parents missing. |
| 16 | `_LINE_VERSION_RE = ^\d+\.\d+\.\d+$` | Regex for `2.10.0` only (no suffix). | Validate base version from SLCE. |

### Class `MatterBaseRecipe`

| Line(s) | What | Why |
|---------|------|-----|
| 19 | `class MatterBaseRecipe(ConanFile)` | Shared base. | DRY for matter + matter_app. |
| 20 | `user = "silabs"` | Conan user. | Packages publish as `...@silabs`. |
| 21–25 | license, author, homepage, url, topics | Package metadata. | Shown in remotes / tooling. |
| 26 | `python_requires = silabs_package_assistant/...` | Depend on Silabs packaging helper package. | Provides `get_version`, `find_slc_files_to_release`, `copy_files`, etc. |
| 28–35 | `sl_metadata` dict | Slack/Jira team metadata. | Silabs package manager conventions. |

### `set_version` (lines 37–52)

| Line(s) | What | Why |
|---------|------|-----|
| 37 | `def set_version(self)` | Conan hook to set `self.version`. | Dynamic versioning instead of hardcoding. |
| 38–45 | Docstring | Priority rules. | Matches Wiseconnect-style flow. |
| 46 | Read `MATTER_PACKAGE_VERSION` | Explicit override. | Local/CI one-offs (`dev_build_app.sh --version`). |
| 47–49 | If set → use it and return | Highest priority. | |
| 51 | Load assistant module | From `python_requires`. | Shared Silabs version logic. |
| 52 | `self.version = self.version or assistant.get_version(...)` | Keep CLI `--version` if already set; else compute from `matter.slce` + prerelease env. | Local → `2.10.0-0.dev`; CI → `2.10.0-alpha.N`. |

### `package_id` (54–56)

| Line | What | Why |
|------|------|-----|
| 56 | `self.info.clear()` | Package id ignores settings/options. | Content-only SDK package: one id per version. |

### `export_shared_recipe_support` (58–84)

| Line(s) | What | Why |
|---------|------|-----|
| 58–63 | Docstring | Explains ModuleNotFoundError without this. | Critical for SLT reload from cache. |
| 64 | `shared_src = recipe_folder.parent / "_shared"` | From `packages/matter` → `packages/_shared`. | |
| 65–72 | If exists, `copy` into `export_folder/_shared` | Exclude pycache and `.sh`. | Cached recipe can `import _shared`. Scripts not needed in cache. |
| 73–81 | Copy first found `dependency_versions.yaml` next to exported recipe | So cache can load dep versions without full git tree. | |
| 82–84 | Copy `matter.slce` into export folder | Version helpers need SLCE beside recipe in cache. | |

### Properties (86–120)

| Line(s) | What | Why |
|---------|------|-----|
| 86–89 | `repo_root` | Returns `SHARED_REPO_ROOT`. | All recipes share one root concept. |
| 91–101 | `matter_slce_path` | Prefer `recipe_folder/matter.slce` (cache), else repo root. | Works in git **and** Conan export cache. |
| 103–112 | `matter_line_version` | Base `X.Y.Z` via assistant; validate with regex. | Reject weird versions early. |
| 114–120 | `matter_conan_range` | Build `[>=2.10.0 <2.10.1,include_prerelease]`. | `matter_app` can depend on any prerelease on the 2.10.0 line. |

### Required root metadata helpers (Option A — shared by matter + matter_app)

Both recipes define their own `_REQUIRED_ROOT_FILES` tuple, then call the same two base methods:

```text
files_to_package.update(self._gather_required_root_files())
...
self._require_root_files(files_to_package)
```

| Method | What | Why |
|--------|------|-----|
| `_gather_required_root_files()` | For each path in subclass `_REQUIRED_ROOT_FILES`, if the file exists under `repo_root`, add the **repo-relative** name to a set. | Same “add required files” pattern for both packages. |
| `_require_root_files(files_to_package)` | **Hard-fail** if any `_REQUIRED_ROOT_FILES` entry is missing from the package set (handles relative or absolute entries). | Same guardrail; do not ship a package without SDK/ZAP root metadata. |

| Package | `_REQUIRED_ROOT_FILES` contents |
|---------|----------------------------------|
| `matter` | `matter.slsdk`, ZAP `app-templates.json`, ZAP `zcl.json` |
| `matter_app` | `matter_app.slsdk`, `matter_templates.xml` |

ZAP JSON stays in `matter` only (stack). App package only needs its SDK root markers.

### `dep_versions`

| Line(s) | What | Why |
|---------|------|-----|
| Property returns module-level `_DEP_VERSIONS` | Loaded once at import. | Fast; single source of truth YAML. |

### Helpers outside class

| Line(s) | What | Why |
|---------|------|-----|
| `_dependency_versions_candidates` | Candidate paths: repo `slc/script/...`, and (when running from exported `e/_shared/`) yaml at `e/`. | Same code works in tree and cache. |
| Loader docstring | Grouped vs flat YAML. | |
| Search candidates | Find file. | |
| Raise if not found | Fail fast. | |
| `yaml.safe_load` | Parse; wrap errors. | |
| Must be a mapping/dict | Validate shape. | |
| If keys include common/thread/wifi → merge groups | Flat map for Conan `requires()`. Later groups override. | Stack package needs **all** platform deps. |
| Else treat as legacy flat dict | Skip `None` values. | Backward compatible. |
| `_DEP_VERSIONS = _load_dep_versions_shared()` | Load at import time. | Cached for all recipe instances. |

---

## 5. `packages/matter/conanfile.py`

Recipe for the **matter** stack package.

### Imports and `_shared` bootstrap (1–25)

| Line(s) | What | Why |
|---------|------|-----|
| 1–8 | Standard imports | Paths, Conan, typing, yaml, sys. | |
| 9–11 | Logging comment | Conan `self.output.*` API hint. | |
| 13 | Comment about `repo_root` | Comes from base recipe now. | |
| 16–24 | Try: add `_shared` parent to `sys.path` | Prefer directory of this file (cache `e/`), else parent (`packages/`). | `from _shared.base_recipe import ...` works after export. |
| 25 | Import `MatterBaseRecipe` | Inherit shared behavior. | |

### Class header and options (28–74)

| Line(s) | What | Why |
|---------|------|-----|
| 28 | `class matterRecipe(MatterBaseRecipe)` | Stack recipe. | |
| 29 | `name = "matter"` | Conan package name. | Explicit (was implicit before). |
| 30 | Comment on dynamic version | Version from base `set_version`. | |
| 31 | `description` | Human string. | |
| 33–34 | Optional `revision_mode` commented out | SCM revision mode not used. | |
| 36–56 | Docstring of SLT option meanings | Documentation only. | |
| 58–64 | `options = {...}` | Declare SLT-related Conan options. | Studio/SLT metadata knobs. |
| 68–74 | `default_options` | Defaults; `packageType: sdk`. | Treated as SDK package. |

### Required root files (`_REQUIRED_ROOT_FILES`)

| What | Why |
|------|-----|
| Tuple: `matter.slsdk`, `src/app/zap-templates/app-templates.json`, `src/app/zap-templates/zcl/zcl.json` | Must ship in stack package. Without them, generate can fall back to **Zigbee** ZCL apack → wrong code. |
| Used via base helpers `_gather_required_root_files()` + `_require_root_files()` | Same Option A pattern as `matter_app`. |

### Folder + requirements

| What | Why |
|------|-----|
| `matter_folder` → `repo_root` | Source root for copying. |
| `requirements()` | For each entry in `dep_versions`, `self.requires(name/version@silabs)`. Pulls thread/wifi/zigbee/etc. from YAML. |
| `slt_requirements` | Need `zap` and `slc_cli` tools via SLT (`~` = any compatible). |

### Empty hooks

`layout` / `deploy` empty — placeholders Conan may call.

### `export`

| What | Why |
|------|-----|
| `export_shared_recipe_support()` | Copy `_shared`, yaml, slce into export. |
| Also copy `matter.slce.extra` if present | Packaging manifest travels with recipe. |

### `package_id`

Same as base: clear info → content-only id.

### `package` — create package contents

| What | Why |
|------|-----|
| `os.chdir(self.repo_root)` | Relative paths resolve from repo root. |
| Start set with `"License"` | Always include license. |
| Process `matter.slce.extra` | Extra files not discovered via SLCC alone. Sample-app paths (`slc/apps/**`, `.slcp`/`.slcw`) are **skipped** here — they belong in `matter_app`. |
| `find_slc_files_to_release` | Collect production/evaluation/experimental matter SLCCs (`include_slcp=False`). |
| `files_to_package.update(self._gather_required_root_files())` | Add stack root metadata that exists on disk. |
| `_normalize_existing_repo_files` | Drop missing; unify path form. |
| `_require_root_files` | **Hard fail** if any `_REQUIRED_ROOT_FILES` still missing. |
| Split `.a` static libs; `copy` / `copy_files` | Package contents into `package_folder`. |
| Optional `conan-matter.lock` + `generate_metadata` | Lockfile + SLT metadata. |

### `build` — file list for filter-repo / CI

Same gathering as `package` (including gather/require root files), but writes `matter-filter-repo-filelist.txt` and pathmap for git filter workflows (qualities without experimental). Sorted for stable diffs.

### `package_info`

Appends `package_folder` to `SLC_SDK_PACKAGE_PATH` so SLC finds this SDK.

### Helpers (matter-specific)

| Helper | What | Why |
|--------|------|-----|
| `_resolve_repo_path` / `_to_repo_relative` / `_normalize_existing_repo_files` | Path normalization for packaging lists. | Consistent repo-relative copies. |
| `_matter_extra_skip_reason` (262–269) | Return a skip reason for `slc/apps/**` or any `.slcp`/`.slcw`; else `None`. | Keeps sample projects out of the **matter** stack package (owned by **matter_app**). |
| `_process_slce_extra` (271–357) | Find/parse `matter.slce.extra` (recipe folder, `packages/matter/`, or repo root). For each `extra_files` entry: skip with logged reason if sample-app; warn if missing; else keep. Ends with a summary (`skipped N sample-app path(s), M missing…`). | Extra content + CI path maps; works after export; belt-and-suspenders if regenerator left stale sample paths. |
| `_get_local_slce_file` | Require `matter.slce` at repo root; return relative name. | Discovery entry point. |

#### Sample-app skip logging (package / build time)

Every intentional skip is logged at Conan `info`:

```text
matter.slce.extra: skipped slc/apps/.../foo.slcp: sample-app content (owned by matter_app package)
matter.slce.extra: skipped N sample-app path(s), M missing path(s); kept K file(s)
```

Missing listed files still use `warning` (unchanged).

Root-file require logic lives in **`MatterBaseRecipe`**, not here.

---

## 6. `packages/matter_app/conanfile.py`

Recipe for the **matter_app** sample-apps package.

Owns all `.slcp` / `.slcw` under `slc/apps/` (and related sample inputs). Those paths are intentionally **not** packaged via `matter.slce.extra` / the `matter` recipe.

### Bootstrap (1–24)

Same pattern as matter: put `_shared` on `sys.path`, import `MatterBaseRecipe`.

### Class header

| What | Why |
|------|-----|
| `name = "matter_app"` | Package name. |
| Dynamic version | Same versioning as matter. |
| `_REQUIRED_ROOT_FILES` = (`matter_app.slsdk`, `matter_templates.xml`) | App SDK root markers so SLC accepts this folder as an SDK. Same Option A pattern as matter (different file list). |
| SLT options / defaults | Same idea as matter; `packageType: sdk`. |

### Folder + requirements

| What | Why |
|------|-----|
| `matter_app_folder` → repo root | Copy source root. |
| `requires(matter/{matter_conan_range}@silabs)` | Depend on compatible matter line **including prereleases**. |

### Hooks

| What | Why |
|------|-----|
| Empty layout/deploy | |
| `export` → `export_shared_recipe_support()` | Cache can import `_shared`. |
| `package_id` clear | Content-only. |

### `package`

| What | Why |
|------|-----|
| Start with License | |
| Qualities = production/evaluation; packages = matter | Filter which samples to ship. |
| `_gather_slc_release_files` | Discover `.slcp`/`.slcw` + assistant-related files. |
| `_gather_required_root_files()` | Add `matter_app.slsdk` + `matter_templates.xml` (shared Option A helper). |
| `_gather_slcp_external_inputs` | Add files referenced by relative paths (often under `third_party/matter_sdk`). |
| Add `packages/build_app.sh` | Ship independent builder; **`package()` copies it to `<pkg>/build_app.sh`** (not under `packages/`). Uses `_existing_repo_relative_files` so cwd during export-pkg cannot drop paths. |
| Filter to existing paths; re-add root files; `_require_root_files` | Absolute-path exists-filter can drop relative root names — re-add then **hard fail** if still missing. |
| Copy `.a` then other files; optional lockfile; metadata | |

### `build`

Same gathering as package (including gather/require root files); writes `matter_app-filter-repo-*.txt` (pathmap currently empty list).

### `package_info`

Appends package folder to `SLC_SDK_PACKAGE_PATH` (same as matter).

### Helpers (matter_app-specific)

Root metadata uses **`MatterBaseRecipe._gather_required_root_files` / `_require_root_files`** — there is no separate `_gather_sdk_root_marker_files`.

### `_iter_slc_path_entries`

Recursive walk of dict/list YAML; yield every string value of key `"path"`.

**Why:** `.slcp` nests `path:` deeply under source/include/etc.

### `_INPUT_PATH_KEYS`

Only these sections are treated as **inputs**: `source`, `include`, `config_file`, `other_file`, `readme`, `post_build`, `postbuild`.

**Why:** Skip export/artifact outputs (e.g. `artifact/*.o`) that must not be packaged as sources.

### `_iter_input_path_entries`

For each input key present in the project YAML, yield paths via `_iter_slc_path_entries`.

### `_slc_project_selected` (248–266)

| Line(s) | What | Why |
|---------|------|-----|
| 255–257 | If `quality` set and not in desired list → reject | Only prod/eval samples. | |
| 259–261 | If `package` field in desired → accept | Direct package tag. | |
| 263–265 | Or any `sdk_extension[].id` in desired → accept | Extensions declare Matter dependency this way. | |
| 266 | Else false | | |

### `_gather_slcp_external_inputs` (268–340) — critical new logic

| Line(s) | What | Why |
|---------|------|-----|
| 273–282 | Docstring | Explains relative `third_party/matter_sdk` paths must exist inside package. | |
| 283–285 | Init root, collected, missing | | |
| 287–291 | `rglob("*.slc*")` but only `.slcp`/`.slcw`; skip `third_party` | Don't parse nested third-party projects as Matter samples. | |
| 293–297 | YAML load; warn and skip on error | Robustness. | |
| 299–302 | Must be dict + selected | | |
| 304–307 | For each input path: skip bare filenames without `/` or `.` | Those are file-list names, not repo paths. | |
| 309 | Resolve path relative to `.slcp` directory | Same as SLC would. | |
| 310–314 | Must stay inside repo | Outside repo → record missing. | |
| 316–318 | Must exist | Else missing (often uninitialized submodule). | |
| 320–325 | File → add; dir → add all files under it | Directory includes are expanded. | |
| 327–334 | If any missing → raise with helpful message | Fail export early; tell user to init `matter_sdk`. | |
| 336–340 | Log count; return set | Visibility. | |

### `_gather_slc_release_files` (342–376)

| Line(s) | What | Why |
|---------|------|-----|
| 353–361 | Scan `.slcp`/`.slcw` outside third_party | Candidate samples. | |
| 364–369 | `assistant.list_files_in_slc_file(...)` | Related files for that project. | |
| 370–372 | Warn on failure; continue | Don't abort whole package for one bad file. | |
| 373–375 | If related nonempty: add project + related | Only include matching quality/package. | |

---

## 7. `packages/matter/pkg.slt`

```toml
1| # Version defaults to "0" if not defined
2| version = "0"
3|
4|
5| [dependency]
6| # Get a specific version of the package
7| matter = {version = ">=2.10.0 <2.10.1", installer = "conan", user="silabs", prerelease = true}
```

| Line | What | Why |
|------|------|-----|
| 1–2 | SLT file schema version `"0"` | Not the Matter product version. |
| 5 | Dependency section | |
| 6 | Comment | |
| 7 | Depend on Conan package `matter` in range 2.10.0 ≤ v < 2.10.1, user `silabs`, allow prereleases | Aligns with current Matter line; `user` required for `@silabs`; `prerelease=true` allows `-alpha.N` / `-0.dev`. |

**Change from before:** was `2.8.x` without `user="silabs"`.

---

## 8. `packages/matter_app/pkg.slt`

Same structure as matter's `pkg.slt`, but dependency name is `matter_app` with range `>=2.10.0 <2.10.1`, `user="silabs"`, `prerelease = true`.

**Why:** SLT installs the sample-app package (which then pulls `matter` via Conan requires).

---

## 9. `packages/remotes.json`

```json
{
 "remotes": [
  {
   "name": "silabs-conan-production",
   "url": "https://artifactory-local.silabs.net/artifactory/api/conan/silabs-conan-production",
   "verify_ssl": true
  }
 ]
}
```

| Field | What | Why |
|-------|------|-----|
| `remotes` | List of Conan remotes Conan/SLT may register | Where to download packages. |
| `name` | Logical remote name | Referenced by tooling. |
| `url` | Artifactory Conan API endpoint | Production Silabs packages. |
| `verify_ssl` | Verify HTTPS certs | Security. |

**What was removed:** Extra remotes (`gsdk-*`, `wiseconnect-conan-sqa`, `netstack-conan-sqa`, `studio-conan-development`, etc.).

**Why:** Narrow search to the remotes Matter packaging actually needs; fewer wrong-version / wrong-repo hits; simpler local setup.

---

## How to use this knowledge (quick recipes)

**Local export + build a Wi-Fi lighting sample:**

```bash
./packages/dev_build_app.sh \
  --export \
  --slcp matter_wifi_soc_lighting_app_freertos.slcp \
  --board brd4338a \
  --update-submodules
```

**Package-only build (no export / submodules; installs slc_cli, zap, make, find):**

```bash
./packages/build_app.sh \
  --slcp matter_wifi_soc_lighting_app_freertos.slcp \
  --board brd4338a \
  --version 2.10.0-alpha.8
# or: "$(slt where matter_app)/build_app.sh" --slcp ... --board ...
```

**CI-style shared prerelease env (then export both packages):**

```bash
source packages/_shared/prerelease_env.sh
set_prerelease_env
# then conan export-pkg / publish with same shell env
```

**Override version explicitly:**

```bash
export MATTER_PACKAGE_VERSION=2.10.0-alpha.8
# or: ./packages/dev_build_app.sh --version 2.10.0-alpha.8 --export ...
```

---

## Related files outside `packages/` (context only)

| File | Role |
|------|------|
| `matter.slce` | Extension definition; base version source. |
| `matter.slsdk` | Stack SDK root marker + ZAP property pointers. |
| `matter_app.slsdk` | App package SDK root marker. |
| `slc/script/dependency_versions.yaml` | Thread/Wi-Fi/common Conan dep versions. |
| `packages/matter/matter.slce.extra` | Extra files to force into `matter` package. **Does not** list `slc/apps/**` sample projects (those ship via `matter_app`). |
| `slc/script/get_slce_extra_paths.py` | Regenerates `components` + `extra_files` (+ SDK path block) in `matter.slce.extra`. |

### `slc/script/get_slce_extra_paths.py` — sample-app exclusion

`extra_files` is rebuilt as: **git-tracked extension files − paths already referenced by `.slcc` components**.

| Helper / behavior | What | Why |
|-------------------|------|-----|
| `_exclusion_reason` (57–75) | Return skip reason for `slc/apps/**`, stray `.slcp`/`.slcw`, hidden dirs, git meta, `__pycache__`; else `None`. | Sample apps must not enter the **matter** package manifest. |
| `_git_tracked_extension_paths` (77–113) | Walk `git ls-files`; for each path print `skipped <path>: <reason>` (stderr) when excluded; keep the rest. Prints a kept/skipped summary. | Auditable regenerator; every skip has a reason. |

Example regenerator log:

```text
skipped slc/apps/.../foo.slcp: sample-app content (owned by matter_app package)
extension path scan: kept 516, skipped 282
```

Re-run after submodule / tree changes:

```bash
python3 slc/script/get_slce_extra_paths.py --slce-extra packages/matter/matter.slce.extra
```

**Ownership split:** `matter` = stack/components; `matter_app` discovers `.slcp`/`.slcw` via `_gather_slc_release_files` / `_gather_slcp_external_inputs`.

---

*Generated as a learning aid for Matter Package Manager changes under `packages/`.*
