#!/bin/bash

# This script copies the Matter extension files to the supplied directory path

MATTER_ROOT="$(dirname "$0")/.."
GSDK_ROOT="$MATTER_ROOT/third_party/silabs/simplicity_sdk"
WIFI_SDK_ROOT="$MATTER_ROOT/third_party/silabs/wifi_sdk"

if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters"
    echo "Usage: $0 <destination directory>"
    exit 1
fi

DEST_DIR=$1
EXT_DIR="$DEST_DIR/matter_extension"

if [ ! -d "$DEST_DIR" ]; then
    echo "Directory $DEST_DIR does not exist"
    exit 1
fi

# Create directories within new extension for necessary source/header files to be copied to
mkdir -p $EXT_DIR/examples/platform/
mkdir -p $EXT_DIR/examples/common/
mkdir -p $EXT_DIR/examples/shell/
mkdir -p $EXT_DIR/examples/common/QRCode/repo/
mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/bus/
mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/pds/
mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/secure_link/
mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/config/
mkdir -p $EXT_DIR/third_party/silabs/matter_support/matter/mbedtls/tinycrypt/
mkdir -p $EXT_DIR/third_party/silabs/matter_support/matter/si91x/siwx917/BRD4338A/support/
mkdir -p $EXT_DIR/third_party/silabs/matter_support/platform/emdrv/
mkdir -p $EXT_DIR/third_party/mbedtls/

mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/segger/systemview
mkdir -p $EXT_DIR/third_party/zap/repo/zcl-builtin/shared

mkdir $EXT_DIR/third_party/silabs/wiseconnect-wifi-bt-sdk/
mkdir $EXT_DIR/examples/providers/

#GSDK LWIP
mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src/api
mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src/core
mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src/netif
mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src/include/lwip
mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/platform/common/errno/inc
mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src/include/compat/posix/sys
mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src/include/compat/posix/net

cp -R $GSDK_ROOT/util/third_party/lwip/lwip/src/api $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src
cp -R $GSDK_ROOT/util/third_party/lwip/lwip/src/core $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src
cp $GSDK_ROOT/util/third_party/lwip/lwip/src/netif/ethernet.c $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src/netif/
cp -R $GSDK_ROOT/util/third_party/lwip/lwip/src/include/lwip  $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src/include
cp -R $GSDK_ROOT/util/third_party/lwip/lwip/src/include/netif $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src/include
cp -R $GSDK_ROOT/platform/common/errno/inc $EXT_DIR/third_party/silabs/simplicity_sdk/platform/common/errno
cp -R $GSDK_ROOT/util/third_party/lwip/lwip/src/include/compat/posix/sys $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src/include/compat/posix
cp -R $GSDK_ROOT/util/third_party/lwip/lwip/src/include/compat/posix/net $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/lwip/lwip/src/include/compat/posix


#WIFI_SDK fw upgrade for 917SoC
mkdir -p $EXT_DIR/third_party/silabs/wifi_sdk/components/device/silabs/si91x/wireless


# Override built-in crypto configurations MATTER-1838
mkdir -p $EXT_DIR/third_party/silabs/simplicity_sdk/platform/security/sl_component/sl_mbedtls_support/config/template

cp -R $GSDK_ROOT/platform/security/sl_component/sl_mbedtls_support/config/template $EXT_DIR/third_party/silabs/simplicity_sdk/platform/security/sl_component/sl_mbedtls_support/config
cp -R $GSDK_ROOT/platform/security/sl_component/sl_mbedtls_support/config $EXT_DIR/third_party/silabs/simplicity_sdk/platform/security/sl_component/sl_mbedtls_support

cp -R $WIFI_SDK_ROOT/components/device/silabs/si91x/wireless/firmware_upgrade $EXT_DIR/third_party/silabs/wifi_sdk/components/device/silabs/si91x/wireless/firmware_upgrade

# Files needed by various SLC components included in Matter projects
cp -R $MATTER_ROOT/src $EXT_DIR
cp -R $MATTER_ROOT/slc $EXT_DIR
cp -R $MATTER_ROOT/examples/platform/silabs $EXT_DIR/examples/platform
cp -R $MATTER_ROOT/examples/shell/shell_common $EXT_DIR/examples/shell
cp -R $MATTER_ROOT/examples/providers $EXT_DIR/examples
cp -R $MATTER_ROOT/examples/common/QRCode/repo/c $EXT_DIR/examples/common/QRCode/repo
cp -R $MATTER_ROOT/third_party/nlassert $EXT_DIR/third_party/nlassert
cp -R $MATTER_ROOT/third_party/nlio $EXT_DIR/third_party/nlio
cp -R $MATTER_ROOT/third_party/silabs/wiseconnect-wifi-bt-sdk/sapi $EXT_DIR/third_party/silabs/wiseconnect-wifi-bt-sdk/
cp -R $MATTER_ROOT/provision $EXT_DIR

mkdir -p $EXT_DIR/credentials/test/certification-declaration
cp $MATTER_ROOT/credentials/test/certification-declaration/Chip-Test-CD-Signing-Cert.pem $EXT_DIR/credentials/test/certification-declaration/
cp $MATTER_ROOT/credentials/test/certification-declaration/Chip-Test-CD-Signing-Key.pem $EXT_DIR/credentials/test/certification-declaration/

cp -R $MATTER_ROOT/third_party/silabs/matter_support/matter/mbedtls/tinycrypt $EXT_DIR/third_party/silabs/matter_support/matter/mbedtls/
cp -R $MATTER_ROOT/third_party/silabs/matter_support/matter/si91x/siwx917/BRD4338A/support $EXT_DIR/third_party/silabs/matter_support/matter/si91x/siwx917/BRD4338A/
cp -R $MATTER_ROOT/third_party/mbedtls/repo $EXT_DIR/third_party/mbedtls/

# Segger files needed due to GSDK component override within Matter projects
cp -R $GSDK_ROOT/util/third_party/segger/systemview/SEGGER $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/segger/systemview/
cp -R $GSDK_ROOT/util/third_party/segger/systemview/Config $EXT_DIR/third_party/silabs/simplicity_sdk/util/third_party/segger/systemview/

# Copy app source code to extension
mkdir -p $EXT_DIR/examples/lighting-app/silabs/data_model/zap-generated
mkdir -p $EXT_DIR/examples/lighting-app/silabs/include
mkdir -p $EXT_DIR/examples/lighting-app/silabs/src

mkdir -p $EXT_DIR/silabs_examples/onoff-plug-app/onoff-plug-common
mkdir -p $EXT_DIR/silabs_examples/onoff-plug-app/
mkdir -p $EXT_DIR/examples/onoff-plug-app/silabs/src
mkdir -p $EXT_DIR/examples/onoff-plug-app/silabs/include

mkdir -p $EXT_DIR/silabs_examples/dishwasher-app/silabs/data_model
mkdir -p $EXT_DIR/silabs_examples/dishwasher-app/silabs/
mkdir -p $EXT_DIR/silabs_examples/dishwasher-app/silabs/src
mkdir -p $EXT_DIR/silabs_examples/dishwasher-app/silabs/include

mkdir -p $EXT_DIR/silabs_examples/silabs-sensors/data_model

mkdir -p $EXT_DIR/examples/light-switch-app/light-switch-common
mkdir -p $EXT_DIR/examples/light-switch-app/silabs/include
mkdir -p $EXT_DIR/examples/light-switch-app/silabs/src

mkdir -p $EXT_DIR/examples/lock-app/lock-common
mkdir -p $EXT_DIR/examples/lock-app/silabs/include
mkdir -p $EXT_DIR/examples/lock-app/silabs/src

mkdir -p $EXT_DIR/examples/thermostat/thermostat-common
mkdir -p $EXT_DIR/examples/thermostat/silabs/include
mkdir -p $EXT_DIR/examples/thermostat/silabs/src

mkdir -p $EXT_DIR/examples/window-app/common/include
mkdir -p $EXT_DIR/examples/window-app/common/src
mkdir -p $EXT_DIR/examples/window-app/silabs/include
mkdir -p $EXT_DIR/examples/window-app/silabs/src

# Pefromance testing utils
mkdir -p $EXT_DIR/silabs_utils

#DIC
mkdir -p $EXT_DIR/examples/platform/silabs/DIC/matter_abs_interface/include
mkdir -p $EXT_DIR/examples/platform/silabs/DIC/matter_abs_interface/src
mkdir -p $EXT_DIR/third_party/silabs/mqtt/mqtt_transport_interface/include
mkdir -p $EXT_DIR/third_party/silabs/mqtt/mqtt_transport_interface/src
mkdir -p $EXT_DIR/third_party/silabs/mqtt/stack

#DIC Components
cp -R $MATTER_ROOT/examples/platform/silabs/DIC/matter_abs_interface/include $EXT_DIR/examples/platform/silabs/DIC/matter_abs_interface
cp -R $MATTER_ROOT/examples/platform/silabs/DIC/matter_abs_interface/src $EXT_DIR/examples/platform/silabs/DIC/matter_abs_interface
cp -R $MATTER_ROOT/third_party/silabs/mqtt/mqtt_transport_interface/src $EXT_DIR/third_party/silabs/mqtt/mqtt_transport_interface
cp -R $MATTER_ROOT/third_party/silabs/mqtt/mqtt_transport_interface/include $EXT_DIR/third_party/silabs/mqtt/mqtt_transport_interface
cp -R $MATTER_ROOT/third_party/silabs/mqtt/stack $EXT_DIR/third_party/silabs/mqtt


cp $MATTER_ROOT/examples/lighting-app/silabs/data_model/lighting-thread-app.zap $EXT_DIR/examples/lighting-app/silabs/data_model/
cp $MATTER_ROOT/examples/lighting-app/silabs/data_model/lighting-wifi-app.zap $EXT_DIR/examples/lighting-app/silabs/data_model/
cp -R $MATTER_ROOT/examples/lighting-app/silabs/include $EXT_DIR/examples/lighting-app/silabs/
cp -R $MATTER_ROOT/examples/lighting-app/silabs/src $EXT_DIR/examples/lighting-app/silabs/

cp $MATTER_ROOT/silabs_examples/silabs-sensors/data_model/sensor-thread-app.zap $EXT_DIR/silabs_examples/silabs-sensors/data_model/
cp $MATTER_ROOT/silabs_examples/silabs-sensors/data_model/sensor-wifi-app.zap $EXT_DIR/silabs_examples/silabs-sensors/data_model/
cp -R $MATTER_ROOT/silabs_examples/silabs-sensors/include $EXT_DIR/silabs_examples/silabs-sensors/
cp -R $MATTER_ROOT/silabs_examples/silabs-sensors/src $EXT_DIR/silabs_examples/silabs-sensors/

cp -R $MATTER_ROOT/silabs_examples/zigbee-matter-light $EXT_DIR/silabs_examples/

cp $MATTER_ROOT/silabs_examples/onoff-plug-app/onoff-plug-common/onoff-plug-app.zap $EXT_DIR/silabs_examples/onoff-plug-app/onoff-plug-common
cp -R $MATTER_ROOT/silabs_examples/onoff-plug-app/include $EXT_DIR/silabs_examples/onoff-plug-app
cp -R $MATTER_ROOT/silabs_examples/onoff-plug-app/src $EXT_DIR/silabs_examples/onoff-plug-app

cp $MATTER_ROOT/silabs_examples/dishwasher-app/silabs/data_model/dishwasher-thread-app.zap $EXT_DIR/silabs_examples/dishwasher-app/silabs/data_model/
cp $MATTER_ROOT/silabs_examples/dishwasher-app/silabs/data_model/dishwasher-wifi-app.zap $EXT_DIR/silabs_examples/dishwasher-app/silabs/data_model/
cp -R $MATTER_ROOT/silabs_examples/dishwasher-app/silabs/include $EXT_DIR/silabs_examples/dishwasher-app/silabs/
cp -R $MATTER_ROOT/silabs_examples/dishwasher-app/silabs/src $EXT_DIR/silabs_examples/dishwasher-app/silabs/

cp $MATTER_ROOT/examples/light-switch-app/light-switch-common/light-switch-app.zap $EXT_DIR/examples/light-switch-app/light-switch-common/light-switch-app.zap
cp -R $MATTER_ROOT/examples/light-switch-app/silabs/include $EXT_DIR/examples/light-switch-app/silabs
cp -R $MATTER_ROOT/examples/light-switch-app/silabs/src $EXT_DIR/examples/light-switch-app/silabs

cp $MATTER_ROOT/examples/lock-app/lock-common/lock-app.zap $EXT_DIR/examples/lock-app/lock-common/lock-app.zap
cp -R $MATTER_ROOT/examples/lock-app/silabs/include $EXT_DIR/examples/lock-app/silabs
cp -R $MATTER_ROOT/examples/lock-app/silabs/src $EXT_DIR/examples/lock-app/silabs

cp $MATTER_ROOT/examples/thermostat/thermostat-common/thermostat.zap $EXT_DIR/examples/thermostat/thermostat-common/thermostat.zap
cp -R $MATTER_ROOT/examples/thermostat/silabs/include $EXT_DIR/examples/thermostat/silabs
cp -R $MATTER_ROOT/examples/thermostat/silabs/src $EXT_DIR/examples/thermostat/silabs

cp $MATTER_ROOT/examples/window-app/common/window-app.zap $EXT_DIR/examples/window-app/common/window-app.zap
cp -R $MATTER_ROOT/examples/window-app/silabs/include $EXT_DIR/examples/window-app/silabs
cp -R $MATTER_ROOT/examples/window-app/silabs/src $EXT_DIR/examples/window-app/silabs
cp -R $MATTER_ROOT/examples/window-app/common/include $EXT_DIR/examples/window-app/common
cp -R $MATTER_ROOT/examples/window-app/common/src $EXT_DIR/examples/window-app/common

# Performance Testing utils
cp -R $MATTER_ROOT/silabs_utils $EXT_DIR/

#zap script
mkdir -p $EXT_DIR/scripts/tools/zap/
cp $MATTER_ROOT/scripts/tools/zap/run_zaptool.sh $EXT_DIR/scripts/tools/zap/

# DIC_AWS_SDK_OTA
mkdir -p $EXT_DIR/third_party/silabs/aws_ota_sdk
mkdir -p $EXT_DIR/third_party/silabs/aws_ota_sdk/ota-for-aws-iot-embedded-sdk/source
cp -R $MATTER_ROOT/third_party/silabs/aws_ota_sdk/LICENSE $EXT_DIR/third_party/silabs/aws_ota_sdk
cp -R $MATTER_ROOT/third_party/silabs/aws_ota_sdk/demos  $EXT_DIR/third_party/silabs/aws_ota_sdk
cp -R $MATTER_ROOT/third_party/silabs/aws_ota_sdk/ota-for-aws-iot-embedded-sdk/source $EXT_DIR/third_party/silabs/aws_ota_sdk/ota-for-aws-iot-embedded-sdk

# Matter SLC component framework files
cp $MATTER_ROOT/matter.slce $EXT_DIR
cp $MATTER_ROOT/matter.slsdk $EXT_DIR
cp $MATTER_ROOT/upgrade.slcu $EXT_DIR
cp $MATTER_ROOT/matter_templates.xml $EXT_DIR
cp $MATTER_ROOT/matter_docs.xml $EXT_DIR
cp $MATTER_ROOT/matter_demos.xml $EXT_DIR
cp $MATTER_ROOT/provision.mattpconf $EXT_DIR
cp $MATTER_ROOT/slc/EXTENSION_README.md $EXT_DIR/README.md

# Files required for WF200 fmac driver
cp $GSDK_ROOT/platform/radio/wifi/wfx_fmac_driver/bus/sl_wfx_bus.h  $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/bus/
cp $GSDK_ROOT/platform/radio/wifi/wfx_fmac_driver/bus/sl_wfx_bus_spi.c  $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/bus/
cp $GSDK_ROOT/platform/radio/wifi/wfx_fmac_driver/bus/sl_wfx_bus.c  $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/bus/
cp -R $GSDK_ROOT/platform/radio/wifi/wfx_fmac_driver/config/brd2204a/  $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/config/
cp $GSDK_ROOT/platform/radio/wifi/wfx_fmac_driver/config/sl_wfx*  $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/config/
cp -R $GSDK_ROOT/platform/radio/wifi/wfx_fmac_driver/firmware  $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/
cp -R $GSDK_ROOT/platform/radio/wifi/wfx_fmac_driver/pds $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/
cp $GSDK_ROOT/platform/radio/wifi/wfx_fmac_driver/secure_link/sl_wfx_secure_link*  $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/secure_link/
cp $GSDK_ROOT/platform/radio/wifi/wfx_fmac_driver/sl_wfx* $EXT_DIR/third_party/silabs/simplicity_sdk/platform/radio/wifi/wfx_fmac_driver/

# SPI related files for 917 NCP
mkdir -p $EXT_DIR/third_party/silabs/wifi_sdk/components/device/silabs/si91x/wireless/host_mcu/efx32/
mkdir -p $EXT_DIR/third_party/silabs/wifi_sdk/components/device/silabs/si91x/wireless/spi_interface/

cp $WIFI_SDK_ROOT/components/device/silabs/si91x/wireless/host_mcu/efx32/efx32_ncp_host.c $EXT_DIR/third_party/silabs/wifi_sdk/components/device/silabs/si91x/wireless/host_mcu/efx32/

# Remove unnecessary directories
rm -fr $EXT_DIR/src/test_driver/
rm -fr $EXT_DIR/slc/copy-app.sh
rm -fr $EXT_DIR/slc/copy-extension.sh
rm -fr $EXT_DIR/slc/build.sh
rm -fr $EXT_DIR/slc/README.md
rm -fr $EXT_DIR/slc/script/
rm -fr $EXT_DIR/slc/EXTENSION_README.md

echo "Matter extension code copied to $DEST_DIR"

exit 0
