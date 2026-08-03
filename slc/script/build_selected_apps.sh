#!/usr/bin/env bash
# Build selected Matter sample apps via ./slc/build.sh
#
# Usage:
#   ./slc/script/build_selected_apps.sh --flavour wifi-soc --board brd4338a
#   ./slc/script/build_selected_apps.sh --flavour wifi-soc --board brd4338a --apps lock_app
#   ./slc/script/build_selected_apps.sh --flavour wifi --board brd4338a --apps lock_app,lighting_app
#   ./slc/script/build_selected_apps.sh --flavour wifi --board brd4338a --exclude lock_app,oven_app
#   ./slc/script/build_selected_apps.sh --flavour thread-soc --board brd4187c --list
#   ./slc/script/build_selected_apps.sh --flavour all --board brd4338a --sqa
#
# Always continues after a failed app and prints a full success/failure report.
#
# Flavours:
#   wifi-soc     Wi-Fi SoC .slcp only
#   wifi-ncp     Wi-Fi 917 NCP .slcp only
#   thread-soc   Thread SoC .slcp only (skips trustzone by default)
#   wifi         wifi-soc + wifi-ncp
#   all          wifi-soc + wifi-ncp + thread-soc
#
# App filters (directory names under slc/apps/, e.g. lock_app, thermostat):
#   --apps / -a      build only these apps within the flavour (comma-separated)
#   --exclude / -e   skip these apps within the flavour (comma-separated)
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_SH="$REPO_ROOT/slc/build.sh"
APPS_ROOT="$REPO_ROOT/slc/apps"

FLAVOUR=""
BOARD=""
APPS_CSV=""
EXCLUDE_CSV=""
INCLUDE_TRUSTZONE=0
LIST_ONLY=0
DRY_RUN=0
BUILD_EXTRA=()

usage() {
  sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

csv_has() {
  local needle="$1"
  local csv="$2"
  local IFS=','
  local item
  for item in $csv; do
    item="${item// /}"
    [[ -z "$item" ]] && continue
    [[ "$needle" == "$item" ]] && return 0
  done
  return 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --flavour|-f) FLAVOUR="${2:-}"; shift 2 ;;
    --board|-b) BOARD="${2:-}"; shift 2 ;;
    --apps|-a) APPS_CSV="${2:-}"; shift 2 ;;
    --exclude|-e) EXCLUDE_CSV="${2:-}"; shift 2 ;;
    --include-trustzone) INCLUDE_TRUSTZONE=1; shift ;;
    --list|-l) LIST_ONLY=1; shift ;;
    --continue|-c) shift ;; # legacy no-op; always continues on failure
    --dry-run|-n) DRY_RUN=1; shift ;;
    --help|-h) usage 0 ;;
    --sqa|--dev|--col|--skip_gen)
      BUILD_EXTRA+=("$1"); shift ;;
    --*)
      # Pass unknown flags through to build.sh (and its value if present)
      BUILD_EXTRA+=("$1")
      if [[ $# -ge 2 && "${2:-}" != -* ]]; then
        BUILD_EXTRA+=("$2"); shift 2
      else
        shift
      fi
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage 1
      ;;
  esac
done

[[ -n "$FLAVOUR" ]] || { echo "ERROR: --flavour is required" >&2; usage 1; }
[[ -n "$BOARD" || "$LIST_ONLY" -eq 1 ]] || { echo "ERROR: --board is required (unless --list)" >&2; usage 1; }
[[ -f "$BUILD_SH" ]] || { echo "ERROR: missing $BUILD_SH" >&2; exit 1; }

# app dir name from path: slc/apps/<app>/...
app_name_of() {
  local rel="$1"
  echo "$rel" | awk -F/ '{print $3}'
}

is_excluded() {
  [[ -n "$EXCLUDE_CSV" ]] && csv_has "$1" "$EXCLUDE_CSV"
}

is_requested_app() {
  # Empty --apps means all apps in the flavour.
  [[ -z "$APPS_CSV" ]] && return 0
  csv_has "$1" "$APPS_CSV"
}

collect_wifi_soc() {
  find "$APPS_ROOT" -type f -path '*/wifi/matter_wifi_soc_*_freertos.slcp' | sort
}

collect_wifi_ncp() {
  find "$APPS_ROOT" -type f -path '*/wifi/matter_wifi_917_ncp_*_freertos.slcp' | sort
}

collect_thread_soc() {
  local files
  files="$(find "$APPS_ROOT" -type f -path '*/thread/matter_thread_soc_*_freertos.slcp' | sort)"
  if [[ "$INCLUDE_TRUSTZONE" -eq 0 ]]; then
    echo "$files" | grep -v '/trustzone/' || true
  else
    echo "$files"
  fi
}

SLCPS=()
case "$FLAVOUR" in
  wifi-soc) mapfile -t SLCPS < <(collect_wifi_soc) ;;
  wifi-ncp) mapfile -t SLCPS < <(collect_wifi_ncp) ;;
  thread-soc) mapfile -t SLCPS < <(collect_thread_soc) ;;
  wifi)
    mapfile -t SLCPS < <( { collect_wifi_soc; collect_wifi_ncp; } | sort -u )
    ;;
  all)
    mapfile -t SLCPS < <( { collect_wifi_soc; collect_wifi_ncp; collect_thread_soc; } | sort -u )
    ;;
  *)
    echo "ERROR: unknown flavour '$FLAVOUR' (wifi-soc|wifi-ncp|thread-soc|wifi|all)" >&2
    exit 1
    ;;
esac

SELECTED=()
SKIPPED=()
FOUND_APPS_CSV=""
for slcp in "${SLCPS[@]}"; do
  [[ -z "$slcp" ]] && continue
  rel="${slcp#"$REPO_ROOT"/}"
  app="$(app_name_of "$rel")"
  if ! is_requested_app "$app"; then
    continue
  fi
  if [[ -z "$FOUND_APPS_CSV" ]]; then
    FOUND_APPS_CSV="$app"
  elif ! csv_has "$app" "$FOUND_APPS_CSV"; then
    FOUND_APPS_CSV="$FOUND_APPS_CSV,$app"
  fi
  if is_excluded "$app"; then
    SKIPPED+=("$rel")
  else
    SELECTED+=("$rel")
  fi
done

if [[ -n "$APPS_CSV" ]]; then
  MISSING_APPS=()
  local_ifs="$IFS"
  IFS=','
  for req in $APPS_CSV; do
    req="${req// /}"
    [[ -z "$req" ]] && continue
    if ! csv_has "$req" "$FOUND_APPS_CSV"; then
      MISSING_APPS+=("$req")
    fi
  done
  IFS="$local_ifs"
  if [[ ${#MISSING_APPS[@]} -gt 0 ]]; then
    echo "ERROR: app(s) not found in flavour '$FLAVOUR': ${MISSING_APPS[*]}" >&2
    echo "Hint: use --list to see available projects for this flavour." >&2
    exit 1
  fi
fi

echo "Flavour: $FLAVOUR"
echo "Board:   ${BOARD:-(list only)}"
[[ -n "$APPS_CSV" ]] && echo "Apps:    $APPS_CSV"
echo "Selected (${#SELECTED[@]}):"
printf '  %s\n' "${SELECTED[@]}"
if [[ ${#SKIPPED[@]} -gt 0 ]]; then
  echo "Excluded (${#SKIPPED[@]}):"
  printf '  %s\n' "${SKIPPED[@]}"
fi

[[ "$LIST_ONLY" -eq 1 ]] && exit 0
[[ ${#SELECTED[@]} -gt 0 ]] || { echo "Nothing to build."; exit 0; }

if [[ -f "$REPO_ROOT/slc/tools/.env" ]]; then
  # shellcheck disable=SC1091
  source "$REPO_ROOT/slc/tools/.env"
fi

FAILED=()
PASSED=()
cd "$REPO_ROOT"

for rel in "${SELECTED[@]}"; do
  echo
  echo "===== Building $rel ($BOARD) ====="
  cmd=(./slc/build.sh "${BUILD_EXTRA[@]}" "$rel" "$BOARD")
  printf '+'
  printf ' %q' "${cmd[@]}"
  echo
  if [[ "$DRY_RUN" -eq 1 ]]; then
    PASSED+=("$rel")
    continue
  fi
  if "${cmd[@]}"; then
    PASSED+=("$rel")
  else
    FAILED+=("$rel")
    echo "WARN: build failed, continuing: $rel" >&2
  fi
done

echo
echo "========================================"
echo " Build report"
echo "========================================"
echo "Flavour:  $FLAVOUR"
echo "Board:    $BOARD"
echo "Selected: ${#SELECTED[@]}"
echo "Passed:   ${#PASSED[@]}"
echo "Failed:   ${#FAILED[@]}"
echo "Skipped:  ${#SKIPPED[@]} (excluded)"
echo

if [[ ${#PASSED[@]} -gt 0 ]]; then
  echo "SUCCESS (${#PASSED[@]}):"
  printf '  PASS  %s\n' "${PASSED[@]}"
  echo
fi

if [[ ${#FAILED[@]} -gt 0 ]]; then
  echo "FAILURE (${#FAILED[@]}):"
  printf '  FAIL  %s\n' "${FAILED[@]}"
  echo
fi

if [[ ${#SKIPPED[@]} -gt 0 ]]; then
  echo "EXCLUDED (${#SKIPPED[@]}):"
  printf '  SKIP  %s\n' "${SKIPPED[@]}"
  echo
fi

echo "========================================"
if [[ ${#FAILED[@]} -gt 0 ]]; then
  echo "Result: FAILED"
  exit 1
fi
echo "Result: SUCCESS"
