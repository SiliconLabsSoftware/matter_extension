#!/usr/bin/env bash
# Re-export local matter/matter_app Conan packages and reinstall via SLT.
#
# Usage:
#   ./slc/script/refresh_local_packages.sh
#   ./slc/script/refresh_local_packages.sh slc/apps/lock_app/thread/pkg.slt

set -euo pipefail

MATTER_ROOT="${MATTER_ROOT:-$(pwd -P)}"
cd "$MATTER_ROOT"

if [ -f "$MATTER_ROOT/slc/tools/.env" ]; then
	set -a
	# shellcheck source=/dev/null
	. "$MATTER_ROOT/slc/tools/.env"
	set +a
fi

export MATTER_SDK_SOURCE_ROOT="${MATTER_SDK_SOURCE_ROOT:-$(python3 -c "
import sys
sys.path.insert(0, 'slc')
from pathlib import Path
from script.stack_tooling import default_matter_sdk_source_root
print(default_matter_sdk_source_root(Path('.').resolve()))
")}"

SLT_EXE="${SLT_EXE:-$MATTER_ROOT/slc/tools/slt}"
if [ ! -x "$SLT_EXE" ]; then
	SLT_EXE=$(command -v slt)
fi

python3 slc/script/generate_pkg_slt.py -d slc

MATTER_VERSION=$(python3 slc/script/generate_pkg_slt.py --version-only)
CONAN_EXE="${CONAN_EXE:-$(python3 -c "
import sys
sys.path.insert(0, 'slc')
from script.stack_tooling import resolve_conan_exe
print(resolve_conan_exe())
")}"

export CONAN_HOME="${CONAN_HOME:-$HOME/.silabs/slt/installs/conan}"
export MATTER_PACKAGE_VERSION="$MATTER_VERSION"

echo "Exporting matter/${MATTER_VERSION}, matter_app/${MATTER_VERSION}..."
python3 -c "
import sys
sys.path.insert(0, 'slc')
from pathlib import Path
from script.stack_tooling import export_local_packages
export_local_packages(Path('$MATTER_ROOT'), version='$MATTER_VERSION')
"

echo "Installing matter stack from packages/matter/pkg.slt..."
"$SLT_EXE" install -f packages/matter/pkg.slt --non-interactive

if [ $# -gt 0 ]; then
	for pkg_slt in "$@"; do
		echo "Installing from $pkg_slt..."
		"$SLT_EXE" install -f "$pkg_slt" --non-interactive
		app_dir="$(dirname "$pkg_slt")"
		slcp_name=""
		for slcp in "$app_dir"/*.slcp; do
			if [ -f "$slcp" ]; then
				slcp_name="$(basename "$slcp")"
				break
			fi
		done
		echo "Writing filtered slc-sdk.slconf for $app_dir..."
		if [ -n "$slcp_name" ]; then
			python3 slc/script/write_app_slconf.py --app-dir "$app_dir" --slcp-name "$slcp_name"
		else
			python3 slc/script/write_app_slconf.py --app-dir "$app_dir"
		fi
	done
else
	echo "Done. Re-install app deps with: slt install -f <path/to/pkg.slt>"
fi
