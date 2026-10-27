# CI overview for `release_2.10-1.6.1`

This document describes GitHub Actions that apply to the Matter Extension branch
`release_2.10-1.6.1`: scheduled (daily / nightly / weekly), push, and PR.

Package-manager lock details live in
[`.github/pkg-manifest/README.md`](pkg-manifest/README.md).

## Two build paths

| Path | When it runs for this branch | How apps are built |
| --- | --- | --- |
| **Packages** | Push to `release_2.10-1.6.1`; scheduled / manual dispatch of Packages Validation | Export `matter` / `matter_app` Conan packages, then `*-pkg` builders |
| **Legacy SLC** | Pull requests targeting `release_*` | SLC project generation + classic builders (`dev-apps-builder.yaml`, etc.) |

Packages Validation explicitly keeps **PR gates on legacy CI**. Package
lockfiles under `.github/pkg-manifest/` are used by the packages path
(push / daily unlock / nightly locked / Thursday SQA when that path runs).

---

## Schedule summary (UTC)

| Cadence | Cron | Local (approx. EDT) | Workflow | Packages Validation mode |
| --- | --- | --- | --- | --- |
| **Daily** lock-refresh | `5 0 * * *` | ~8:05 pm | `trigger-matter-packages-validation.yaml` → Packages Validation | `use_lockfile=false` (always) |
| **Nightly** Matter-delta | `5 6 * * *` | ~2:05 am | Same trigger → Packages Validation | `use_lockfile=true` (only if commits in last 24h) |
| **Weekly** SQA | No separate cron | Thursday (America/New_York) | Inside Packages Validation → `dev-apps-builder-pkg` | Same lock mode as the parent run |

Crons are staggered (~6 hours). Concurrency also splits unlock vs locked:

`create-matter-packages-<ref>-unlock` vs `…-locked`, so a push cannot cancel
a daily unlock (and vice versa).

```text
Daily 00:05 UTC ──► Packages Validation (unlocked) ──► lock refresh PR on success
Nightly 06:05 UTC ─► if commits in 24h ──► Packages Validation (locked)
Any Packages run on Thu (ET) ──► also Build SQA apps (custom-sqa)
```

---

## Daily — lock refresh (floating package deps)

**Purpose:** Let third-party Silabs Conan packages float within
`dependency_versions.yaml` / `pkg.slt` ranges, prove the branch still builds,
then promote a new certified pin set.

| Item | Value |
| --- | --- |
| Trigger | `trigger-matter-packages-validation.yaml` job `trigger_daily_lock_refresh` |
| Schedule | Every day `5 0 * * *` |
| Commit gate | **None** (deps can move without Matter commits) |
| Dispatch | `use_lockfile=false`, `build_dev_apps=true`, `ota_size_check=true` |
| Orchestrator | `matter-packages-validation.yaml` |
| Build type | `full` (because ref is `release_2.10-1.6.1`) |
| After green | Unlocked `lock_app`/`siwx-soc` uploads seed `pkg.lock`; job |
| | **Update CI pkg.lock and conan.lock** promotes that artifact (no |
| | re-resolve) and opens PR on |
| | `automation/pkg-manifest-lock-release_2.10-1.6.1` updating |
| | `.github/pkg-manifest/{pkg.lock,conan.lock,conanfile.txt}` |

If daily fails, committed locks are left unchanged.

Manual equivalent: run Packages Validation on `release_2.10-1.6.1` with
`use_lockfile=false`.

---

## Nightly — locked Matter-delta validation

**Purpose:** Validate Matter / extension code changes against the **committed**
pin set so package churn is not a variable.

| Item | Value |
| --- | --- |
| Trigger | `trigger-matter-packages-validation.yaml` job `trigger_locked_matter_validation` |
| Schedule | Every day `5 6 * * *` |
| Commit gate | Yes — checkout `release_2.10-1.6.1`; skip unless |
| | `git rev-list --count --since="24 hours ago" HEAD > 0` |
| Dispatch | `use_lockfile=true`, `build_dev_apps=true`, `ota_size_check=true` |
| Lock refresh PR | **No** |

Same packages pipeline as a locked push: create Matter packages → full Dev apps
→ OTA size check (pkg path).

---

## Weekly — Thursday SQA (packages path)

There is no dedicated weekly cron. SQA is decided inside
`dev-apps-builder-pkg.yaml` when Packages Validation runs:

- Weekday captured once at start in `America/New_York` (`date +%u`; `4` = Thursday)
- `run-sqa=true` when `github.ref_name` matches `release_*` **and** day is Thursday
- Then job **Build SQA apps** calls `sqa-apps-builder-pkg.yaml` (`build-type: custom-sqa`)

So on Thursdays, whichever Packages Validation run fires (daily unlock, nightly
locked if gated on, push, or manual) that reaches Dev apps with `run-sqa=true`
also builds SQA apps with the same `use-lockfile` mode as that run.

Also on packages Dev builds for this branch: coverage builder, wait-for-test-results
(SQA sanity), merge artifacts — see `dev-apps-builder-pkg.yaml`.

---

## Push to `release_2.10-1.6.1`

### Packages Validation (locked)

| Item | Value |
| --- | --- |
| Workflow | `matter-packages-validation.yaml` (`on.push` for this branch only) |
| Lock mode | Always `use_lockfile=true` (push never unlocks) |
| Jobs | Create Matter packages → Build Dev apps (`full`) → OTA flash size (pkg) |
| Lock refresh | No |

### Other push workflows (`release_*`)

| Workflow | Role |
| --- | --- |
| `validate-metadata.yaml` | Package field, path lengths, metadata checks |
| `validate-gitmodules-branches.yaml` | `matter_sdk` / `matter_support` branch entries |
| `build-zephyr.yaml` | Zephyr example builds (matrix includes main/release-only rows) |
| `cache-sdks.yaml` | Seed SDK cache when `.gitmodules` / SDK paths change |

---

## PR level (into `release_2.10-1.6.1`)

PRs targeting `release_*` use the **legacy** path. Packages Validation does
**not** run on `pull_request`.

| Workflow | Role |
| --- | --- |
| `dev-apps-builder.yaml` | Build Dev apps — **standard** build type on PR |
| `ota-size-checker.yaml` | OTA flash space (legacy SLC) |
| `validate-metadata.yaml` | Same metadata checks as push |
| `validate-gitmodules-branches.yaml` | Submodule branch validation |
| `code-size-check.yaml` | Code size vs base SHA |
| `build-zephyr.yaml` | Zephyr builds on PR |
| `pr-validation.yaml` | Requires `**Testing Done:**` and `**Description of Fix/Solution:**` in body (bots skipped) |
| `CLA-Assistant.yml` | CLA |
| `require-admin-action-check.yaml` | Fails if `sl-require-admin-action` label is present |

Legacy Dev apps on `release_*` also wires coverage / SQA-related follow-ups
similar to the packages builder; see `dev-apps-builder.yaml` for branch filters.

---

## Lock mode cheat sheet (packages path only)

| Event | `use_lockfile` | Floats third-party deps? | Opens lock refresh PR? |
| --- | --- | --- | --- |
| Push to `release_2.10-1.6.1` | `true` | No | No |
| Daily schedule dispatch | `false` | Yes | Yes (if green) |
| Nightly schedule dispatch (24h commits) | `true` | No | No |
| Manual dispatch | Input (default `true`) | Only if `false` | Only if `false` and green |

Mode selection is in `matter-packages-validation.yaml` job `resolve-deps-mode`:
unlock is allowed only for
`ref == release_2.10-1.6.1` + `workflow_dispatch` + `use_lockfile == false`.

---

## Manual / on-demand (useful on this branch)

| Workflow | Notes |
| --- | --- |
| `matter-packages-validation.yaml` | Full packages run; set `use_lockfile` / build / OTA flags |
| `sdk-submodule-bump.yaml` | SiSDK bump helper (targets older release lines by default; check inputs) |
| `update-matter_sdk.yml` | Manual can run on current ref; **scheduled** targets are `main` and `release_2.9-1.6` only — **not** `release_2.10-1.6.1` |
| `slc-cli-scripts.yml`, `version-update.yml`, `build-ot-rcp.yaml` | Tooling / one-offs |

---

## Not currently scheduled for `release_2.10-1.6.1`

| Automation | Current targets |
| --- | --- |
| Daily `update-matter_sdk.yml` schedule | `main`, `release_2.9-1.6` |
| Dependabot `matter_support` gitsubmodule | `main`, `release_2.9-1.6` |
| Dependabot github-actions | Weekly, repo root (not branch-specific) |

---

## Key workflow files

| File | Role |
| --- | --- |
| `.github/workflows/trigger-matter-packages-validation.yaml` | Daily unlock + nightly locked dispatches |
| `.github/workflows/matter-packages-validation.yaml` | Packages orchestrator + lock refresh job |
| `.github/workflows/dev-apps-builder-pkg.yaml` | Packages Dev apps + Thursday SQA gate |
| `.github/workflows/sqa-apps-builder-pkg.yaml` | SQA app matrix (packages) |
| `.github/workflows/ota-size-checker-pkg.yaml` | OTA check (packages) |
| `.github/workflows/dev-apps-builder.yaml` | Legacy Dev apps (PR) |
| `.github/workflows/ota-size-checker.yaml` | Legacy OTA (PR) |
| `.github/pkg-manifest/` | Committed CI pin set (`pkg.lock` source of truth) |
| `.github/workflows/validate-pkg-manifest.yaml` | Sync check: `pkg.lock` → regenerate Conan files, fail on drift |

---

## Related docs

- [`.github/pkg-manifest/README.md`](pkg-manifest/README.md) — lock formats, convert script, install flow
