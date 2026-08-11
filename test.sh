#!/bin/bash
set -xe

# rm -rf out
if [ ! -d "out" ]; then
  ./slc/build.sh ./slc/apps/thermostat/wifi/matter_wifi_soc_thermostat_freertos.slcw "brd4338a" > build.log 2>&1
else
  ./slc/build.sh ./slc/apps/thermostat/wifi/matter_wifi_soc_thermostat_freertos.slcw "brd4338a" --skip_gen > build.log 2>&1
fi
commander rps load out/brd4338a/matter_wifi_soc_thermostat_freertos_solution/artifact/matter_wifi_soc_thermostat_freertos.rps
sleep 5
gtimeout 300 commander rtt connect --timestamp > device.log 2>&1
