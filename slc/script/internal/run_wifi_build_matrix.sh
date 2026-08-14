#!/usr/bin/env bash
# Run a fixed smoke matrix of Matter sample builds from Conan/SLT packages
# (matter + matter_app) and print a PASS/FAIL summary.
#
# Usage (from repo root):
#   ./slc/script/internal/run_wifi_build_matrix.sh --suite smoke-wifi --version 2.10.0-0.dev
#   ./slc/script/internal/run_wifi_build_matrix.sh --suite smoke-thread --version 2.10.0-alpha.9
#   ./slc/script/internal/run_wifi_build_matrix.sh --suite smoke-cmp --version 2.10.0-0.dev --export
#   ./slc/script/internal/run_wifi_build_matrix.sh --suite sanity --version 2.10.0-0.dev
#   ./slc/script/internal/run_wifi_build_matrix.sh --suite all --version 2.10.0-0.dev --export --clean
#   ./slc/script/internal/run_wifi_build_matrix.sh --suite all --version 2.10.0-0.dev --dry-run
#   ./slc/script/internal/run_wifi_build_matrix.sh --suite smoke-wifi --version 2.10.0-0.dev -j 16
#
# Suites:
#   smoke-wifi   Wi-Fi SoC / 917 NCP lock + platform
#   smoke-thread Thread platform template (non-ICD / ICD)
#   smoke-cmp    Zigbee concurrent / sequential + thermostat concurrent
#   sanity       917 SoC lighting (brd4338a) + Thread lighting (brd4187c)
#   all          Run every smoke suite above in order (excludes sanity)
#
# Package options (same idea as packages/dev_build_app.sh):
#   default      Use cached matter/matter_app for --version (no remove, no export-pkg)
#   --export     conan export-pkg matter + matter_app at --version
#   --clean      Remove cached matter/matter_app for --version first (requires --export)
#
# Continues after failures so the full matrix result is reported.
# Exit code: 0 if all builds pass, 1 if any fail.
#
# Flow:
#   1) optional: --clean remove + --export export-pkg matter + matter_app
#   2) slt install matter_app/<version>@silabs (uses cache unless freshly exported)
#   3) for each config: find project under $(slt where matter_app),
#      slt install in app dir, slc generate, make
#
# Solutions (.slcw / sampleAppName ending in _full):
#   App-only components (withApp) must NOT go in a flat --with - SLC applies
#   --with to every project in the workspace, which pollutes the bootloader
#   (e.g. siwx917_ncp_brd4357c). Matches CI / slc/build.sh --with_app:
#     generate -pids bootloader --with <board>
#     generate -pids application --with <board>[,withApp]

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "${ROOT}"

MATTER_PACKAGE_VERSION=""
SUITE=""
DRY_RUN=0
DO_EXPORT=0
CLEAN=0
GENERATOR_TIMEOUT=300
JOBS=8
# Field separator for RESULTS records (project, additional_cmd, result)
RS=$'\x1e'
# Newline placeholder inside additional_cmd (read cannot span real newlines)
NL=$'\x1f'

usage() {
  sed -n '2,40p' "$0" | sed 's/^# \?//'
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
    --dry-run) DRY_RUN=1; shift ;;
    --export) DO_EXPORT=1; shift ;;
    --clean) CLEAN=1; shift ;;
    --suite)
      SUITE="${2:-}"
      [[ -n "${SUITE}" ]] || die "--suite needs a value"
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
    -h | --help) usage 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage 1
      ;;
  esac
done

[[ -n "${SUITE}" ]] || die "required: --suite <smoke-wifi|smoke-thread|smoke-cmp|sanity|all>"
[[ -n "${MATTER_PACKAGE_VERSION}" ]] || die "required: --version <ver> (e.g. --version 2.10.0-0.dev)"
if [[ "${CLEAN}" -eq 1 && "${DO_EXPORT}" -eq 0 ]]; then
  die "--clean only applies with --export"
fi

# Each entry: sampleAppName|board|withApp|appName|makeParams
# board    : host board id for --with (e.g. brd4187c). May include a device
#            qualifier as board,device (e.g. brd1019a,SIMG301M113WIH).
# withApp  : optional app-only components; empty if unused
# appName  : optional out-dir suffix; empty if unused
# sampleAppName ending in _full resolves to the matching .slcw (solution).

MATRIX_SMOKE_WIFI=(
  "matter_wifi_917_ncp_lock_app_freertos_full|brd4187c|||-j8"
  "matter_wifi_917_ncp_lock_app_freertos_full|brd4187c|siwx917_ncp_brd4357c|brd4357c|-j8"
  "matter_wifi_soc_lock_app_freertos|brd4343c|||-j8"
  "matter_wifi_soc_lock_app_freertos|brd4338a|||-j8"
  "matter_wifi_soc_platform_template_freertos|brd4338a|matter_peripherals_917soc|peripherals|-j8"
  "matter_wifi_soc_platform_template_freertos|brd4338a|matter_peripherals_917soc,matter_icd_core|peripherals-icd|-j8"
)

# Thread platform smoke (non-ICD / ICD). Workspace series matches demos.xml.
MATRIX_SMOKE_THREAD=(
  "matter_thread_soc_platform_template_series_2_freertos_full|brd4187c|matter_peripherals|peripherals|-j8"
  "matter_thread_soc_platform_template_series_2_freertos_full|brd4116a|matter_peripherals,matter_icd_core|peripherals-icd|-j8"
  "matter_thread_soc_platform_template_series_3_freertos_full|brd4407a|matter_peripherals|peripherals|-j8"
)

# CMP smoke: zigbee concurrent/sequential + thermostat concurrent.
MATRIX_SMOKE_CMP=(
  "matter_thread_soc_zigbee_light_series_2_freertos_full|brd4116a|matter_zigbee_concurrent,matter_zigbee_multiprotocol_common|cmp-concurrent|-j8"
  "matter_thread_soc_zigbee_light_series_3_freertos_full|brd4407a|matter_zigbee_concurrent,matter_zigbee_multiprotocol_common|cmp-concurrent|-j8"
  "matter_thread_soc_zigbee_light_series_3_freertos_full|brd1019a,SIMG301M113WIH|matter_zigbee_sequential|sequential|-j8"
  "matter_thread_soc_thermostat_series_3_freertos_full|brd1019a,SIMG301M113WIH|matter_zigbee_concurrent,matter_zigbee_multiprotocol_common|cmp-concurrent|-j8"
)

# Sanity: 917 SoC lighting + Thread series-2 lighting.
MATRIX_SANITY=(
  "matter_wifi_soc_lighting_app_freertos|brd4338a|||-j8"
  "matter_thread_soc_lighting_app_series_2_freertos_full|brd4187c|||-j8"
)

select_matrix() {
  local suite="$1"
  case "${suite}" in
    smoke-wifi) MATRIX=("${MATRIX_SMOKE_WIFI[@]}") ;;
    smoke-thread) MATRIX=("${MATRIX_SMOKE_THREAD[@]}") ;;
    smoke-cmp) MATRIX=("${MATRIX_SMOKE_CMP[@]}") ;;
    sanity) MATRIX=("${MATRIX_SANITY[@]}") ;;
    *)
      die "unknown suite: ${suite} (expected smoke-wifi|smoke-thread|smoke-cmp|sanity|all)"
      ;;
  esac
}

board_dir_from_with() {
  # Out-dir board token: strip optional ",DEVICE" qualifier.
  echo "${1%%,*}"
}

merge_with() {
  local board="$1"
  local with_app="$2"
  if [[ -n "${with_app}" ]]; then
    echo "${board},${with_app}"
  else
    echo "${board}"
  fi
}

config_label() {
  local sample_app_name="$1"
  local board="$2"
  local with_app="$3"
  local app_name="$4"
  local label="${sample_app_name}"
  if [[ -n "${app_name}" ]]; then
    label="${label}/${app_name}"
  fi
  label="${label} [$(merge_with "${board}" "${with_app}")]"
  echo "${label}"
}

# Exact slc generate args used under the hood (may be multi-line for solutions).
additional_command_for() {
  local sample_app_name="$1"
  local board="$2"
  local with_app="$3"
  local app_with
  app_with="$(merge_with "${board}" "${with_app}")"
  if [[ "${sample_app_name}" == *_full ]]; then
    printf '%s\n%s' \
      "--with ${board} --generator-timeout ${GENERATOR_TIMEOUT} -pids bootloader" \
      "--with ${app_with} --generator-timeout ${GENERATOR_TIMEOUT} -pids application"
  else
    printf '%s' "--with ${app_with} --generator-timeout ${GENERATOR_TIMEOUT}"
  fi
}

project_path_for() {
  local sample_app_name="$1"
  if [[ "${sample_app_name}" == *_full ]]; then
    echo "${sample_app_name%_full}.slcw"
  else
    echo "${sample_app_name}.slcp"
  fi
}

record_result() {
  local suite_name="$1"
  local project_path="$2"
  local additional_cmd="$3"
  local result="$4"
  # Encode newlines so each RESULTS entry stays a single physical line.
  additional_cmd="${additional_cmd//$'\n'/${NL}}"
  RESULTS+=("${suite_name}${RS}${project_path}${RS}${additional_cmd}${RS}${result}")
}

resolve_project_under_package() {
  # Sets PROJECT_PATH, PROJECT_FLAG, PROJECT_FILE, PROJECT_BASE.
  local sample_app_name="$1"
  local matter_app_root="$2"
  local base="${sample_app_name%_full}"
  local want_solution=0
  local found=""

  if [[ "${sample_app_name}" == *_full ]]; then
    want_solution=1
  fi

  if [[ "${want_solution}" -eq 1 ]]; then
    found="$(find "${matter_app_root}" -type f -name "${base}.slcw" 2>/dev/null | head -n1 || true)"
    if [[ -n "${found}" ]]; then
      PROJECT_PATH="${found}"
      PROJECT_FLAG="-w"
      PROJECT_FILE="$(basename "${found}")"
      PROJECT_BASE="${base}"
      return 0
    fi
  fi

  found="$(find "${matter_app_root}" -type f -name "${base}.slcp" 2>/dev/null | head -n1 || true)"
  if [[ -n "${found}" ]]; then
    PROJECT_PATH="${found}"
    PROJECT_FLAG="-p"
    PROJECT_FILE="$(basename "${found}")"
    PROJECT_BASE="${base}"
    return 0
  fi

  found="$(find "${matter_app_root}" -type f -name "${base}.slcw" 2>/dev/null | head -n1 || true)"
  if [[ -n "${found}" ]]; then
    PROJECT_PATH="${found}"
    PROJECT_FLAG="-w"
    PROJECT_FILE="$(basename "${found}")"
    PROJECT_BASE="${base}"
    return 0
  fi

  return 1
}

# --- env / package setup (skipped for dry-run except printing intent) ---
export MATTER_PACKAGE_VERSION
REF="matter_app/${MATTER_PACKAGE_VERSION}@silabs"

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

if [[ -x "${ROOT}/slc/tools/slt" ]]; then
  export PATH="${ROOT}/slc/tools:${PATH}"
fi

SLT_HOME="${SLT_HOME:-${HOME}/.silabs/slt}"
CONAN="${SLT_HOME}/engines/conan/conan/conan"
export CONAN_HOME="${CONAN_HOME:-${SLT_HOME}/installs/conan}"

MATTER_APP=""
MATTER=""

setup_packages() {
  need_cmd slt
  need_cmd slc
  need_cmd make
  need_cmd find

  echo "Ensuring SLT Conan engine..."
  slt install conan
  [[ -x "${CONAN}" ]] || die "SLT Conan missing after install: ${CONAN}"
  echo "Using CONAN=${CONAN}"
  echo "CONAN_HOME=${CONAN_HOME}"
  echo "MATTER_PACKAGE_VERSION=${MATTER_PACKAGE_VERSION}"

  if [[ "${DO_EXPORT}" -eq 1 ]]; then
    if [[ "${CLEAN}" -eq 1 ]]; then
      echo "Removing cached packages for version ${MATTER_PACKAGE_VERSION}..."
      "${CONAN}" remove "matter/${MATTER_PACKAGE_VERSION}@silabs" -c || true
      "${CONAN}" remove "matter_app/${MATTER_PACKAGE_VERSION}@silabs" -c || true
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
  else
    echo "Using cached packages for ${MATTER_PACKAGE_VERSION} (pass --export to rebuild packages)"
  fi

  echo "=== Conan home / local packages (must match export) ==="
  echo "CONAN=${CONAN}"
  echo "CONAN_HOME=${CONAN_HOME}"
  "${CONAN}" config home
  "${CONAN}" list "matter/${MATTER_PACKAGE_VERSION}@silabs:*"
  "${CONAN}" list "matter_app/${MATTER_PACKAGE_VERSION}@silabs:*"

  echo "Installing ${REF} via SLT..."
  slt install "${REF}" -e conan

  MATTER_APP="$(slt where matter_app)"
  MATTER="$(slt where matter)"
  [[ -n "${MATTER_APP}" ]] || die "slt where matter_app returned empty (export with --export if missing)"
  [[ -n "${MATTER}" ]] || die "slt where matter returned empty (export with --export if missing)"
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
}

build_one() {
  local board="$1"
  local with_app="$2"
  local app_name="$3"
  local make_params="$4"
  local app_dir
  local out_dir
  local makefile
  local make_jobs="${JOBS}"
  local app_with
  local board_dir
  local with_app_disp

  app_with="$(merge_with "${board}" "${with_app}")"
  board_dir="$(board_dir_from_with "${board}")"
  app_dir="$(dirname "${PROJECT_PATH}")"

  if [[ -n "${app_name}" ]]; then
    out_dir="out/${board_dir}/${PROJECT_BASE}_${app_name}"
  else
    out_dir="out/${board_dir}/${PROJECT_BASE}"
  fi

  if [[ "${PROJECT_FLAG}" == "-w" ]]; then
    makefile="${PROJECT_BASE}.solution.Makefile"
  else
    makefile="${PROJECT_BASE}.Makefile"
  fi

  if [[ "${make_params}" =~ -j([0-9]+) ]]; then
    make_jobs="${BASH_REMATCH[1]}"
  fi

  if [[ -n "${with_app}" ]]; then
    with_app_disp="${with_app}"
  else
    with_app_disp="(none)"
  fi

  echo "App dir: ${app_dir}"
  echo "Project: ${PROJECT_FILE} (${PROJECT_FLAG})  board: ${board}  withApp: ${with_app_disp}  out: ${out_dir}"

  (
    set -e
    cd "${app_dir}"
    echo "Running slt install (project pkg.slt / pkg.slconf)..."
    slt install

    if [[ "${PROJECT_FLAG}" == "-w" ]]; then
      # App-only components must not be applied to the bootloader project.
      echo "Running slc generate (bootloader, --with ${board})..."
      slc generate \
        -d "${out_dir}" \
        "${PROJECT_FLAG}" "${PROJECT_FILE}" \
        --with "${board}" \
        -pids bootloader \
        --generator-timeout="${GENERATOR_TIMEOUT}" \
        -o makefile

      echo "Running slc generate (application, --with ${app_with})..."
      slc generate \
        -d "${out_dir}" \
        "${PROJECT_FLAG}" "${PROJECT_FILE}" \
        --with "${app_with}" \
        -pids application \
        --generator-timeout="${GENERATOR_TIMEOUT}" \
        -o makefile
    else
      echo "Running slc generate (--with ${app_with})..."
      slc generate \
        -d "${out_dir}" \
        "${PROJECT_FLAG}" "${PROJECT_FILE}" \
        --with "${app_with}" \
        --generator-timeout="${GENERATOR_TIMEOUT}" \
        -o makefile
    fi

    if [[ ! -f "${out_dir}/${makefile}" ]]; then
      echo "error: expected ${out_dir}/${makefile} after generate" >&2
      exit 1
    fi
    echo "Building with make -j${make_jobs}..."
    make -C "${out_dir}" -f "${makefile}" -j"${make_jobs}"
    echo "Done: ${app_dir}/${out_dir}"
  )
}

run_matrix() {
  local suite_name="$1"
  local idx=0
  local total=${#MATRIX[@]}
  local entry
  local sample_app_name
  local board
  local with_app
  local app_name
  local make_params
  local label
  local base
  local app_with
  local board_dir
  local rc
  local make_jobs_disp
  local project_path
  local additional_cmd

  echo "========================================"
  echo "Suite: ${suite_name} (${total} configs)"
  echo "Repo: ${ROOT}"
  echo "Package: ${REF}"
  echo "========================================"
  echo

  for entry in "${MATRIX[@]}"; do
    idx=$((idx + 1))
    IFS='|' read -r sample_app_name board with_app app_name make_params <<<"${entry}"

    label="$(config_label "${sample_app_name}" "${board}" "${with_app}" "${app_name}")"
    board_dir="$(board_dir_from_with "${board}")"
    project_path="$(project_path_for "${sample_app_name}")"
    additional_cmd="$(additional_command_for "${sample_app_name}" "${board}" "${with_app}")"

    echo "----------------------------------------"
    echo "[${idx}/${total}] ${label}"

    if [[ "${DRY_RUN}" -eq 1 ]]; then
      base="${sample_app_name%_full}"
      app_with="$(merge_with "${board}" "${with_app}")"
      if [[ "${sample_app_name}" == *_full ]]; then
        echo "Would: find ${base}.slcw under matter_app"
        echo "Would: slc generate -w ... --with ${board} -pids bootloader"
        echo "Would: slc generate -w ... --with ${app_with} -pids application"
      else
        echo "Would: find ${base}.slcp under matter_app, slc generate -p ... --with ${app_with}"
      fi
      if [[ -n "${app_name}" ]]; then
        echo "Would out: out/${board_dir}/${base}_${app_name}"
      else
        echo "Would out: out/${board_dir}/${base}"
      fi
      if [[ -n "${make_params}" ]]; then
        make_jobs_disp="${make_params}"
      else
        make_jobs_disp="-j${JOBS}"
      fi
      echo "Would make: make ${make_jobs_disp}"
      record_result "${suite_name}" "${project_path}" "${additional_cmd}" "SKIP"
      echo "----------------------------------------"
      continue
    fi

    if ! resolve_project_under_package "${sample_app_name}" "${MATTER_APP}"; then
      echo "[${idx}/${total}] FAIL  ${label} - project not found under ${MATTER_APP}"
      record_result "${suite_name}" "${project_path}" "${additional_cmd}" "FAILED"
      FAIL=$((FAIL + 1))
      echo "----------------------------------------"
      continue
    fi

    echo "Resolved: ${PROJECT_PATH}"
    echo "----------------------------------------"

    if build_one "${board}" "${with_app}" "${app_name}" "${make_params}"; then
      echo "[${idx}/${total}] PASS  ${label}"
      record_result "${suite_name}" "${project_path}" "${additional_cmd}" "SUCCESS"
      PASS=$((PASS + 1))
    else
      rc=$?
      echo "[${idx}/${total}] FAIL  ${label} (exit ${rc})"
      record_result "${suite_name}" "${project_path}" "${additional_cmd}" "FAILED"
      FAIL=$((FAIL + 1))
    fi
    echo
  done
}

print_summary_table() {
  local w_suite=13
  local w_proj=49
  local w_cmd=83
  local w_tc=11
  local w_res=7
  local r suite_name project_path additional_cmd result
  local first line

  hrule() {
    printf '+-%s-+-%s-+-%s-+-%s-+-%s-+\n' \
      "$(printf '%*s' "${w_suite}" '' | tr ' ' '-')" \
      "$(printf '%*s' "${w_proj}" '' | tr ' ' '-')" \
      "$(printf '%*s' "${w_cmd}" '' | tr ' ' '-')" \
      "$(printf '%*s' "${w_tc}" '' | tr ' ' '-')" \
      "$(printf '%*s' "${w_res}" '' | tr ' ' '-')"
  }

  echo "========================================"
  echo "Results summary"
  echo "========================================"
  hrule
  printf "| %-*s | %-*s | %-*s | %-*s | %-*s |\n" \
    "${w_suite}" "Suite" \
    "${w_proj}" "Project Path" \
    "${w_cmd}" "Additional Command" \
    "${w_tc}" "Toolchain" \
    "${w_res}" "Result"
  hrule

  for r in "${RESULTS[@]}"; do
    IFS="${RS}" read -r suite_name project_path additional_cmd result <<<"${r}"
    additional_cmd="${additional_cmd//${NL}/$'\n'}"
    first=1
    while IFS= read -r line || [[ -n "${line}" ]]; do
      if [[ "${first}" -eq 1 ]]; then
        printf "| %-*s | %-*s | %-*s | %-*s | %-*s |\n" \
          "${w_suite}" "${suite_name}" \
          "${w_proj}" "${project_path}" \
          "${w_cmd}" "${line}" \
          "${w_tc}" "gcc" \
          "${w_res}" "${result}"
        first=0
      else
        printf "| %-*s | %-*s | %-*s | %-*s | %-*s |\n" \
          "${w_suite}" "" \
          "${w_proj}" "" \
          "${w_cmd}" "${line}" \
          "${w_tc}" "" \
          "${w_res}" ""
      fi
    done <<< "${additional_cmd}"
    hrule
  done

  echo
  echo "Total: ${#RESULTS[@]}  Pass: ${PASS}  Fail: ${FAIL}"
}

RESULTS=()
PASS=0
FAIL=0

if [[ "${SUITE}" == "all" ]]; then
  SUITES=(smoke-wifi smoke-thread smoke-cmp)
else
  SUITES=("${SUITE}")
fi

if [[ "${DRY_RUN}" -eq 0 ]]; then
  setup_packages
else
  echo "(dry-run: skipping package install/export)"
  echo
fi

for suite_name in "${SUITES[@]}"; do
  select_matrix "${suite_name}"
  run_matrix "${suite_name}"
done

print_summary_table

if [[ "${DRY_RUN}" -eq 1 ]]; then
  exit 0
fi
[[ "${FAIL}" -eq 0 ]]
