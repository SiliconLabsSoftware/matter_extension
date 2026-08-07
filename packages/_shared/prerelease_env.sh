#!/usr/bin/env bash
# Prerelease env helpers for Matter Conan packages.
#
# Usage (from repo root or any cwd):
#   source packages/_shared/prerelease_env.sh
#   set_prerelease_env
#
# Both matter and matter_app share one label and one number so they publish
# the same version (matter_app requires matter/{same version}).
#
# Sets:
#   SL_PRERELEASE         - absolute path to packages/.prerelease
#   SL_PRERELEASE_NUMBER  - kept if already set (e.g. Jenkins PR number);
#                           otherwise unset so action-conan-create-publish
#                           auto-generates the next number from the remote.
#
# Recipes use silabs_package_assistant.get_version(matter.slce):
#   - local export-pkg (no CI): always {base}-0.dev (e.g. 2.10.0-0.dev)
#   - CI + these env vars: {base}-{label}.{number} (e.g. 2.10.0-alpha.7)
# Override any time with: export MATTER_PACKAGE_VERSION=2.10.0-alpha.7
#
# Call once, then export/publish both matter and matter_app with the same env.

# Resolve packages/.prerelease at source time without cd (avoids fragile nested cd/pwd).
# BASH_SOURCE[0] is this file when sourced: .../packages/_shared/prerelease_env.sh
_prerelease_env_file="${BASH_SOURCE[0]//$'\r'/}"
_prerelease_env_file="${_prerelease_env_file//$'\n'/}"
_prerelease_env_dir="${_prerelease_env_file%/*}"
if [[ "${_prerelease_env_dir}" != /* ]]; then
    _prerelease_env_dir="${PWD}/${_prerelease_env_dir}"
fi
# packages/_shared -> packages/.prerelease
_MATTER_SHARED_PRERELEASE="${_prerelease_env_dir%/*}/.prerelease"
unset _prerelease_env_file _prerelease_env_dir

set_prerelease_env() {
    local prerelease_file label

    prerelease_file="${_MATTER_SHARED_PRERELEASE}"

    if [[ ! -f "${prerelease_file}" ]]; then
        echo "Error: missing .prerelease file: ${prerelease_file}" >&2
        return 1
    fi

    label="$(tr -d '[:space:]' < "${prerelease_file}")"
    if [[ -z "${label}" ]]; then
        echo "Error: packages/.prerelease is empty (expected alpha|beta|rc)" >&2
        return 1
    fi

    # Set SL_PRERELEASE to absolute path (shared by matter and matter_app)
    export SL_PRERELEASE="${prerelease_file}"

    # If SL_PRERELEASE_NUMBER is already set (e.g., from Jenkins env with PR number), use it
    # Otherwise, unset to let action-conan-create-publish auto-generate the pre-release number
    if [[ -n "${SL_PRERELEASE_NUMBER:-}" ]]; then
        echo "Using SL_PRERELEASE_NUMBER from environment: ${SL_PRERELEASE_NUMBER}"
    else
        echo "SL_PRERELEASE_NUMBER not set, will auto-generate based on remote"
        unset SL_PRERELEASE_NUMBER
    fi

    echo "SL_PRERELEASE=${SL_PRERELEASE} (label=${label})"
    echo "Use this env for both matter and matter_app publishes"
}
