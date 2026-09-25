#!/usr/bin/env bash

# This script is used to generate a graph of the project dependencies.
# It is used to help with the development of the project.
# It is not used to generate the final graph.
# It is used to help with the development of the project.

set -x

MATTER_ROOT="${MATTER_ROOT:-$(pwd -P)}"

args=("$@")

matter_sdk="$MATTER_ROOT"
sisdk="$MATTER_ROOT/third_party/simplicity_sdk"
wifi_sdk="$MATTER_ROOT/third_party/wifi_sdk"

# Bash 3.2 (macOS default) does not support negative array subscripts.
_argc=${#args[@]}
if [ "$_argc" -lt 2 ]; then
  echo "Usage: $0 [options] <project.slcw> <board>" >&2
  exit 1
fi

project_path=${args[$((_argc - 2))]}
board=${args[$((_argc - 1))]}

# Drop the last two positional args (project + board)
if [ "$_argc" -eq 2 ]; then
  args=()
else
  args=("${args[@]:0:$((_argc - 2))}")
fi

i=0
while [ $i -lt ${#args[@]} ]; do
  arg="${args[$i]}"
  case $arg in
    --sisdk)
      i=$((i + 1))
      sisdk="${args[$i]}"
      ;;
    --wifi-sdk)
      i=$((i + 1))
      wifi_sdk="${args[$i]}"
      ;;
    *)
      extra_args+=("$arg")
      ;;
  esac
  i=$((i + 1))
done

SLC_TOOLS_PATH="$($MATTER_ROOT/slc/tools/slt where slc-cli)"

$SLC_TOOLS_PATH/slc graph \
    --project-file $project_path \
    --sdk-package-path $matter_sdk \
    --sdk-package-path $sisdk \
    --sdk-package-path $wifi_sdk \
    --with $board \
    "${extra_args[@]}"
