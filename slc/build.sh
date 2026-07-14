#!/usr/bin/env bash

# This script generates and builds the SLC project for the given Matter application and board.
#
#   Usage:
#   ./slc/build.sh <slcp/slcw path> <board>
#
#   Example .slcp usage:
#   ./slc/build.sh slc/apps/lighting_app/thread/matter_thread_soc_lighting_app_freertos.slcp brd4187c
#       output in: out/brd4187c/matter_thread_soc_lighting_app_freertos/
#
#   Example .slcw usage:
#   ./slc/build.sh slc/apps/lighting_app/thread/matter_thread_soc_lighting_app_series_2_freertos.slcw brd4187c
#       output in: out/brd4187c/matter_thread_soc_lighting_app_series_2_freertos_solution/
#
#   Example --configuration option usage:
#   ./slc/build.sh slc/apps/lighting_app/thread/matter_thread_soc_lighting_app_freertos.slcp brd4187c --configuration CHIP_DEVICE_CONFIG_DEVICE_SOFTWARE_VERSION:20,CHIP_DEVICE_CONFIG_DEVICE_SOFTWARE_VERSION_STRING:\"1.0.0-1.0\"
#       output in: out/brd4187c/matter_thread_soc_lighting_app_freertos/
#
#   --skip_gen option : Allows to skip the slc gen step and only run the make command to rebuild modified files. slc gen normally regenerate your config, autogen, linker_options and makefile for your output folder.
#                       This option only works if the project has previously been generated
#   Example
#   ./slc/build.sh slc/apps/lighting_app/thread/matter_thread_soc_lighting_app_freertos.slcp brd4187c --skip_gen
#       output in: out/brd4187c/matter_thread_soc_lighting_app_freertos/
#
#   --sisdk option : Allows to build a project using a different SISDK folder, at the provided path, rather than the default one found in third_party/simplicity_sdk
#   Example
#   ./slc/build.sh slc/apps/lighting_app/thread/matter_thread_soc_lighting_app_freertos.slcp brd4187c --sisdk /Users/Shared/silabs/Github/sisdk
#       output in: out/brd4187c/matter_thread_soc_lighting_app_freertos/
#
#   --with_app option : Allows to specify additional components for the application build for solutions only. If provided for .slcp file, silently ignored.
#   Example
#   ./slc/build.sh slc/apps/lighting_app/thread/matter_thread_soc_lighting_app_freertos.slcp brd4187c --with_app '<component1>,<component2>'
#       output in: out/brd4187c/matter_thread_soc_lighting_app_freertos/
#
#   --without_app option : Allows to exclude specific components from the application build for solutions only. If provided for .slcp file, silently ignored.
#   Example
#   ./slc/build.sh slc/apps/lighting_app/thread/matter_thread_soc_lighting_app_freertos.slcp brd4187c --without_app '<component1>,<component2>'
#       output in: out/brd4187c/matter_thread_soc_lighting_app_freertos/
#
#   --with_bootloader option : Allows to specify additional components for the bootloader build for solutions only. If provided for .slcp file, silently ignored.
#   Example
#   ./slc/build.sh slc/apps/thermostat/wifi/matter_wifi_917_ncp_thermostat_freertos.slcw brd4187c --with_bootloader '<component1>,<component2>'
#       output in: out/brd4187c/matter_wifi_917_ncp_thermostat_freertos_solution/
#
#   --without_bootloader option : Allows to exclude specific components from the bootloader build for solutions only. If provided for .slcp file, silently ignored.
#   Example
#   ./slc/build.sh slc/apps/thermostat/wifi/matter_wifi_917_ncp_thermostat_freertos.slcw brd4187c --without_bootloader '<component1>,<component2>'
#       output in: out/brd4187c/matter_wifi_917_ncp_thermostat_freertos_solution/
#
#   -pids option : Allows to build only specific parts of a solution (.slcw) project. If provided for .slcp file, silently ignored.
#   Valid arguments: 'bootloader' or 'application'
#   Example bootloader-only build:
#   ./slc/build.sh slc/apps/lighting_app/thread/matter_thread_soc_lighting_app_series_2_freertos.slcw brd4187c -pids bootloader
#       output in: out/brd4187c/matter_thread_soc_lighting_app_series_2_freertos_solution/ (builds only bootloader)
#   Example application-only build:
#   ./slc/build.sh slc/apps/lighting_app/thread/matter_thread_soc_lighting_app_series_2_freertos.slcw brd4187c -pids application
#       output in: out/brd4187c/matter_thread_soc_lighting_app_series_2_freertos_solution/ (builds only application)
#
#   --from-package : Dev workflow — git clone + installed SLT packages (uses write_app_slconf.py).
#   --package-only : Customer workflow — no git clone; uses matter/matter_app SLT packages only.
#   Example package-only:
#   cd "$(slt where matter)"
#   ./slc/build.sh --package-only slc/apps/lock_app/wifi/matter_wifi_soc_lock_app_freertos.slcp brd4338a
#       output in: <matter_app>/slc/apps/lock_app/wifi/out/brd4338a/matter_wifi_soc_lock_app_freertos/
#

# Helper functions to build component arguments
build_with_arg() {
	local board="$1"
	local components="$2"

	if [ -n "$components" ]; then
		echo "--with $board,$components"
	else
		echo "--with $board"
	fi
}

build_without_arg() {
	local components="$1"

	if [ -n "$components" ]; then
		echo "--without $components"
	else
		echo ""
	fi
}

resolve_slt_exe() {
	local matter_root="$1"
	if [ -n "${SLT_EXE:-}" ] && [ -x "$SLT_EXE" ]; then
		echo "$SLT_EXE"
		return 0
	fi
	if [ -n "$matter_root" ] && [ -x "$matter_root/slc/tools/slt" ]; then
		echo "$matter_root/slc/tools/slt"
		return 0
	fi
	if command -v slt >/dev/null 2>&1; then
		command -v slt
		return 0
	fi
	local loc="$HOME/.silabs/slt/slt.location"
	if [ -f "$loc" ]; then
		local candidate
		candidate="$(tr -d '\r\n' < "$loc")"
		if [ -n "$candidate" ] && [ -x "$candidate" ]; then
			echo "$candidate"
			return 0
		fi
	fi
	echo "ERROR: slt not found (set SLT_EXE or install SLT CLI)" >&2
	return 1
}

resolve_slc_exe() {
	if [ -n "${SLC_EXECUTABLE:-}" ] && [ -x "$SLC_EXECUTABLE" ]; then
		echo "$SLC_EXECUTABLE"
		return 0
	fi
	if command -v slc >/dev/null 2>&1; then
		command -v slc
		return 0
	fi
	echo "ERROR: slc (slc-cli) not found on PATH (install via SLT or set SLC_EXECUTABLE)" >&2
	return 1
}

resolve_slt_pkg_path() {
	local spec="$1"
	local raw path
	raw=$("$SLT_EXE" where --non-interactive "$spec" 2>/dev/null | tail -1)
	raw="${raw// /}"
	if [[ "$raw" == /* ]]; then
		path="$raw"
	elif [[ "$raw" == *'?'* ]]; then
		path=$(printf '%s' "$raw" | sed 's/.*?\s*//')
	else
		path="$raw"
	fi
	if [ -z "$path" ] || [ ! -d "$path" ]; then
		echo "ERROR: SLT package not installed: $spec" >&2
		return 1
	fi
	echo "$path"
}

write_app_slconf() {
	local app_dir="$1"
	local slcp_name="$2"

	if [ "$PACKAGE_ONLY" = true ]; then
		local cli="${MATTER_APP_SLCONF:-$MATTER_PKG/bin/matter-app-slconf}"
		if [ ! -x "$cli" ]; then
			echo "ERROR: matter-app-slconf not found at $cli" >&2
			return 1
		fi
		if [ ! -f "$app_dir/pkg.slt" ]; then
			echo "ERROR: pkg.slt not found in $app_dir" >&2
			return 1
		fi
		echo "Running: $SLT_EXE install -f $app_dir/pkg.slt --non-interactive"
		if ! "$SLT_EXE" install -f "$app_dir/pkg.slt" --non-interactive; then
			return 1
		fi
		echo "Running: $cli slconf --app-dir $app_dir --slcp-name $slcp_name"
		"$cli" slconf --app-dir "$app_dir" --slcp-name "$slcp_name"
		return $?
	fi

	if [ ! -f "$MATTER_ROOT/slc/script/write_app_slconf.py" ]; then
		echo "ERROR: write_app_slconf.py not found under $MATTER_ROOT/slc/script" >&2
		return 1
	fi
	python3 "$MATTER_ROOT/slc/script/write_app_slconf.py" \
		--app-dir "$app_dir" \
		--slcp-name "$slcp_name"
}

# Helper function to run slc generate with retry on timeout
run_slc_generate_with_retry() {
	local max_retries=3
	local attempt=1
	local exit_code=0
	local output=""

	while [ $attempt -le $max_retries ]; do
		echo "Running: slc $* (attempt $attempt/$max_retries)"
		output=$(slc "$@" 2>&1)
		exit_code=$?
		echo "$output"

		if [ $exit_code -eq 0 ]; then
			break
		fi

		# Check for ConcurrentModificationException
		if echo "$output" | grep -q "ConcurrentModificationException: Internal Error. Please see logs."; then
			echo "ConcurrentModificationException detected. Exporting logs..."
			slc --exportLogs=out/artifacts/log
			echo "Logs exported to out/artifacts/log"
			if [ $attempt -lt $max_retries ]; then
				echo "Retrying slc generate command after ConcurrentModificationException..."
				sleep 1
			else
				echo "Maximum retries reached after ConcurrentModificationException."
			fi
		# Check for timeout
		elif echo "$output" | grep -qi "Generation did not complete within .* seconds!"; then
			if [ $attempt -lt $max_retries ]; then
				echo "Timeout detected. Retrying slc generate command..."
				sleep 1
			else
				echo "Maximum retries reached after timeout."
			fi
		else
			echo "Attempt $attempt failed with exit code $exit_code (not a timeout or ConcurrentModificationException - no retry)"
			break
		fi

		attempt=$((attempt + 1))
	done
	return $exit_code
}

# Run slc generate; uses app user.slconf when USE_APP_SLCONF is set (no CLI sdk paths).
run_slc_generate_project() {
	local out_dir="$1"
	shift
	local project_file="$SILABS_APP_PATH"
	local -a pkg_paths=()
	if [ "${#PACKAGE_PATHS[@]}" -gt 0 ]; then
		pkg_paths=("${PACKAGE_PATHS[@]}")
	fi
	if [ "$USE_APP_SLCONF" = true ]; then
		out_dir="$OUTPUT_DIR_ABS"
		project_file="$SLC_PROJECT_FILE"
		pkg_paths=()
		echo "Using app slconf from $SLC_WORK_DIR (filtered sdk-package-path)"
		(
			cd "$SLC_WORK_DIR" || exit 1
			run_slc_generate_with_retry generate -d "$out_dir" "${pkg_paths[@]}" $PROJECT_FLAG "$project_file" "$@" $CONFIG_ARGS --generator-timeout=180 -o makefile
		)
		return $?
	fi
	run_slc_generate_with_retry generate -d "$out_dir" "${pkg_paths[@]}" $PROJECT_FLAG "$project_file" "$@" $CONFIG_ARGS --generator-timeout=180 -o makefile
}

MATTER_ROOT="${MATTER_ROOT:-$(pwd -P)}"
echo "MATTER_ROOT: $MATTER_ROOT"

FROM_PACKAGE=false
PACKAGE_ONLY=false
if [ "${MATTER_FROM_PACKAGE:-}" = "1" ] || [ "$1" = "--from-package" ]; then
	FROM_PACKAGE=true
	if [ "$1" = "--from-package" ]; then
		shift
	fi
fi
if [ "${MATTER_PACKAGE_ONLY:-}" = "1" ] || [ "$1" = "--package-only" ]; then
	PACKAGE_ONLY=true
	if [ "$1" = "--package-only" ]; then
		shift
	fi
fi
if [ "$FROM_PACKAGE" = true ] && [ "$PACKAGE_ONLY" = true ]; then
	echo "ERROR: --from-package and --package-only are mutually exclusive" >&2
	exit 1
fi

USE_SLT_PACKAGES=false
if [ "$FROM_PACKAGE" = true ] || [ "$PACKAGE_ONLY" = true ]; then
	USE_SLT_PACKAGES=true
fi

: "${SISDK_ROOT:=$MATTER_ROOT/third_party/simplicity_sdk}"

# include env variables from .env file generated by sl_setup_env.py
set -a
if [ -f "$MATTER_ROOT/slc/tools/.env" ]; then
	echo "Loading environment variables from $MATTER_ROOT/slc/tools/.env"
	. "$MATTER_ROOT/slc/tools/.env"
	PATH="$TOOLS_PATH:$PATH"
fi
set +a

if [ "$USE_SLT_PACKAGES" = true ]; then
	SLT_EXE="$(resolve_slt_exe "$MATTER_ROOT")" || exit 1
	export SLT_EXE
	if [ "$PACKAGE_ONLY" = true ]; then
		SLC_EXE="$(resolve_slc_exe)" || exit 1
		export SLC_EXECUTABLE="$SLC_EXE"
		export PATH="$(dirname "$SLT_EXE"):$(dirname "$SLC_EXE"):$PATH"
	fi
	MATTER_APP_PKG=$(resolve_slt_pkg_path "matter_app") || exit 1
	MATTER_PKG=$(resolve_slt_pkg_path "matter") || exit 1
	if [ ! -d "$MATTER_PKG/third_party/matter_sdk" ]; then
		echo "ERROR: matter package missing third_party/matter_sdk at $MATTER_PKG/third_party/matter_sdk" >&2
		exit 1
	fi
	if [ "$PACKAGE_ONLY" = true ]; then
		MATTER_ROOT="${MATTER_ROOT:-$MATTER_PKG}"
	fi
	EXTENSION_DIR="$MATTER_PKG"
	export silabs_chip_root="$MATTER_PKG"
	PACKAGE_PATHS=()
	USE_APP_SLCONF=false
	SLC_WORK_DIR=""
	SLC_PROJECT_FILE=""
else
	EXTENSION_DIR=$MATTER_ROOT
	PACKAGE_PATHS=(--sdk-package-path "$EXTENSION_DIR")
	USE_APP_SLCONF=false
	SLC_WORK_DIR=""
	SLC_PROJECT_FILE=""
	if [ -n "$STACK_SDK_PATHS" ]; then
		IFS=':' read -ra _stack_paths <<< "$STACK_SDK_PATHS"
		for _p in "${_stack_paths[@]}"; do
			PACKAGE_PATHS+=(--sdk-package-path "$_p")
		done
	elif [ -d "$SISDK_ROOT" ]; then
		PACKAGE_PATHS+=(--sdk-package-path "$SISDK_ROOT")
		if [ -n "$WISECONNECT_ROOT" ] && [ -d "$WISECONNECT_ROOT" ]; then
			PACKAGE_PATHS+=(--sdk-package-path "$WISECONNECT_ROOT")
		fi
	fi
fi

# Validate required arguments
if [ -z "$1" ] || [ -z "$2" ]; then
	echo "ERROR: Missing required arguments."
	echo "Usage: $0 <slcp/slcw path> <board> [options...]"
	exit 1
fi

SILABS_APP_PATH=$1
SILABS_BOARD=$2
ORIG_APP_ARG=$1
REPO_APP_DIR=""
if [[ "$ORIG_APP_ARG" != /* ]]; then
	REPO_APP_DIR="$MATTER_ROOT/$(dirname "$ORIG_APP_ARG")"
fi
if [ "$USE_SLT_PACKAGES" = true ]; then
	if [[ "$SILABS_APP_PATH" != /* ]]; then
		SILABS_APP_PATH="$MATTER_APP_PKG/$SILABS_APP_PATH"
	fi
	if [ ! -f "$SILABS_APP_PATH" ]; then
		echo "ERROR: Project file not found in matter_app package: $SILABS_APP_PATH" >&2
		exit 1
	fi
	if [ "$PACKAGE_ONLY" = true ]; then
		SLCONF_APP_DIR="$(dirname "$SILABS_APP_PATH")"
	else
		SLCONF_APP_DIR="$REPO_APP_DIR"
		if [ ! -f "$SLCONF_APP_DIR/autogen/pkg.slconf" ]; then
			SLCONF_APP_DIR="$(dirname "$SILABS_APP_PATH")"
		fi
	fi
	if [ ! -f "$SLCONF_APP_DIR/autogen/pkg.slconf" ]; then
		if [ "$PACKAGE_ONLY" = true ]; then
			echo "ERROR: missing autogen/pkg.slconf in $SLCONF_APP_DIR (slt install -f pkg.slt failed?)" >&2
		else
			echo "ERROR: missing autogen/pkg.slconf in $SLCONF_APP_DIR (run ./slc/script/refresh_local_packages.sh)" >&2
		fi
		exit 1
	fi
	write_app_slconf "$SLCONF_APP_DIR" "$(basename "$SILABS_APP_PATH")" || exit 1
	USE_APP_SLCONF=true
	SLC_WORK_DIR="$SLCONF_APP_DIR"
	SLC_PROJECT_FILE="$(basename "$SILABS_APP_PATH")"
	PACKAGE_PATHS=()
fi
CONFIG_ARGS=""
BRD_ONLY=$(echo "$SILABS_BOARD" | cut -f1 -d";")
if [ -z "$POST_BUILD_EXE" ]; then
	export POST_BUILD_EXE=$(which commander)
fi

# Determine vars based on project type provided (.slcw solution example or .slcp project example file)
if [[ "$SILABS_APP_PATH" == *.slcw ]]; then
	SILABS_APP=$(basename "$SILABS_APP_PATH" .slcw)
	MAKE_FILE=$SILABS_APP.solution.Makefile
	PROJECT_FLAG="-w"
	OUTPUT_DIR="out/$BRD_ONLY/${SILABS_APP}_solution"

elif [[ "$SILABS_APP_PATH" == *.slcp ]]; then
	SILABS_APP=$(basename "$SILABS_APP_PATH" .slcp)
	PROJECT_FLAG="-p"
	OUTPUT_DIR="out/$BRD_ONLY/$SILABS_APP"
	MAKE_FILE=$SILABS_APP.Makefile

else
	echo "ERROR: Did not provide a valid path for a .slcw or .slcp project file."
	exit 1
fi

if [ "$PACKAGE_ONLY" = true ]; then
	OUTPUT_DIR_ABS="$SLCONF_APP_DIR/$OUTPUT_DIR"
elif [ "$FROM_PACKAGE" = true ]; then
	OUTPUT_DIR_ABS="$MATTER_ROOT/$OUTPUT_DIR"
else
	OUTPUT_DIR_ABS="$OUTPUT_DIR"
fi

# Remove SILABS_APP_PATH and SILABS_BOARD from argument list
shift
shift
skip_gen=false
WITH_APP_COMPONENTS=""
WITHOUT_APP_COMPONENTS=""
WITH_BOOTLOADER_COMPONENTS=""
WITHOUT_BOOTLOADER_COMPONENTS=""
PIDS_ARG=""
GENERATE_BOOTLOADER=true
GENERATE_APPLICATION=true
GENERATE_TZ_SECURE=false
while [ $# -gt 0 ]; do
	case "$1" in
	--clean)
		rm -rf "$OUTPUT_DIR_ABS"
		shift
		;;
	--skip_gen)
		skip_gen=true
		shift
		;;
	--sisdk)
		SISDK_ROOT="$2"
		shift
		shift
		;;
	--output_suffix)
		OUTPUT_DIR="${OUTPUT_DIR}_$2"
		shift
		shift
		;;
	--with_app)
		WITH_APP_COMPONENTS="$2"
		shift
		shift
		;;
	--with_app\ *)
		WITH_APP_COMPONENTS="${1#--with_app }"
		shift
		;;
	--without_app)
		WITHOUT_APP_COMPONENTS="$2"
		shift
		shift
		;;
	--without_app\ *)
		WITHOUT_APP_COMPONENTS="${1#--without_app }"
		shift
		;;

	--with_bootloader)
		WITH_BOOTLOADER_COMPONENTS="$2"
		shift
		shift
		;;
	--with_bootloader\ *)
		WITH_BOOTLOADER_COMPONENTS="${1#--with_bootloader }"
		shift
		;;

	--without_bootloader)
		WITHOUT_BOOTLOADER_COMPONENTS="$2"
		shift
		shift
		;;
	--without_bootloader\ *)
		WITHOUT_BOOTLOADER_COMPONENTS="${1#--without_bootloader }"
		shift
		;;

	-pids)
		PIDS_ARG="$2"
		if [ "$PIDS_ARG" = "bootloader" ]; then
			GENERATE_APPLICATION=false
		elif [ "$PIDS_ARG" = "application" ]; then
			GENERATE_BOOTLOADER=false
		elif [ "$PIDS_ARG" = "trustzone" ]; then
			GENERATE_APPLICATION=true
			GENERATE_BOOTLOADER=true
			GENERATE_TZ_SECURE=true
		else
			echo "ERROR: Invalid -pids argument: $PIDS_ARG. Must be 'bootloader', 'application', or 'trustzone'"
			exit 1
		fi
		shift
		shift
		;;

	*)
		# Collect remaining arguments as configuration options
		CONFIG_ARGS+="$1 "
		shift
		;;
	esac
done

if [[ "$OUTPUT_DIR" == *"cmp-concurrent-high-bw-phy-em1" ]]; then
	python3 slc/script/em1-augmentation.py EM2 ## to change the sleep.c file from EM1 to EM2
fi

# Validate required tools and environment

if ! [ -x "$(command -v slc)" ]; then
	echo "ERROR: please install slc_cli for your host."
	exit 1
fi

if [ -n "${ARM_GCC_DIR:-}" ] && [ -d "$ARM_GCC_DIR" ] && [ -d "$ARM_GCC_DIR/bin" ]; then
	if ! [ -x "$ARM_GCC_DIR/bin/arm-none-eabi-gcc" ]; then
		echo "WARNING: might be an incompatible toolchain."
		echo "Please install gcc-arm-none-eabi for your host (see sl_setup_env.py)."
	fi
elif [ "$PACKAGE_ONLY" = true ] && command -v arm-none-eabi-gcc >/dev/null 2>&1; then
	: # gcc on PATH is sufficient for package-only builds without .env
elif [ "$PACKAGE_ONLY" = true ]; then
	echo "ERROR: arm-none-eabi-gcc not found (install gcc-arm-none-eabi via SLT or source slc/tools/.env)" >&2
	exit 1
else
	if ! [ -d "$ARM_GCC_DIR" ]; then
		echo "ERROR: ARM_GCC_DIR is not set or directory does not exist."
		exit 1
	fi

	if ! [ -d "$ARM_GCC_DIR/bin" ]; then
		echo "ERROR: $ARM_GCC_DIR path should have a bin folder."
		exit 1
	fi

	if ! [ -x "$ARM_GCC_DIR/bin/arm-none-eabi-gcc" ]; then
		echo "WARNING: might be an incompatible toolchain."
		echo "Please install gcc-arm-none-eabi for your host (see sl_setup_env.py)."
	fi
fi

echo "Building $SILABS_APP for $SILABS_BOARD in $OUTPUT_DIR"

if [ "$USE_SLT_PACKAGES" = true ]; then
	echo "Package mode: matter_app=$MATTER_APP_PKG matter=$MATTER_PKG"
	if [ "$PACKAGE_ONLY" = true ]; then
		echo "Package-only: output=$OUTPUT_DIR_ABS"
	fi
fi

# Make ZAP available to SLC-CLI
if [ -z "$STUDIO_ADAPTER_PACK_PATH" ] || [ ! -f "$STUDIO_ADAPTER_PACK_PATH/apack.json" ]; then
	if [ -n "$ZAP_INSTALL_PATH" ]; then
		export STUDIO_ADAPTER_PACK_PATH="$ZAP_INSTALL_PATH"
	fi
fi

if [ "$skip_gen" = false ]; then
	if [[ "$SILABS_APP_PATH" == *.slcw ]]; then
		if [[ "$SILABS_APP_PATH" != *wifi_soc* ]] && [ "$GENERATE_BOOTLOADER" = true ]; then
			# Get bootloader arguments
			BOOTLOADER_WITH_ARG=$(build_with_arg "$SILABS_BOARD" "$WITH_BOOTLOADER_COMPONENTS")
			BOOTLOADER_WITHOUT_ARG=$(build_without_arg "$WITHOUT_BOOTLOADER_COMPONENTS")

			# Generate bootloader
			echo "Generating bootloader..."
			run_slc_generate_project "$OUTPUT_DIR" $BOOTLOADER_WITH_ARG $BOOTLOADER_WITHOUT_ARG -pids bootloader
			if [ $? -ne 0 ]; then
				echo "ERROR: Failed to generate bootloader for: $SILABS_APP_PATH"
				exit 1
			fi
		fi

		if [ "$GENERATE_TZ_SECURE" = true ]; then
			# Get trustzone args
			WITH_ARG=$(build_with_arg "$SILABS_BOARD" "$WITH_APP_COMPONENTS")

			echo "Generating trustzone-secure..."
			run_slc_generate_project "$OUTPUT_DIR" $WITH_ARG -pids trustzone-secure
			if [ $? -ne 0 ]; then
				echo "ERROR: Failed to generate application for: $SILABS_APP_PATH"
				exit 1
			fi
		fi

		if [[ "$SILABS_APP_PATH" != *bootloader* ]] && [ "$GENERATE_APPLICATION" = true ]; then
			# Get application args
			APP_WITH_ARG=$(build_with_arg "$SILABS_BOARD" "$WITH_APP_COMPONENTS")
			APP_WITHOUT_ARG=$(build_without_arg "$WITHOUT_APP_COMPONENTS")

			echo "Generating application..."
			run_slc_generate_project "$OUTPUT_DIR" $APP_WITH_ARG $APP_WITHOUT_ARG -pids application
			if [ $? -ne 0 ]; then
				echo "ERROR: Failed to generate application for: $SILABS_APP_PATH"
				exit 1
			fi
		fi
	else
        APP_WITH_ARG=$(build_with_arg "$SILABS_BOARD" "$WITH_APP_COMPONENTS")
        APP_WITHOUT_ARG=$(build_without_arg "$WITHOUT_APP_COMPONENTS")
		# Generate .slcp projects
		run_slc_generate_project "$OUTPUT_DIR" $APP_WITH_ARG $APP_WITHOUT_ARG
		if [ $? -ne 0 ]; then
			echo "ERROR: Failed to generate project for: $SILABS_APP_PATH"
			exit 1
		fi
	fi
fi

# Build the project
if [ "$GENERATE_BOOTLOADER" = true ] && [ "$GENERATE_APPLICATION" = false ]; then
	# Use bootloader makefile instead of solution makefile
	echo "Building bootloader only..."
	BOOTLOADER_MAKEFILE=$(find "$OUTPUT_DIR/matter_bootloader" -maxdepth 1 -name "*.Makefile" | head -1)
	if [ -z "$BOOTLOADER_MAKEFILE" ]; then
		echo "ERROR: No bootloader Makefile found in $OUTPUT_DIR/matter_bootloader"
		exit 1
	fi
	BOOTLOADER_MAKEFILE_NAME=$(basename "$BOOTLOADER_MAKEFILE")
	if ! make all -C "$OUTPUT_DIR/matter_bootloader" -f "$BOOTLOADER_MAKEFILE_NAME" -j13; then
		echo "ERROR: Failed to build bootloader"
		exit 1
	fi
elif [ "$GENERATE_BOOTLOADER" = false ] && [ "$GENERATE_APPLICATION" = true ]; then
	# Use application makefile instead of solution makefile
	echo "Building application only..."
	APP_MAKEFILE=$(find "$OUTPUT_DIR_ABS" -mindepth 1 -maxdepth 2 -name "*.Makefile" ! -name "*.solution.Makefile" | head -1)
	if [ -z "$APP_MAKEFILE" ]; then
		echo "ERROR: No application Makefile found in $OUTPUT_DIR_ABS"
		exit 1
	fi
	APP_DIR=$(dirname "$APP_MAKEFILE")
	APP_MAKEFILE_NAME=$(basename "$APP_MAKEFILE")
	if ! make all -C "$APP_DIR" -f "$APP_MAKEFILE_NAME" -j13; then
		echo "ERROR: Failed to build application"
		exit 1
	fi
else
	echo "Building solution..."
	if ! make all -C "$OUTPUT_DIR_ABS" -f "$MAKE_FILE" -j13; then
		echo "ERROR: Failed to build solution"
		exit 1
	fi
fi

if [[ "$OUTPUT_DIR" == *"cmp-concurrent-high-bw-phy-em1" ]]; then
	python3 slc/script/em1-augmentation.py EM1 ## to revert the changes made to the sleep.c file from EM2 to EM1
fi