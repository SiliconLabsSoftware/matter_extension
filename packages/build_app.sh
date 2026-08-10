#!/usr/bin/env bash
# Build a Matter sample from installed Conan/SLT packages (matter + matter_app).
#
# Independent of a git checkout: no --export and no submodule updates.
# Installs SLT tools (conan, slc-cli, zap) and OS packages (make, find) as needed.
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
#                            or 2.10.0)
#   -j N                     make -jN (default: 8)
#   -h, --help               Show this help
#
# Prerequisites: `slt` on PATH. Uses SLT Conan engine (~/.silabs/slt/engines/conan).

set -euo pipefail

VERSION_DEFAULT="2.10.0"
MATTER_PACKAGE_VERSION="${MATTER_PACKAGE_VERSION:-${VERSION_DEFAULT}}"
SLCP=""
BOARD=""
JOBS=8

# Print the header comment block as help text, then exit (arg: exit code).
usage() {
  sed -n '2,21p' "$0" | sed 's/^# \?//'
  exit "${1:-0}"
}

# Print an error to stderr and exit with status 1.
die() {
  echo "error: $*" >&2
  exit 1
}

# Abort if the named command is not on PATH.
need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
}

# Install an OS package when the command is missing (apt-based systems).
# Args: command name, optional apt package name (defaults to command name).
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

SLT_HOME="${SLT_HOME:-${HOME}/.silabs/slt}"
CONAN="${SLT_HOME}/engines/conan/conan/conan"
export CONAN_HOME="${CONAN_HOME:-${SLT_HOME}/installs/conan}"

echo "Installing SLT tools (conan, slc-cli, zap)..."
slt install conan
# Matter slt_requirements use package id "slc-cli" (6.0.23+), not legacy "slc_cli" (6.0.9).
slt install slc-cli
slt install zap
[[ -x "${CONAN}" ]] || die "SLT Conan missing after install: ${CONAN}"
echo "Using CONAN=${CONAN}"
echo "CONAN_HOME=${CONAN_HOME}"

# Put a usable `slc` on PATH from SLT installs.
# Prefers package id "slc-cli" (Matter / 6.0.23+) over legacy "slc_cli" / "slc_cli_base" (6.0.9).
# Falls back to scanning SLT archive installs if `slt where` does not resolve.
ensure_slc_on_path() {
  local cand dir
  for cand in \
    "$(slt where slc-cli 2>/dev/null || true)" \
    "$(slt where slc_cli 2>/dev/null || true)" \
    "$(slt where slc_cli_base 2>/dev/null || true)"; do
    [[ -n "${cand}" ]] || continue
    for dir in "${cand}" "${cand}/slc_cli" "${cand}/bin"; do
      if [[ -x "${dir}/slc" ]]; then
        export PATH="${dir}:${PATH}"
        echo "Using slc from ${dir} ($("${dir}/slc" -version 2>/dev/null || echo unknown))"
        return 0
      fi
    done
  done

  # Fallback: prefer archive installs named slc-cli-* (newer) over slc_cli_*
  cand="$(find "${SLT_HOME}/installs/archive" -type f -path '*/slc-cli-*/slc_cli/slc' -executable 2>/dev/null | sort -r | head -n1 || true)"
  if [[ -z "${cand}" ]]; then
    cand="$(find "${SLT_HOME}/installs/archive" -type f -name slc -executable 2>/dev/null | sort -r | head -n1 || true)"
  fi
  if [[ -n "${cand}" ]]; then
    dir="$(dirname "${cand}")"
    export PATH="${dir}:${PATH}"
    echo "Using slc from ${dir} ($("${dir}/slc" -version 2>/dev/null || echo unknown))"
    return 0
  fi

  return 1
}


echo "Ensuring OS build tools (make, find)..."
ensure_os_cmd make make
ensure_os_cmd find findutils

ensure_slc_on_path || die "slc not found after slt install slc-cli"

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

print_pkg_meta_version() {
  local root="$1"
  local label="$2"
  local meta="${root}/../d/metadata/package_metadata.yaml"
  local ver=""
  if [[ -f "${meta}" ]]; then
    ver="$(sed -n 's/^version:[[:space:]]*//p' "${meta}" | head -n1)"
  fi
  echo "${label} package version=${ver:-unknown}"
}

print_pkg_meta_version "${MATTER_APP}" "matter_app"
print_pkg_meta_version "${MATTER}" "matter"

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
