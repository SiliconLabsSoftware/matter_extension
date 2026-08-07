#!/usr/bin/env bash
# Build a Matter sample from installed Conan/SLT packages (matter + matter_app).
#
# Independent of a git checkout: no --export and no submodule updates.
# Installs SLT tools (conan, slc_cli, zap) and OS packages (make, find) as needed.
#
# Usage:
#   ./packages/build_app.sh --slcp matter_wifi_soc_lighting_app_freertos.slcp --board brd4338a
#   ./packages/build_app.sh --slcp <name>.slcp --board <board> --version 2.10.0-alpha.8
#   "$(slt where matter_app)/build_app.sh" --slcp <name>.slcp --board <board>
#
# Options:
#   --slcp NAME              Sample .slcp basename (required)
#   --board BOARD            Board id, e.g. brd4338a (required)
#   --version VER            matter_app version to install (default: env MATTER_PACKAGE_VERSION
#                            or 2.10.0-0.dev)
#   -j N                     make -jN (default: 8)
#   -h, --help               Show this help
#
# Prerequisites: `slt` on PATH. Uses SLT Conan engine (~/.silabs/slt/engines/conan).

set -euo pipefail

VERSION_DEFAULT="2.10.0-0.dev"
MATTER_PACKAGE_VERSION="${MATTER_PACKAGE_VERSION:-${VERSION_DEFAULT}}"
SLCP=""
BOARD=""
JOBS=8

usage() {
  sed -n '2,21p' "$0" | sed 's/^# \?//'
  exit "${1:-0}"
}

die() {
  echo "error: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

# Install an OS package when the command is missing (apt-based systems).
ensure_os_cmd() {
  local cmd="$1"
  local pkg="${2:-$1}"
  if command -v "${cmd}" >/dev/null 2>&1; then
    return 0
  fi
  if command -v apt-get >/dev/null 2>&1; then
    echo "Installing OS package: ${pkg} (provides ${cmd})"
    if [[ "$(id -u)" -eq 0 ]]; then
      apt-get update -qq
      apt-get install -y "${pkg}"
    else
      need_cmd sudo
      sudo apt-get update -qq
      sudo apt-get install -y "${pkg}"
    fi
  else
    die "required command not found: ${cmd} (install package '${pkg}')"
  fi
  need_cmd "${cmd}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --slcp)
      SLCP="${2:-}"
      [[ -n "${SLCP}" ]] || die "--slcp needs a value"
      shift 2
      ;;
    --board)
      BOARD="${2:-}"
      [[ -n "${BOARD}" ]] || die "--board needs a value"
      shift 2
      ;;
    --version)
      MATTER_PACKAGE_VERSION="${2:-}"
      [[ -n "${MATTER_PACKAGE_VERSION}" ]] || die "--version needs a value"
      shift 2
      ;;
    -j)
      JOBS="${2:-}"
      [[ -n "${JOBS}" ]] || die "-j needs a value"
      shift 2
      ;;
    -h | --help)
      usage 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage 1
      ;;
  esac
done

[[ -n "${SLCP}" && -n "${BOARD}" ]] || die "need both --slcp and --board"
[[ "${SLCP}" == *.slcp ]] || SLCP="${SLCP}.slcp"

export MATTER_PACKAGE_VERSION
REF="matter_app/${MATTER_PACKAGE_VERSION}@silabs"
echo "MATTER_PACKAGE_VERSION=${MATTER_PACKAGE_VERSION}"

need_cmd slt

# Optional: load tools from a checkout when run as packages/build_app.sh in the repo.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECKOUT_ROOT=""
if [[ -f "${SCRIPT_DIR}/../matter.slce" || -d "${SCRIPT_DIR}/../slc/apps" ]]; then
  # Running from repo: packages/build_app.sh
  CHECKOUT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
elif [[ -f "${SCRIPT_DIR}/matter.slce" ]]; then
  CHECKOUT_ROOT="${SCRIPT_DIR}"
fi
if [[ -n "${CHECKOUT_ROOT}" ]]; then
  ENV_FILE="${CHECKOUT_ROOT}/slc/tools/.env"
  if [[ -f "${ENV_FILE}" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "${ENV_FILE}"
    set +a
    if [[ -n "${TOOLS_PATH:-}" ]]; then
      export PATH="${TOOLS_PATH}:${PATH}"
    fi
  fi
  if [[ -x "${CHECKOUT_ROOT}/slc/tools/slt" ]]; then
    export PATH="${CHECKOUT_ROOT}/slc/tools:${PATH}"
  fi
fi

SLT_HOME="${SLT_HOME:-${HOME}/.silabs/slt}"
CONAN="${SLT_HOME}/engines/conan/conan/conan"
export CONAN_HOME="${CONAN_HOME:-${SLT_HOME}/installs/conan}"

echo "Installing SLT tools (conan, slc_cli, zap)..."
slt install conan
slt install slc_cli
slt install zap
[[ -x "${CONAN}" ]] || die "SLT Conan missing after install: ${CONAN}"
echo "Using CONAN=${CONAN}"
echo "CONAN_HOME=${CONAN_HOME}"

# SLT does not always put `slc` on PATH in this shell. The executable lives under
# the slc_cli_base package (…/slc_cli/slc), not always at `slt where slc_cli`.
ensure_slc_on_path() {
  if command -v slc >/dev/null 2>&1; then
    return 0
  fi

  local cand dir
  for cand in \
    "$(slt where slc_cli_base 2>/dev/null || true)" \
    "$(slt where slc_cli 2>/dev/null || true)"; do
    [[ -n "${cand}" ]] || continue
    for dir in "${cand}" "${cand}/slc_cli" "${cand}/bin"; do
      if [[ -x "${dir}/slc" ]]; then
        export PATH="${dir}:${PATH}"
        echo "Using slc from ${dir}"
        return 0
      fi
    done
  done

  # Fallback: newest archive install that contains an executable named slc
  cand="$(find "${SLT_HOME}/installs/archive" -type f -name slc -executable 2>/dev/null | sort -r | head -n1 || true)"
  if [[ -n "${cand}" ]]; then
    dir="$(dirname "${cand}")"
    export PATH="${dir}:${PATH}"
    echo "Using slc from ${dir}"
    return 0
  fi

  return 1
}

ensure_slc_on_path || die "slc not found after slt install slc_cli (check slc_cli_base install)"

echo "Ensuring OS build tools (make, find)..."
ensure_os_cmd make make
ensure_os_cmd find findutils

need_cmd slc
need_cmd make
need_cmd find

echo "Installing ${REF} via SLT..."
slt install "${REF}" -e conan

MATTER_APP="$(slt where matter_app)"
MATTER="$(slt where matter)"
[[ -n "${MATTER_APP}" ]] || die "slt where matter_app returned empty"
[[ -n "${MATTER}" ]] || die "slt where matter returned empty"
echo "MATTER_APP=${MATTER_APP}"
echo "MATTER=${MATTER}"

for f in matter.slsdk src/app/zap-templates/app-templates.json; do
  if [[ ! -f "${MATTER}/${f}" ]]; then
    echo "warning: missing in matter package: ${f}" >&2
  fi
done
if [[ ! -f "${MATTER_APP}/matter_app.slsdk" ]]; then
  echo "warning: missing matter_app.slsdk in matter_app package" >&2
fi

SLCP_PATH="$(find "${MATTER_APP}" -type f -name "${SLCP}" 2>/dev/null | head -n1 || true)"
[[ -n "${SLCP_PATH}" ]] || die "could not find ${SLCP} under ${MATTER_APP}"

APP_DIR="$(dirname "${SLCP_PATH}")"
SLCP_BASE="${SLCP%.slcp}"
OUT_DIR="out/${BOARD}/${SLCP_BASE}"

echo "App dir: ${APP_DIR}"
echo "Project: ${SLCP}  board: ${BOARD}  out: ${OUT_DIR}"

cd "${APP_DIR}"

echo "Running slt install (project pkg.slt / pkg.slconf)..."
slt install

echo "Running slc generate..."
slc generate \
  -d "${OUT_DIR}" \
  -p "${SLCP}" \
  --with "${BOARD}" \
  --generator-timeout=180 \
  -o makefile

MAKEFILE="${SLCP_BASE}.Makefile"
[[ -f "${OUT_DIR}/${MAKEFILE}" ]] || die "expected ${OUT_DIR}/${MAKEFILE} after generate"

echo "Building with make -j${JOBS}..."
make -C "${OUT_DIR}" -f "${MAKEFILE}" -j"${JOBS}"

echo "Done: ${APP_DIR}/${OUT_DIR}"
