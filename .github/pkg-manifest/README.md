# CI package dependency locks

This directory holds **CI-only** dependency pins for Matter package validation
workflows (`.github/workflows/matter-packages-validation.yaml` and the package
builders it calls).

These files are **not** part of the `matter` / `matter_app` Conan packages.
Packaging pulls SLC/SDK trees and explicit recipe roots; it does not ship
`.github/`.

## Why this exists

Package CI depends on many Silabs Conan packages (direct and transitive).
Floating ranges (for example in `slc/script/dependency_versions.yaml` /
generated `pkg.slt`) can pick up newly published prereleases and break PR CI
even when Matter code did not change.

This directory stores a **certified pin set**:

1. **PR / push / locked Matter CI** installs that pin set so builds are reproducible.
2. **Daily lock-refresh CI** resolves freely with `slt install`, and on success
   refreshes the pins so later locked runs pick up a validated set.

## Files

| File | Format | Role |
| --- | --- | --- |
| `pkg.lock` | SLT TOML-like lock | **Source of truth.** Exact pins from `slt install` (versions + Conan recipe revisions, plus archive tools). |
| `conan.lock` | Conan 2 JSON lock (`version: "0.5"`) | **Derived.** Used by `conan install --lockfile=...`. |
| `conanfile.txt` | Conan requires list | **Derived.** Companion graph for `conan install <dir> --lockfile=...`. |
| `README.md` | Markdown | This document. |

### Important: two lock formats

| | `pkg.lock` | `conan.lock` |
| --- | --- | --- |
| Consumer | `slt install` | `conan install --lockfile` |
| Shape | `[dependency]` entries with `installer`, `type`, `ref` | JSON `requires` array of `name/version@user#revision` |
| Compatible with each other? | **No** — do not pass `pkg.lock` to `--lockfile` |

Always treat `pkg.lock` as the source and regenerate Conan files from it.

## Source of truth and conversion

```text
slt install  -->  pkg.lock  -->  pkg_lock_to_conan_lock.py  -->  conan.lock
                                                         \-->  conanfile.txt
```

Converter script (repo root):

```bash
python3 slc/script/pkg_lock_to_conan_lock.py \
  --input .github/pkg-manifest/pkg.lock \
  --output .github/pkg-manifest/conan.lock \
  --conanfile .github/pkg-manifest/conanfile.txt
```

What the converter does:

- Keeps only entries with `installer = "conan"`.
- Skips archive/tool packages (`commander`, `slc-cli`, `python`, `java21`, `zap`, …).
- By default **omits** `matter` and `matter_app` so CI can install PR-built
  Matter packages on top of the locked third-party set.
- Prefers each entry’s `ref = "name/version@silabs#revision"` when present.
- Adds Silabs recipe `python_requires` (default
  `silabs_package_assistant/1.8.0@silabs#...`) — required by Conan 2 lock
  installs; not present in SLT `pkg.lock`.
- Writes a minimal `conanfile.txt` with exact `name/version@silabs` requires
  (revision stripped in the requires list; revisions stay in `conan.lock`).

Optional flag:

```bash
# Include matter/matter_app in the Conan lock (normally not needed in CI)
python3 slc/script/pkg_lock_to_conan_lock.py --include-matter ...
```

## PR CI (locked / stable)

Triggered on pull requests into `main` / `release_*` with `use_lockfile=true`
(default).

Flow (via `.github/actions/install-pkg-manifest` + `packages/build_app.sh`):

1. Restore the Actions cache that contains the PR’s exported `matter` /
   `matter_app` packages.
2. Configure the Conan remote (`conan-prerelease`).
3. Install third-party deps:

   ```bash
   conan install .github/pkg-manifest \
     --lockfile=.github/pkg-manifest/conan.lock \
     -r conan-prerelease
   ```

4. Install the PR Matter app package (no float after the lock install):

   ```bash
   slt install "matter_app/<PR_VERSION>@silabs" -e conan --check-updates=false
   ```

5. Export `CI_PKG_LOCK` (absolute path of `pkg.lock`) and `CHECK_UPDATES=false`
   to `GITHUB_ENV` so later `build_app.sh` steps inherit both.
6. For each app build, `build_app.sh`:
   - Copies `CI_PKG_LOCK` into the app directory as `pkg.lock`.
   - Rewrites `matter` / `matter_app` entries to the PR package version
     (drops recipe revision so local `export-pkg` packages resolve).
   - Runs `slt install --check-updates=false` so SLT does not float.

Result: third-party packages stay at the certified pins; only Matter code under
test comes from the PR.

## Daily CI (resolve + refresh)

Lock refresh runs only on `release_2.10-1.6.1` when dispatched with
`use_lockfile=false`:

- Daily schedule (`5 0 * * *`) via
  `.github/workflows/trigger-matter-packages-validation.yaml` (always; no
  Matter commit gate — package deps can move without Matter commits)
- Manual `workflow_dispatch` with `use_lockfile=false`

Pushes (including to `release_2.10-1.6.1`) install the committed locks and do
not open a refresh pull request.

Flow:

1. **Build** without installing `.github/pkg-manifest` locks.
2. App builds use normal `slt install` (`CHECK_UPDATES=true`) so newly published
   packages matching `pkg.slt` ranges can be pulled.
3. The unlocked `lock_app` / `siwx-soc` (wifi) builder uploads the `pkg.lock`
   produced by that green build as artifact `ci-unlocked-pkg-lock`.
4. If the package app builds (and OTA check, when enabled) succeed, the
   **Update CI pkg.lock and conan.lock** job:
   - Downloads that seed artifact (no post-green re-resolve).
   - Copies it to `.github/pkg-manifest/pkg.lock`.
   - Runs `pkg_lock_to_conan_lock.py` to refresh `conan.lock` and
     `conanfile.txt`.
   - Opens a pull request (via `silabs-matter-ci-bot`) with the three files
     against the dispatched branch (for example `release_2.10-1.6.1`).
     Reuses `automation/pkg-manifest-lock-<branch>` if a refresh PR is already open.

If daily lock-refresh fails, the previous committed locks are left unchanged,
so locked CI keeps using the last green pin set.

## Nightly / Matter-delta CI (locked)

Validates Matter code changes against the committed pin set
(`use_lockfile=true`):

- Nightly schedule (`5 6 * * *`) via
  `.github/workflows/trigger-matter-packages-validation.yaml`
- Runs only if `release_2.10-1.6.1` had commits in the last 24 hours
- Same locked install path as push/PR (no lock refresh PR)

## Manual update (local)

Use this when you want to refresh pins without waiting for daily:

```bash
# From repo root, with slt/conan configured and remotes available
python3 slc/script/generate_pkg_slt.py -d slc   # if pkg.slt missing
rm -f slc/apps/lock_app/wifi/pkg.lock
( cd slc/apps/lock_app/wifi && slt install --check-updates=true )

mkdir -p .github/pkg-manifest
cp -f slc/apps/lock_app/wifi/pkg.lock .github/pkg-manifest/pkg.lock

python3 slc/script/pkg_lock_to_conan_lock.py \
  --input .github/pkg-manifest/pkg.lock \
  --output .github/pkg-manifest/conan.lock \
  --conanfile .github/pkg-manifest/conanfile.txt

# Review diff, then commit all three files together
git add .github/pkg-manifest/pkg.lock \
        .github/pkg-manifest/conan.lock \
        .github/pkg-manifest/conanfile.txt
```

Always convert after editing or replacing `pkg.lock`. Never hand-edit
`conan.lock` alone unless you also update `pkg.lock`.

## Secrets / remotes

Remote used by CI (same as `create-and-cache-matter-packages` / `install-tools`; no Artifactory login):

```bash
conan remote add -f conan-prerelease https://conan-prerelease.silabs.net/
```

## Related code

| Path | Role |
| --- | --- |
| `slc/script/pkg_lock_to_conan_lock.py` | `pkg.lock` → `conan.lock` + `conanfile.txt` |
| `.github/actions/install-pkg-manifest/` | Restore Matter cache; locked Conan install; sole exporter of `CI_PKG_LOCK` + `CHECK_UPDATES` |
| `packages/build_app.sh` | Honors `CI_PKG_LOCK` / `--pkg-lock` and `CHECK_UPDATES`; removes leftover `pkg.lock` when unlocked |
| `slc/build-pkg.sh` | Local entry: `--use-lockfile` / `--pkg-lock` / `--check-updates`; forwards locks to `build_app.sh` on `--build-from-package-version` |
| `.github/workflows/matter-packages-validation.yaml` | Locked vs daily unlocked mode; promotes seed lock from green wifi build |
| `.github/workflows/trigger-matter-packages-validation.yaml` | Daily unlock (`use_lockfile=false`) + nightly locked Matter-delta (`use_lockfile=true`, 24h gate) |
| `.github/workflows/validate-pkg-manifest.yaml` | PR/push: regenerate Conan files from `pkg.lock` and fail on drift |
| `slc/script/dependency_versions.yaml` | Floating ranges for local/dev `pkg.slt` generation (not the CI pin set) |

## Seed note

The initial `pkg.lock` was taken from `slc/apps/lock_app/wifi/pkg.lock` (a
representative Wi‑Fi app resolve that also includes shared Thread/platform
packages). Daily lock-refresh (or a manual refresh) should replace it with a
newly resolved lock after a green package validation run.
