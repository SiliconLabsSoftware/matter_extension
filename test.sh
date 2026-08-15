#!/bin/bash
set -e

GENERATE=false
if [ ! -d "out" ]; then
  GENERATE=true
fi
echo "BUILDING..."
./slc/build.sh ./slc/apps/thermostat/wifi/matter_wifi_soc_thermostat_dual_stack_freertos.slcw "brd4338a" $([ "$GENERATE" = false ] && echo --skip_gen) 2>&1 > build.log
tail build.log
echo "FLASHING..."
commander rps load out/brd4338a/matter_wifi_soc_thermostat_dual_stack_freertos_solution/artifact/matter_wifi_soc_thermostat_dual_stack_freertos.rps
sleep 5
echo "CONNECTING..."
gtimeout 180 commander rtt connect 2>&1 |tee device.log
