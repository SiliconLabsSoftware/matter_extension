#!/usr/bin/env bash
# DEPRECATED — use slc/build.sh (see docs/PACKAGE_MANAGER_DEVELOPER_GUIDE.md).
#
# Thin compatibility wrapper. Old flags are translated and execution is delegated:
#   --export                          -> slc/build.sh --create-package-version
#   --export --slcp X --board Y       -> slc/build.sh --build-from-package-version
#   --slcp X --board Y (no --export)   -> packages/build_app.sh
#
#   --update-submodules               -> git submodule update (then delegate as above)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

VERSION_DEFAULT="2.10.0-0.dev"
MATTER_PACKAGE_VERSION="${MATTER_PACKAGE_VERSION:-${VERSION_DEFAULT}}"
SLCP=""
BOARD=""
DO_EXPORT=0
CLEAN=0
UPDATE_SUBMODULES=0
JOBS=8

warn_deprecated() {
	echo "warning: packages/dev_build_app.sh is deprecated and will be removed in a future release." >&2
	echo "warning: Use slc/build.sh instead (see docs/PACKAGE_MANAGER_DEVELOPER_GUIDE.md)." >&2
}

usage() {
	warn_deprecated
	cat >&2 <<'EOF'
Migrate to:

  Export packages:
    ./slc/build.sh --create-package-version VER [--clean]

  Export and build (package path):
    ./slc/build.sh --build-from-package-version VER <project.slcp|slcw> <board> [--clean]

  Build from already-installed matter_app (no export):
    ./packages/build_app.sh <project> <board> --version VER

EOF
	exit "${1:-0}"
}

die() {
	echo "error: $*" >&2
	exit 1
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
		die "unknown argument: $1 (run with --help)"
		;;
	esac
done

warn_deprecated

if [[ -z "${SLCP}" && -z "${BOARD}" ]]; then
	[[ "${DO_EXPORT}" -eq 1 ]] || die "need --slcp and --board to build, or --export to export packages"
elif [[ -z "${SLCP}" || -z "${BOARD}" ]]; then
	die "need both --slcp and --board (or omit both and pass --export)"
fi

if [[ "${CLEAN}" -eq 1 && "${DO_EXPORT}" -eq 0 ]]; then
	die "--clean only applies with --export (use slc/build.sh --create-package-version VER --clean)"
fi

if [[ "${UPDATE_SUBMODULES}" -eq 1 ]]; then
	echo "Updating submodules..."
	git -C "${ROOT}" submodule update --init --recursive \
		third_party/matter_sdk \
		third_party/nlio \
		third_party/nlassert \
		third_party/QR-Code-generator
fi

export MATTER_PACKAGE_VERSION

if [[ "${DO_EXPORT}" -eq 1 ]]; then
	args=(--build-from-package-version "${MATTER_PACKAGE_VERSION}")
	if [[ -z "${SLCP}" ]]; then
		args=(--create-package-version "${MATTER_PACKAGE_VERSION}")
	fi
	[[ "${CLEAN}" -eq 1 ]] && args+=(--clean)
	if [[ -n "${SLCP}" ]]; then
		args+=("${SLCP}" "${BOARD}")
	fi
	exec "${ROOT}/slc/build.sh" "${args[@]}"
fi

args=("${SLCP}" "${BOARD}" --version "${MATTER_PACKAGE_VERSION}")
if [[ "${JOBS}" != "8" ]]; then
	args+=(-j "${JOBS}")
fi
exec "${ROOT}/packages/build_app.sh" "${args[@]}"
