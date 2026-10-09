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

1. **PR CI** installs that pin set so builds are reproducible.
2. **Nightly CI** resolves freely with `slt install`, and on success refreshes
   the pins so the next day’s PRs pick up a validated set.

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

4. Install the PR Matter app package:

   ```bash
   slt install "matter_app/<PR_VERSION>@silabs" -e conan
   ```

5. Export `CI_PKG_LOCK` to the absolute path of `pkg.lock`.
6. For each app build, `build_app.sh`:
   - Copies `CI_PKG_LOCK` into the app directory as `pkg.lock`.
   - Rewrites `matter` / `matter_app` entries to the PR package version
     (drops recipe revision so local `export-pkg` packages resolve).
   - Runs `slt install --check-updates=false` so SLT does not float.

Result: third-party packages stay at the certified pins; only Matter code under
test comes from the PR.

## Nightly CI (resolve + refresh)

Triggered by `.github/workflows/trigger-matter-packages-validation.yaml` with
`use_lockfile=false`.

Flow:

1. **Build** without installing `.github/pkg-manifest` locks.
2. App builds use normal `slt install` (`CHECK_UPDATES=true`) so newly published
   packages matching `pkg.slt` ranges can be pulled.
3. If the package app builds (and OTA check, when enabled) succeed, the
   **Update CI pkg.lock and conan.lock** job:
   - Runs unlocked `slt install` in `slc/apps/lock_app/wifi`.
   - Copies the produced `pkg.lock` to `.github/pkg-manifest/pkg.lock`.
   - Runs `pkg_lock_to_conan_lock.py` to refresh `conan.lock` and
     `conanfile.txt`.
   - Commits and pushes the three files on the branch that was dispatched
     (for example `release_2.10-1.6.1`).

If nightly fails, the previous committed locks are left unchanged, so PRs keep
using the last green pin set.

## Manual update (local)

Use this when you want to refresh pins without waiting for nightly:

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
`conan.lock` alone unless you also update `pkg.lock` (or accept drift).

## Secrets / remotes

| Name | Purpose |
| --- | --- |
| Job `contents: write` + `GITHUB_TOKEN` | Nightly commit/push of refreshed locks (branch protection may require a bot PAT). |

Remote used by CI (same as `create-and-cache-matter-packages` / `install-tools`; no Artifactory login):

```bash
conan remote add -f conan-prerelease https://conan-prerelease.silabs.net/
```

## Related code

| Path | Role |
| --- | --- |
| `slc/script/pkg_lock_to_conan_lock.py` | `pkg.lock` → `conan.lock` + `conanfile.txt` |
| `.github/actions/install-pkg-manifest/` | Restore Matter cache; locked Conan install; set `CI_PKG_LOCK` |
| `packages/build_app.sh` | Honors `CI_PKG_LOCK` / `--pkg-lock` and `CHECK_UPDATES` |
| `.github/workflows/matter-packages-validation.yaml` | PR vs nightly mode; nightly lock refresh job |
| `.github/workflows/trigger-matter-packages-validation.yaml` | Daily dispatch with `use_lockfile=false` |
| `slc/script/dependency_versions.yaml` | Floating ranges for local/dev `pkg.slt` generation (not the CI pin set) |

## Seed note

The initial `pkg.lock` was taken from `slc/apps/lock_app/wifi/pkg.lock` (a
representative Wi‑Fi app resolve that also includes shared Thread/platform
packages). Nightly (or a manual refresh) should replace it with a newly
resolved lock after a green package validation run.
