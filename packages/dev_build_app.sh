#!/usr/bin/env bash
# Develop Matter apps from Conan/SLT packages (matter + matter_app).
#
# Default: install/use a specific package version, generate, and build.
# Export runs only with --export.
#   --export without --slcp/--board  -> export packages only
#   --export with --slcp/--board     -> export, then generate and build
#
# Usage:
#   ./packages/dev_build_app.sh --slcp matter_wifi_soc_lighting_app_freertos.slcp --board brd4338a
#   ./packages/dev_build_app.sh --slcp <name>.slcp --board <board> --version 2.10.0-alpha.8
#   ./packages/dev_build_app.sh --slcp <name>.slcp --board <board> --version 2.10.0-alpha.8 --export
#   ./packages/dev_build_app.sh --export --version 2.10.0-alpha.8 --clean
#   ./packages/dev_build_app.sh --slcp ... --board ... --update-submodules
#
# Options:
#   --slcp NAME              Sample .slcp basename (required to generate/build)
#   --board BOARD            Board id, e.g. brd4338a (required to generate/build)
#   --version VER            Package version to use/export (default: env MATTER_PACKAGE_VERSION
#                            or 2.10.0-0.dev)
#   --export                 SLT conan export-pkg matter + matter_app. Without --slcp/--board,
#                            stops after export/install. With them, continues to generate/build.
#   --clean                  Remove local matter/matter_app Conan packages (only with --export)
#   --update-submodules      git submodule update --init for matter_sdk, nlio, nlassert, QR-Code-generator
#   -j N                     make -jN (default: 8)
#   -h, --help               Show this help
#
# Uses SLT Conan engine (~/.silabs/slt/engines/conan), not a system/pip conan.
# Loads slc/tools/.env from sl_setup_env (slc, arm gcc, java, etc.) and prefers
# repo-local slt from slc/tools when present.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

VERSION_DEFAULT="2.10.0-0.dev"
MATTER_PACKAGE_VERSION="${MATTER_PACKAGE_VERSION:-${VERSION_DEFAULT}}"
SLCP=""
BOARD=""
DO_EXPORT=0
CLEAN=0
UPDATE_SUBMODULES=0
JOBS=8

usage() {
  sed -n '2,31p' "$0" | sed 's/^# \?//'
  exit "${1:-0}"
}

die() {
  echo "error: $*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "required command not found: $1"
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
    --export)
      DO_EXPORT=1
      shift
      ;;
    --clean)
      CLEAN=1
      shift
      ;;
    --update-submodules)
      UPDATE_SUBMODULES=1
      shift
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

# Export-only: --export and neither app arg. Build: both --slcp and --board.
EXPORT_ONLY=0
if [[ -z "${SLCP}" && -z "${BOARD}" ]]; then
  [[ "${DO_EXPORT}" -eq 1 ]] || die "need --slcp and --board to build, or --export to export packages"
  EXPORT_ONLY=1
elif [[ -z "${SLCP}" || -z "${BOARD}" ]]; then
  die "need both --slcp and --board (or omit both and pass --export)"
else
  [[ "${SLCP}" == *.slcp ]] || SLCP="${SLCP}.slcp"
fi

if [[ "${CLEAN}" -eq 1 && "${DO_EXPORT}" -eq 0 ]]; then
  die "--clean only applies with --export"
fi

export MATTER_PACKAGE_VERSION
REF="matter_app/${MATTER_PACKAGE_VERSION}@silabs"
echo "MATTER_PACKAGE_VERSION=${MATTER_PACKAGE_VERSION}"

ENV_FILE="${ROOT}/slc/tools/.env"
if [[ -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
  if [[ -n "${TOOLS_PATH:-}" ]]; then
    export PATH="${TOOLS_PATH}:${PATH}"
  fi
else
  echo "warning: missing ${ENV_FILE} (run: python3 slc/sl_setup_env.py)" >&2
fi

# Prefer repo-local slt from sl_setup_env over anything in TOOLS_PATH
if [[ -x "${ROOT}/slc/tools/slt" ]]; then
  export PATH="${ROOT}/slc/tools:${PATH}"
fi

need_cmd slt
if [[ "${EXPORT_ONLY}" -eq 0 ]]; then
  need_cmd slc
  need_cmd make
  need_cmd find
fi

SLT_HOME="${SLT_HOME:-${HOME}/.silabs/slt}"
CONAN="${SLT_HOME}/engines/conan/conan/conan"
export CONAN_HOME="${CONAN_HOME:-${SLT_HOME}/installs/conan}"

echo "Ensuring SLT Conan engine..."
slt install conan
[[ -x "${CONAN}" ]] || die "SLT Conan missing after install: ${CONAN}"
echo "Using CONAN=${CONAN}"
echo "CONAN_HOME=${CONAN_HOME}"

if [[ "${UPDATE_SUBMODULES}" -eq 1 ]]; then
  echo "Updating submodules..."
  git submodule update --init --recursive \
    third_party/matter_sdk \
    third_party/nlio \
    third_party/nlassert \
    third_party/QR-Code-generator
fi

if [[ "${DO_EXPORT}" -eq 1 ]]; then
  if [[ "${CLEAN}" -eq 1 ]]; then
    echo "Removing local matter / matter_app Conan packages..."
    "${CONAN}" remove "matter/*@silabs" -c || true
    "${CONAN}" remove "matter_app/*@silabs" -c || true
  fi

  echo "Exporting matter/${MATTER_PACKAGE_VERSION}@silabs ..."
  "${CONAN}" export-pkg packages/matter/conanfile.py \
    --name=matter \
    --version="${MATTER_PACKAGE_VERSION}" \
    --user=silabs

  echo "Exporting matter_app/${MATTER_PACKAGE_VERSION}@silabs ..."
  "${CONAN}" export-pkg packages/matter_app/conanfile.py \
    --name=matter_app \
    --version="${MATTER_PACKAGE_VERSION}" \
    --user=silabs
fi

echo "Installing ${REF} via SLT..."
slt install "${REF}" -e conan

MATTER_APP="$(slt where matter_app)"
MATTER="$(slt where matter)"
[[ -n "${MATTER_APP}" ]] || die "slt where matter_app returned empty"
[[ -n "${MATTER}" ]] || die "slt where matter returned empty"
echo "MATTER_APP=${MATTER_APP}"
echo "MATTER=${MATTER}"

# Helpful checks for Matter ZAP / sample-app SDK markers
for f in matter.slsdk src/app/zap-templates/app-templates.json; do
  if [[ ! -f "${MATTER}/${f}" ]]; then
    echo "warning: missing in matter package: ${f}" >&2
  fi
done
if [[ ! -f "${MATTER_APP}/matter_app.slsdk" ]]; then
  echo "warning: missing matter_app.slsdk in matter_app package" >&2
fi

if [[ "${EXPORT_ONLY}" -eq 1 ]]; then
  echo "Export done."
  exit 0
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
