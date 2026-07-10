#!/usr/bin/env bash
# Build a Matter sample app from SLT packages (slt install, slconf, slc generate, make).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR_ARG="${1:?Usage: $0 <app-dir> <project.slcp> <board> [out-dir]}"
SLCP="${2:?Usage: $0 <app-dir> <project.slcp> <board> [out-dir]}"
BOARD="${3:?Usage: $0 <app-dir> <project.slcp> <board> [out-dir]}"
OUT_DIR_ARG="${4:-}"

resolve_app_dir() {
  local arg="$1"
  if [[ "$arg" = /* ]]; then
    cd "$arg" && pwd
    return
  fi
  if [[ -d "$arg" ]]; then
    cd "$arg" && pwd
    return
  fi
  if [[ -d "${SCRIPT_DIR}/${arg}" ]]; then
    cd "${SCRIPT_DIR}/${arg}" && pwd
    return
  fi
  echo "ERROR: app directory not found: $arg" >&2
  exit 1
}

APP_DIR="$(resolve_app_dir "$APP_DIR_ARG")"

if [[ -z "$OUT_DIR_ARG" ]]; then
  OUT_DIR="${APP_DIR}/out"
elif [[ "$OUT_DIR_ARG" = /* ]]; then
  OUT_DIR="$OUT_DIR_ARG"
else
  OUT_DIR="${APP_DIR}/${OUT_DIR_ARG#./}"
fi

resolve_cli() {
  if [[ -n "${MATTER_APP_SLCONF:-}" && -x "${MATTER_APP_SLCONF}" ]]; then
    echo "${MATTER_APP_SLCONF}"
    return
  fi
  local matter_pkg
  matter_pkg="$(slt where matter 2>/dev/null || true)"
  if [[ -n "${matter_pkg}" && -x "${matter_pkg}/bin/matter-app-slconf" ]]; then
    echo "${matter_pkg}/bin/matter-app-slconf"
    return
  fi
  if command -v matter-app-slconf >/dev/null 2>&1; then
    command -v matter-app-slconf
    return
  fi
  echo "ERROR: matter-app-slconf not found (install matter package or set MATTER_APP_SLCONF)" >&2
  exit 1
}

CLI="$(resolve_cli)"
exec "${CLI}" build-app "${APP_DIR}" "${SLCP}" "${BOARD}" --out-dir "${OUT_DIR}"
