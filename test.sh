#!/bin/bash
set -e

GENERATE=false
APP_NAME="matter_wifi_soc_thermostat_freertos"
OUT_DIR="./out/brd4338a/${APP_NAME}_solution"
SLCW_PATH=$(find ./slc/apps/ -name "${APP_NAME}.slcw" -type f | head -n 1)

if [ ! -d "${OUT_DIR}" ]; then
  GENERATE=true
fi

echo "BUILDING..."
./slc/build.sh ${SLCW_PATH} "brd4338a" --copy-sources $([ "$GENERATE" = false ] && echo --skip_gen) 2>&1 > build.log
tail build.log

echo "SIZE..."
OUT_APP=$(find ${OUT_DIR} -name "${APP_NAME}.out" -type f)
ARM_GCC_DIR="$(./slc/tools/slt where gcc-arm-none-eabi)"
$ARM_GCC_DIR/bin/arm-none-eabi-size -A "${OUT_APP}" | tee -a build.log

echo "FLASHING..."
commander rps load ${OUT_DIR}/artifact/${APP_NAME}.rps
sleep 5

# if darwin, use gtimeout
TIMEOUT_CMD=timeout
if [ "$(uname)" == "Darwin" ]; then
  TIMEOUT_CMD=gtimeout
fi
echo "CONNECTING..."
$TIMEOUT_CMD 120 commander vcom connect 2>&1 |tee device.log