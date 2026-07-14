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

resolve_slt_exe() {
  if [[ -n "${SLT_EXE:-}" && -x "${SLT_EXE}" ]]; then
    echo "${SLT_EXE}"
    return
  fi
  if command -v slt >/dev/null 2>&1; then
    command -v slt
    return
  fi
  local loc="${HOME}/.silabs/slt/slt.location"
  if [[ -f "$loc" ]]; then
    local candidate
    candidate="$(tr -d '\r\n' < "$loc")"
    if [[ -n "$candidate" && -x "$candidate" ]]; then
      echo "$candidate"
      return
    fi
  fi
  echo "ERROR: slt not found. Install SLT CLI or set SLT_EXE." >&2
  echo "  e.g. export SLT_EXE=/path/to/slt" >&2
  exit 1
}

resolve_slc_exe() {
  if [[ -n "${SLC_EXECUTABLE:-}" && -x "${SLC_EXECUTABLE}" ]]; then
    echo "${SLC_EXECUTABLE}"
    return
  fi
  if command -v slc >/dev/null 2>&1; then
    command -v slc
    return
  fi
  echo "ERROR: slc (slc-cli) not found on PATH. Install slc-cli via SLT or set SLC_EXECUTABLE." >&2
  echo "  e.g. slt install slc-cli --non-interactive" >&2
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

SLT_EXE="$(resolve_slt_exe)"
SLC_EXE="$(resolve_slc_exe)"
export SLT_EXE
export SLC_EXECUTABLE="$SLC_EXE"
export PATH="$(dirname "$SLT_EXE"):$(dirname "$SLC_EXE"):$PATH"

resolve_cli() {
  if [[ -n "${MATTER_APP_SLCONF:-}" && -x "${MATTER_APP_SLCONF}" ]]; then
    echo "${MATTER_APP_SLCONF}"
    return
  fi
  local matter_pkg
  matter_pkg="$("$SLT_EXE" where matter 2>/dev/null || true)"
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
