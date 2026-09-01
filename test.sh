#!/bin/bash
set -e

GENERATE=false
if [ ! -d "out" ]; then
  GENERATE=true
fi

echo "BUILDING..."
./slc/build.sh ./slc/apps/thermostat/wifi/matter_wifi_soc_thermostat_dual_stack_freertos.slcw "brd4338a" --copy-sources $([ "$GENERATE" = false ] && echo --skip_gen) 2>&1 > build.log
tail build.log

echo "SIZE..."
OUT_APP=out/brd4338a/matter_wifi_soc_thermostat_dual_stack_freertos_solution/thermostat_siwx/build/debug/matter_wifi_soc_thermostat_dual_stack_freertos.out
ARM_GCC_DIR="$(./slc/tools/slt where gcc-arm-none-eabi)"
$ARM_GCC_DIR/bin/arm-none-eabi-size -A "${OUT_APP}" | tee -a build.log

echo "FLASHING..."
commander rps load out/brd4338a/matter_wifi_soc_thermostat_dual_stack_freertos_solution/artifact/matter_wifi_soc_thermostat_dual_stack_freertos.rps
sleep 5

# if darwin, use gtimeout
TIMEOUT_CMD=timeout
if [ "$(uname)" == "Darwin" ]; then
  TIMEOUT_CMD=gtimeout
fi
echo "CONNECTING..."
$TIMEOUT_CMD 120 commander rtt connect 2>&1 |tee device.log
