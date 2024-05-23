####################################################################
# Automatically-generated file. Do not edit!                       #
# Makefile Version 15                                              #
####################################################################

BASE_SDK_PATH ?= /git/gsdk
UNAME:=$(shell $(POSIX_TOOL_PATH)uname -s | $(POSIX_TOOL_PATH)sed -e 's/^\(CYGWIN\).*/\1/' | $(POSIX_TOOL_PATH)sed -e 's/^\(MINGW\).*/\1/')
ifeq ($(UNAME),MINGW)
# Translate "C:/super" into "/C/super" for MinGW make.
SDK_PATH := /$(shell $(POSIX_TOOL_PATH)echo $(BASE_SDK_PATH) | sed s/://)
endif
SDK_PATH ?= $(BASE_SDK_PATH)
COPIED_SDK_PATH ?= gecko_sdk_4.4.3

# This uses the explicit build rules below
PROJECT_SOURCE_FILES =

C_SOURCE_FILES   += $(filter %.c, $(PROJECT_SOURCE_FILES))
CXX_SOURCE_FILES += $(filter %.cpp, $(PROJECT_SOURCE_FILES))
CXX_SOURCE_FILES += $(filter %.cc, $(PROJECT_SOURCE_FILES))
ASM_SOURCE_FILES += $(filter %.s, $(PROJECT_SOURCE_FILES))
ASM_SOURCE_FILES += $(filter %.S, $(PROJECT_SOURCE_FILES))
LIB_FILES        += $(filter %.a, $(PROJECT_SOURCE_FILES))

C_DEFS += \
 '-DCHIP_SYSTEM_CONFIG_USE_SOCKETS=1' \
 '-DDEBUG_EFM=1' \
 '-DMBEDTLS_CONFIG_FILE="siwx917-chip-tinycrypt-config.h"' \
 '-DNVM3_LOCK_OVERRIDE=1' \
 '-DOPTIMIZE_TINYCRYPT_ASM=1' \
 '-DSILABS_PROVISION_PROTOCOL_V1=0' \
 '-DSL_MBEDTLS_USE_TINYCRYPT=1' \
 '-DSL_PROVISION_CHANNEL_ENABLED=1' \
 '-DSL_PROVISION_GENERATOR=1' \
 '-DTINYCRYPT_PRIMITIVES=1' \
 '-DSIWG917M111MGTBA=1' \
 '-DSLI_SI917=1' \
 '-DSLI_SI917B0=1' \
 '-DSLI_SI91X_MCU_ENABLE_FLASH_BASED_EXECUTION=1' \
 '-DSLI_SI91X_MCU_COMMON_FLASH_MODE=1' \
 '-DSLI_SI91X_MCU_CONFIG_RADIO_BOARD_BASE_VER=1' \
 '-DSLI_SI91X_MCU_CONFIG_RADIO_BOARD_VER2=1' \
 '-DSL_BOARD_NAME="BRD4338A"' \
 '-DSL_BOARD_REV="A02"' \
 '-DSL_NET_COMPONENT_INCLUDED=1' \
 '-D__STATIC_INLINE=static inline' \
 '-DSL_SI91X_BOARD_INIT=1' \
 '-DSRAM_BASE=0x0cUL' \
 '-DSRAM_SIZE=0x2fc00UL' \
 '-DSLI_SI91X_MCU_ENABLE_IPMU_APIS=1' \
 '-DSL_SI91X_SI917_RAM_MEM_CONFIG=1' \
 '-DDEBUG_ENABLE=1' \
 '-DDEBUG_UART=1' \
 '-DENABLE_DEBUG_MODULE=1' \
 '-DFLASH_PAGE_SIZE=4096' \
 '-DSLI_SI91X_OFFLOAD_NETWORK_STACK=1' \
 '-DSI917=1' \
 '-DSLI_SI91X_ENABLE_OS=1' \
 '-DSLI_SI91X_MCU_INTERFACE=1' \
 '-DTA_DEEP_SLEEP_COMMON_FLASH=1' \
 '-DSI91X_PLATFORM=1' \
 '-DSI91X_SYSRTC_PRESENT=1' \
 '-DSL_SLEEP_TIMER=1' \
 '-D__WEAK=__attribute__((weak))' \
 '-DSL_WIFI_COMPONENT_INCLUDED=1' \
 '-DconfigNUM_SDK_THREAD_LOCAL_STORAGE_POINTERS=2' \
 '-DSL_COMPONENT_CATALOG_PRESENT=1' \
 '-DRTT_USE_ASM=0' \
 '-DSEGGER_RTT_SECTION="SEGGER_RTT"'

ASM_DEFS += \
 '-DCHIP_SYSTEM_CONFIG_USE_SOCKETS=1' \
 '-DDEBUG_EFM=1' \
 '-DMBEDTLS_CONFIG_FILE="siwx917-chip-tinycrypt-config.h"' \
 '-DNVM3_LOCK_OVERRIDE=1' \
 '-DOPTIMIZE_TINYCRYPT_ASM=1' \
 '-DSILABS_PROVISION_PROTOCOL_V1=0' \
 '-DSL_MBEDTLS_USE_TINYCRYPT=1' \
 '-DSL_PROVISION_CHANNEL_ENABLED=1' \
 '-DSL_PROVISION_GENERATOR=1' \
 '-DTINYCRYPT_PRIMITIVES=1' \
 '-DSIWG917M111MGTBA=1' \
 '-DSLI_SI917=1' \
 '-DSLI_SI917B0=1' \
 '-DSLI_SI91X_MCU_ENABLE_FLASH_BASED_EXECUTION=1' \
 '-DSLI_SI91X_MCU_COMMON_FLASH_MODE=1' \
 '-DSLI_SI91X_MCU_CONFIG_RADIO_BOARD_BASE_VER=1' \
 '-DSLI_SI91X_MCU_CONFIG_RADIO_BOARD_VER2=1' \
 '-DSL_BOARD_NAME="BRD4338A"' \
 '-DSL_BOARD_REV="A02"' \
 '-DSL_NET_COMPONENT_INCLUDED=1' \
 '-D__STATIC_INLINE=static inline' \
 '-DSL_SI91X_BOARD_INIT=1' \
 '-DSRAM_BASE=0x0cUL' \
 '-DSRAM_SIZE=0x2fc00UL' \
 '-DSLI_SI91X_MCU_ENABLE_IPMU_APIS=1' \
 '-DSL_SI91X_SI917_RAM_MEM_CONFIG=1' \
 '-DDEBUG_ENABLE=1' \
 '-DDEBUG_UART=1' \
 '-DENABLE_DEBUG_MODULE=1' \
 '-DFLASH_PAGE_SIZE=4096' \
 '-DSLI_SI91X_OFFLOAD_NETWORK_STACK=1' \
 '-DSI917=1' \
 '-DSLI_SI91X_ENABLE_OS=1' \
 '-DSLI_SI91X_MCU_INTERFACE=1' \
 '-DTA_DEEP_SLEEP_COMMON_FLASH=1' \
 '-DSI91X_PLATFORM=1' \
 '-DSI91X_SYSRTC_PRESENT=1' \
 '-DSL_SLEEP_TIMER=1' \
 '-D__WEAK=__attribute__((weak))' \
 '-DSL_WIFI_COMPONENT_INCLUDED=1' \
 '-DconfigNUM_SDK_THREAD_LOCAL_STORAGE_POINTERS=2' \
 '-DSL_COMPONENT_CATALOG_PRESENT=1' \
 '-DRTT_USE_ASM=0' \
 '-DSEGGER_RTT_SECTION="SEGGER_RTT"'

INCLUDES += \
 -Iconfig \
 -Iautogen \
 -I../../generator \
 -I$(SDK_PATH)/../../../examples \
 -I$(SDK_PATH)/../../../examples/platform/silabs \
 -I$(SDK_PATH)/../../../src \
 -I$(SDK_PATH)/../../../src/platform/silabs/SiWx917 \
 -I$(SDK_PATH)/../../../src/include \
 -I$(SDK_PATH)/../../../zzz_generated/app-common \
 -I$(SDK_PATH)/../../nlassert/repo/include \
 -I$(SDK_PATH)/../../nlio/repo/include \
 -I$(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/inc \
 -I$(SDK_PATH)/../../mbedtls/repo/library \
 -I$(SDK_PATH)/../../mbedtls/repo/include \
 -I$(SDK_PATH)/../../../src/lib/support \
 -I$(SDK_PATH)/../../../src/platform/silabs \
 -I$(SDK_PATH)/../matter_support/matter/si91x/siwx917/BRD4338A/support/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/bsd_socket/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/CMSIS/Driver/Include \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/config \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/rom_driver/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/board/silabs/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/config \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_api/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_peripheral_drivers/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/button/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/errno/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/icmp \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/firmware_upgrade \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/led/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/sleeptimer/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/protocol/wifi/inc \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/resources/certificates \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/resources/html \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/resources/other \
 -I$(SDK_PATH)/../../../../../stash/wifi_sdk/components/common/inc \
 -I$(SDK_PATH)/platform/common/inc \
 -I$(SDK_PATH)/platform/CMSIS/Core/Include \
 -I$(SDK_PATH)/platform/CMSIS/RTOS2/Include \
 -I$(SDK_PATH)/platform/service/device_init/inc \
 -I$(SDK_PATH)/platform/emdrv/common/inc \
 -I$(SDK_PATH)/platform/emlib/inc \
 -I$(SDK_PATH)/util/third_party/freertos/cmsis/Include \
 -I$(SDK_PATH)/util/third_party/freertos/kernel/include \
 -I$(SDK_PATH)/util/third_party/freertos/kernel/portable/GCC/ARM_CM4F \
 -I$(SDK_PATH)/platform/service/iostream/inc \
 -I$(SDK_PATH)/platform/emdrv/nvm3/inc \
 -I$(SDK_PATH)/util/third_party/segger/systemview/SEGGER \
 -I$(SDK_PATH)/platform/service/system/inc \
 -I$(SDK_PATH)/platform/service/sleeptimer/inc

GROUP_START =-Wl,--start-group
GROUP_END =-Wl,--end-group

PROJECT_LIBS = \
 -lgcc \
 -lnosys \
 -lstdc++ \
 -lc \
 -lm \
 $(SDK_PATH)/platform/emdrv/nvm3/lib/libnvm3_CM4_gcc.a

LIBS += $(GROUP_START) $(PROJECT_LIBS) $(GROUP_END)

LIB_FILES += $(filter %.a, $(PROJECT_LIBS))

C_FLAGS += \
 -mcpu=cortex-m4 \
 -mthumb \
 -mfpu=fpv4-sp-d16 \
 -mfloat-abi=softfp \
 -std=c99 \
 -Wall \
 -Wextra \
 -Og \
 -fdata-sections \
 -ffunction-sections \
 -fomit-frame-pointer \
 -Wno-unused-parameter \
 -mcpu=cortex-m4 \
 --specs=nano.specs \
 -g

CXX_FLAGS += \
 -mcpu=cortex-m4 \
 -mthumb \
 -mfpu=fpv4-sp-d16 \
 -mfloat-abi=softfp \
 -std=c++17 \
 -fno-rtti \
 -fno-exceptions \
 -Wall \
 -Wextra \
 -Og \
 -fdata-sections \
 -ffunction-sections \
 -fomit-frame-pointer \
 -Wno-unused-parameter \
 -mcpu=cortex-m4 \
 --specs=nano.specs \
 -g

ASM_FLAGS += \
 -mcpu=cortex-m4 \
 -mthumb \
 -mfpu=fpv4-sp-d16 \
 -mfloat-abi=softfp \
 -x assembler-with-cpp

LD_FLAGS += \
 -mcpu=cortex-m4 \
 -mthumb \
 -mfpu=fpv4-sp-d16 \
 -mfloat-abi=softfp \
 -T"autogen/linkerfile_SoC.ld" \
 --specs=nano.specs \
 -Xlinker -Map=$(OUTPUT_DIR)/$(PROJECTNAME).map \
 -u _printf_float \
 -Wl,--gc-sections \
 -Wl,--no-warn-rwx-segments


####################################################################
# Pre/Post Build Rules                                             #
####################################################################
pre-build:
	# No pre-build defined

post-build: $(OUTPUT_DIR)/$(PROJECTNAME).out
	# No post-build defined

####################################################################
# SDK Build Rules                                                  #
####################################################################
$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/board/silabs/src/rsi_board.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/board/silabs/src/rsi_board.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/board/silabs/src/rsi_board.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/board/silabs/src/rsi_board.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/board/silabs/src/rsi_board.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/board/silabs/src/rsi_board.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/common/src/sl_utility.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/common/src/sl_utility.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/common/src/sl_utility.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/common/src/sl_utility.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/common/src/sl_utility.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/common/src/sl_utility.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/ipmu_apis.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/ipmu_apis.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/ipmu_apis.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/ipmu_apis.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/ipmu_apis.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/ipmu_apis.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/rsi_system_config_917.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/rsi_system_config_917.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/rsi_system_config_917.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/rsi_system_config_917.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/rsi_system_config_917.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/iPMU_prog/iPMU_dotc/rsi_system_config_917.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/rsi_deepsleep_soc.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/rsi_deepsleep_soc.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/rsi_deepsleep_soc.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/rsi_deepsleep_soc.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/rsi_deepsleep_soc.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/rsi_deepsleep_soc.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/rsi_ps_ram_func.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/rsi_ps_ram_func.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/rsi_ps_ram_func.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/rsi_ps_ram_func.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/rsi_ps_ram_func.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/rsi_ps_ram_func.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/system_si91x.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/system_si91x.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/system_si91x.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/system_si91x.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/system_si91x.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/system_si91x.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/src/rsi_debug.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/src/rsi_debug.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/src/rsi_debug.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/src/rsi_debug.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/src/rsi_debug.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/src/rsi_debug.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/src/sl_si91x_stack_object_declare.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/src/sl_si91x_stack_object_declare.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/src/sl_si91x_stack_object_declare.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/src/sl_si91x_stack_object_declare.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/src/sl_si91x_stack_object_declare.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/common/src/sl_si91x_stack_object_declare.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/config/src/rsi_nvic_priorities_config.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/config/src/rsi_nvic_priorities_config.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/config/src/rsi_nvic_priorities_config.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/config/src/rsi_nvic_priorities_config.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/config/src/rsi_nvic_priorities_config.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/config/src/rsi_nvic_priorities_config.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/UDMA.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/UDMA.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/UDMA.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/UDMA.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/UDMA.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/UDMA.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/USART.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/USART.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/USART.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/USART.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/USART.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/cmsis_driver/USART.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/button/src/sl_si91x_button.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/button/src/sl_si91x_button.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/button/src/sl_si91x_button.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/button/src/sl_si91x_button.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/button/src/sl_si91x_button.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/button/src/sl_si91x_button.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/led/src/sl_si91x_led.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/led/src/sl_si91x_led.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/led/src/sl_si91x_led.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/led/src/sl_si91x_led.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/led/src/sl_si91x_led.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/hardware_drivers/led/src/sl_si91x_led.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/clock_update.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/clock_update.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/clock_update.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/clock_update.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/clock_update.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/clock_update.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_crc.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_crc.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_crc.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_crc.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_crc.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_crc.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_egpio.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_egpio.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_egpio.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_egpio.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_egpio.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_egpio.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_sysrtc.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_sysrtc.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_sysrtc.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_sysrtc.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_sysrtc.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_sysrtc.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_timers.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_timers.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_timers.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_timers.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_timers.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_timers.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma_wrapper.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma_wrapper.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma_wrapper.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma_wrapper.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma_wrapper.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_udma_wrapper.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_usart.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_usart.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_usart.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_usart.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_usart.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/peripheral_drivers/src/rsi_usart.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/src/sl_si91x_common_flash_intf.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/src/sl_si91x_common_flash_intf.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/src/sl_si91x_common_flash_intf.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/src/sl_si91x_common_flash_intf.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/src/sl_si91x_common_flash_intf.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/src/sl_si91x_common_flash_intf.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/src/sl_si91x_nvm3_hal_flash.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/src/sl_si91x_nvm3_hal_flash.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/src/sl_si91x_nvm3_hal_flash.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/src/sl_si91x_nvm3_hal_flash.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/src/sl_si91x_nvm3_hal_flash.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/nvm3/src/sl_si91x_nvm3_hal_flash.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/sleeptimer/src/sl_sleeptimer_hal_si91x_sysrtc.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/sleeptimer/src/sl_sleeptimer_hal_si91x_sysrtc.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/sleeptimer/src/sl_sleeptimer_hal_si91x_sysrtc.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/sleeptimer/src/sl_sleeptimer_hal_si91x_sysrtc.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/sleeptimer/src/sl_sleeptimer_hal_si91x_sysrtc.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/service/sleeptimer/src/sl_sleeptimer_hal_si91x_sysrtc.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ipmu.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ipmu.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ipmu.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ipmu.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ipmu.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ipmu.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_pll.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_pll.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_pll.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_pll.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_pll.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_pll.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_power_save.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_power_save.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_power_save.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_power_save.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_power_save.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_power_save.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_rtc.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_rtc.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_rtc.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_rtc.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_rtc.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_rtc.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_temp_sensor.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_temp_sensor.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_temp_sensor.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_temp_sensor.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_temp_sensor.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_temp_sensor.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_time_period.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_time_period.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_time_period.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_time_period.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_time_period.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_time_period.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ulpss_clk.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ulpss_clk.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ulpss_clk.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ulpss_clk.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ulpss_clk.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_ulpss_clk.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_wwdt.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_wwdt.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_wwdt.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_wwdt.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_wwdt.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/systemlevel/src/rsi_wwdt.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_api/src/sl_si91x_driver_gpio.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_api/src/sl_si91x_driver_gpio.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_api/src/sl_si91x_driver_gpio.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_api/src/sl_si91x_driver_gpio.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_api/src/sl_si91x_driver_gpio.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_api/src/sl_si91x_driver_gpio.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_peripheral_drivers/src/sl_si91x_peripheral_gpio.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_peripheral_drivers/src/sl_si91x_peripheral_gpio.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_peripheral_drivers/src/sl_si91x_peripheral_gpio.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_peripheral_drivers/src/sl_si91x_peripheral_gpio.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_peripheral_drivers/src/sl_si91x_peripheral_gpio.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/drivers/unified_peripheral_drivers/src/sl_si91x_peripheral_gpio.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_ram.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_ram.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_ram.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_ram.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_ram.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_ram.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_rom.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_rom.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_rom.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_rom.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_rom.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/rsi_hal_mcu_m4_rom.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform_wireless.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform_wireless.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform_wireless.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform_wireless.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform_wireless.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_platform_wireless.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_bus.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_bus.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_bus.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_bus.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_bus.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_bus.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_timer.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_timer.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_timer.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_timer.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_timer.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sl_si91x_timer.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sli_siwx917_soc.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sli_siwx917_soc.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sli_siwx917_soc.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sli_siwx917_soc.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sli_siwx917_soc.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/ahb_interface/src/sli_siwx917_soc.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/errno/src/sl_si91x_errno.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/errno/src/sl_si91x_errno.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/errno/src/sl_si91x_errno.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/errno/src/sl_si91x_errno.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/errno/src/sl_si91x_errno.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/errno/src/sl_si91x_errno.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/firmware_upgrade/firmware_upgradation.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/firmware_upgrade/firmware_upgradation.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/firmware_upgrade/firmware_upgradation.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/firmware_upgrade/firmware_upgradation.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/firmware_upgrade/firmware_upgradation.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/firmware_upgrade/firmware_upgradation.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/host_mcu/si91x/siwx917_soc_ncp_host.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/host_mcu/si91x/siwx917_soc_ncp_host.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/host_mcu/si91x/siwx917_soc_ncp_host.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/host_mcu/si91x/siwx917_soc_ncp_host.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/host_mcu/si91x/siwx917_soc_ncp_host.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/host_mcu/si91x/siwx917_soc_ncp_host.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/icmp/sl_net_ping.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/icmp/sl_net_ping.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/icmp/sl_net_ping.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/icmp/sl_net_ping.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/icmp/sl_net_ping.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/icmp/sl_net_ping.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/memory/malloc_buffers.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/memory/malloc_buffers.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/memory/malloc_buffers.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/memory/malloc_buffers.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/memory/malloc_buffers.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/memory/malloc_buffers.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_net_rsi_utility.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_net_rsi_utility.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_net_rsi_utility.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_net_rsi_utility.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_net_rsi_utility.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_net_rsi_utility.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_net_si91x_integration_handler.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_net_si91x_integration_handler.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_net_si91x_integration_handler.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_net_si91x_integration_handler.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_net_si91x_integration_handler.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_net_si91x_integration_handler.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_credentials.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_credentials.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_credentials.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_credentials.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_credentials.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_credentials.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_internal_stack.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_internal_stack.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_internal_stack.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_internal_stack.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_internal_stack.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/sl_net/src/sl_si91x_net_internal_stack.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_rsi_utility.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_rsi_utility.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_rsi_utility.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_rsi_utility.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_rsi_utility.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_rsi_utility.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_si91x_callback_framework.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_si91x_callback_framework.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_si91x_callback_framework.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_si91x_callback_framework.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_si91x_callback_framework.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_si91x_callback_framework.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_si91x_driver.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_si91x_driver.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_si91x_driver.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_si91x_driver.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_si91x_driver.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/src/sl_si91x_driver.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/threading/sli_si91x_multithreaded.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/threading/sli_si91x_multithreaded.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/threading/sli_si91x_multithreaded.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/wireless/threading/sli_si91x_multithreaded.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/threading/sli_si91x_multithreaded.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/wireless/threading/sli_si91x_multithreaded.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/protocol/wifi/si91x/sl_wifi.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/protocol/wifi/si91x/sl_wifi.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/protocol/wifi/si91x/sl_wifi.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/protocol/wifi/si91x/sl_wifi.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/protocol/wifi/si91x/sl_wifi.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/protocol/wifi/si91x/sl_wifi.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/protocol/wifi/src/sl_wifi_callback_framework.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/protocol/wifi/src/sl_wifi_callback_framework.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/protocol/wifi/src/sl_wifi_callback_framework.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/protocol/wifi/src/sl_wifi_callback_framework.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/protocol/wifi/src/sl_wifi_callback_framework.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/protocol/wifi/src/sl_wifi_callback_framework.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/si91x/sl_net_si91x.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/si91x/sl_net_si91x.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/si91x/sl_net_si91x.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/si91x/sl_net_si91x.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/si91x/sl_net_si91x.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/si91x/sl_net_si91x.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/src/sl_net.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/src/sl_net.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/src/sl_net.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/src/sl_net.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/src/sl_net.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/src/sl_net.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_certificate_store.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_certificate_store.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_certificate_store.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_certificate_store.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_certificate_store.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_certificate_store.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_credentials.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_credentials.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_credentials.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_credentials.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_credentials.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_credentials.o

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_profiles.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_profiles.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_profiles.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_profiles.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_profiles.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/service/network_manager/src/sl_net_basic_profiles.o

$(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/AttestationKeyMbed.o: $(SDK_PATH)/../../../examples/platform/silabs/provision/AttestationKeyMbed.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../examples/platform/silabs/provision/AttestationKeyMbed.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../examples/platform/silabs/provision/AttestationKeyMbed.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/AttestationKeyMbed.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/AttestationKeyMbed.o

$(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionChannelRTT.o: $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionChannelRTT.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionChannelRTT.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionChannelRTT.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionChannelRTT.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionChannelRTT.o

$(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionEncoder.o: $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionEncoder.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionEncoder.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionEncoder.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionEncoder.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionEncoder.o

$(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionManager.o: $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionManager.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionManager.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionManager.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionManager.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionManager.o

$(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionProtocolV1.o: $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionProtocolV1.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionProtocolV1.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionProtocolV1.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionProtocolV1.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionProtocolV1.o

$(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionProtocolV2.o: $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionProtocolV2.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionProtocolV2.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionProtocolV2.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionProtocolV2.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionProtocolV2.o

$(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionStorage.o: $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionStorage.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionStorage.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionStorage.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionStorage.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionStorage.o

$(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionStorageCustom.o: $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionStorageCustom.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionStorageCustom.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionStorageCustom.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionStorageCustom.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionStorageCustom.o

$(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionStorageDefault.o: $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionStorageDefault.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionStorageDefault.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../examples/platform/silabs/provision/ProvisionStorageDefault.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionStorageDefault.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/provision/ProvisionStorageDefault.o

$(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/syscalls_stubs.o: $(SDK_PATH)/../../../examples/platform/silabs/syscalls_stubs.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../examples/platform/silabs/syscalls_stubs.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../examples/platform/silabs/syscalls_stubs.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/syscalls_stubs.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/examples/platform/silabs/syscalls_stubs.o

$(OUTPUT_DIR)/sdk/_/_/_/src/lib/support/Base64.o: $(SDK_PATH)/../../../src/lib/support/Base64.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../src/lib/support/Base64.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../src/lib/support/Base64.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/src/lib/support/Base64.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/src/lib/support/Base64.o

$(OUTPUT_DIR)/sdk/_/_/_/src/lib/support/BytesToHex.o: $(SDK_PATH)/../../../src/lib/support/BytesToHex.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../src/lib/support/BytesToHex.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../src/lib/support/BytesToHex.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/src/lib/support/BytesToHex.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/src/lib/support/BytesToHex.o

$(OUTPUT_DIR)/sdk/_/_/_/src/lib/support/logging/TextOnlyLogging.o: $(SDK_PATH)/../../../src/lib/support/logging/TextOnlyLogging.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../src/lib/support/logging/TextOnlyLogging.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../src/lib/support/logging/TextOnlyLogging.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/src/lib/support/logging/TextOnlyLogging.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/src/lib/support/logging/TextOnlyLogging.o

$(OUTPUT_DIR)/sdk/_/_/_/src/platform/silabs/Logging.o: $(SDK_PATH)/../../../src/platform/silabs/Logging.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../src/platform/silabs/Logging.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../src/platform/silabs/Logging.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/src/platform/silabs/Logging.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/src/platform/silabs/Logging.o

$(OUTPUT_DIR)/sdk/_/_/_/src/platform/silabs/SilabsConfig.o: $(SDK_PATH)/../../../src/platform/silabs/SilabsConfig.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../src/platform/silabs/SilabsConfig.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../src/platform/silabs/SilabsConfig.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/src/platform/silabs/SilabsConfig.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/src/platform/silabs/SilabsConfig.o

$(OUTPUT_DIR)/sdk/_/_/_/src/platform/silabs/SiWx917/CHIPCryptoPALTinyCrypt.o: $(SDK_PATH)/../../../src/platform/silabs/SiWx917/CHIPCryptoPALTinyCrypt.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../src/platform/silabs/SiWx917/CHIPCryptoPALTinyCrypt.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../src/platform/silabs/SiWx917/CHIPCryptoPALTinyCrypt.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/src/platform/silabs/SiWx917/CHIPCryptoPALTinyCrypt.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/src/platform/silabs/SiWx917/CHIPCryptoPALTinyCrypt.o

$(OUTPUT_DIR)/sdk/_/_/_/src/setup_payload/Base38Encode.o: $(SDK_PATH)/../../../src/setup_payload/Base38Encode.cpp
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../src/setup_payload/Base38Encode.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ $(SDK_PATH)/../../../src/setup_payload/Base38Encode.cpp
CXXDEPS += $(OUTPUT_DIR)/sdk/_/_/_/src/setup_payload/Base38Encode.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/src/setup_payload/Base38Encode.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/aes.o: $(SDK_PATH)/../../mbedtls/repo/library/aes.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/aes.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/aes.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/aes.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/aes.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/asn1parse.o: $(SDK_PATH)/../../mbedtls/repo/library/asn1parse.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/asn1parse.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/asn1parse.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/asn1parse.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/asn1parse.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/asn1write.o: $(SDK_PATH)/../../mbedtls/repo/library/asn1write.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/asn1write.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/asn1write.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/asn1write.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/asn1write.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/base64.o: $(SDK_PATH)/../../mbedtls/repo/library/base64.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/base64.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/base64.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/base64.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/base64.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/bignum.o: $(SDK_PATH)/../../mbedtls/repo/library/bignum.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/bignum.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/bignum.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/bignum.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/bignum.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ccm.o: $(SDK_PATH)/../../mbedtls/repo/library/ccm.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/ccm.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/ccm.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ccm.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ccm.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/cipher.o: $(SDK_PATH)/../../mbedtls/repo/library/cipher.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/cipher.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/cipher.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/cipher.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/cipher.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/cipher_wrap.o: $(SDK_PATH)/../../mbedtls/repo/library/cipher_wrap.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/cipher_wrap.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/cipher_wrap.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/cipher_wrap.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/cipher_wrap.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/constant_time.o: $(SDK_PATH)/../../mbedtls/repo/library/constant_time.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/constant_time.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/constant_time.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/constant_time.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/constant_time.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ctr_drbg.o: $(SDK_PATH)/../../mbedtls/repo/library/ctr_drbg.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/ctr_drbg.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/ctr_drbg.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ctr_drbg.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ctr_drbg.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ecdh.o: $(SDK_PATH)/../../mbedtls/repo/library/ecdh.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/ecdh.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/ecdh.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ecdh.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ecdh.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ecdsa.o: $(SDK_PATH)/../../mbedtls/repo/library/ecdsa.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/ecdsa.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/ecdsa.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ecdsa.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ecdsa.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ecp.o: $(SDK_PATH)/../../mbedtls/repo/library/ecp.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/ecp.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/ecp.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ecp.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ecp.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ecp_curves.o: $(SDK_PATH)/../../mbedtls/repo/library/ecp_curves.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/ecp_curves.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/ecp_curves.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ecp_curves.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/ecp_curves.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/entropy.o: $(SDK_PATH)/../../mbedtls/repo/library/entropy.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/entropy.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/entropy.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/entropy.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/entropy.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/hkdf.o: $(SDK_PATH)/../../mbedtls/repo/library/hkdf.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/hkdf.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/hkdf.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/hkdf.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/hkdf.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/hmac_drbg.o: $(SDK_PATH)/../../mbedtls/repo/library/hmac_drbg.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/hmac_drbg.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/hmac_drbg.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/hmac_drbg.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/hmac_drbg.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/md.o: $(SDK_PATH)/../../mbedtls/repo/library/md.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/md.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/md.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/md.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/md.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/pem.o: $(SDK_PATH)/../../mbedtls/repo/library/pem.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/pem.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/pem.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/pem.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/pem.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/pkcs5.o: $(SDK_PATH)/../../mbedtls/repo/library/pkcs5.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/pkcs5.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/pkcs5.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/pkcs5.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/pkcs5.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/platform.o: $(SDK_PATH)/../../mbedtls/repo/library/platform.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/platform.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/platform.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/platform.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/platform.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/sha256.o: $(SDK_PATH)/../../mbedtls/repo/library/sha256.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/sha256.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/sha256.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/sha256.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/sha256.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/sha512.o: $(SDK_PATH)/../../mbedtls/repo/library/sha512.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/sha512.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/sha512.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/sha512.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/sha512.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/x509.o: $(SDK_PATH)/../../mbedtls/repo/library/x509.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/x509.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/x509.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/x509.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/x509.o

$(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/x509_create.o: $(SDK_PATH)/../../mbedtls/repo/library/x509_create.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../mbedtls/repo/library/x509_create.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../mbedtls/repo/library/x509_create.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/x509_create.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/mbedtls/repo/library/x509_create.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/ecc.o: $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/ecc.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/ecc.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/ecc.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/ecc.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/ecc.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/ecc_dh.o: $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/ecc_dh.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/ecc_dh.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/ecc_dh.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/ecc_dh.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/ecc_dh.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/ecc_dsa.o: $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/ecc_dsa.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/ecc_dsa.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/ecc_dsa.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/ecc_dsa.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/ecc_dsa.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/error.o: $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/error.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/error.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/error.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/error.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/error.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/oid.o: $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/oid.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/oid.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/oid.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/oid.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/oid.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/pk.o: $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/pk.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/pk.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/pk.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/pk.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/pk.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/pk_wrap.o: $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/pk_wrap.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/pk_wrap.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/pk_wrap.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/pk_wrap.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/pk_wrap.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/pkparse.o: $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/pkparse.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/pkparse.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/pkparse.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/pkparse.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/pkparse.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/pkwrite.o: $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/pkwrite.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/pkwrite.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/pkwrite.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/pkwrite.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/pkwrite.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/platform_util.o: $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/platform_util.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/platform_util.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/platform_util.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/platform_util.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/platform_util.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/x509_crt.o: $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/x509_crt.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/x509_crt.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/x509_crt.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/x509_crt.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/x509_crt.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/x509write_csr.o: $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/x509write_csr.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/x509write_csr.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/mbedtls/tinycrypt/src/x509write_csr.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/x509write_csr.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/mbedtls/tinycrypt/src/x509write_csr.o

$(OUTPUT_DIR)/sdk/_/matter_support/matter/si91x/siwx917/BRD4338A/support/src/startup_common_RS1xxxx.o: $(SDK_PATH)/../matter_support/matter/si91x/siwx917/BRD4338A/support/src/startup_common_RS1xxxx.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../matter_support/matter/si91x/siwx917/BRD4338A/support/src/startup_common_RS1xxxx.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../matter_support/matter/si91x/siwx917/BRD4338A/support/src/startup_common_RS1xxxx.c
CDEPS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/si91x/siwx917/BRD4338A/support/src/startup_common_RS1xxxx.d
OBJS += $(OUTPUT_DIR)/sdk/_/matter_support/matter/si91x/siwx917/BRD4338A/support/src/startup_common_RS1xxxx.o

$(OUTPUT_DIR)/sdk/platform/CMSIS/RTOS2/Source/os_systick.o: $(SDK_PATH)/platform/CMSIS/RTOS2/Source/os_systick.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/CMSIS/RTOS2/Source/os_systick.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/CMSIS/RTOS2/Source/os_systick.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/CMSIS/RTOS2/Source/os_systick.d
OBJS += $(OUTPUT_DIR)/sdk/platform/CMSIS/RTOS2/Source/os_systick.o

$(OUTPUT_DIR)/sdk/platform/common/src/sl_assert.o: $(SDK_PATH)/platform/common/src/sl_assert.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/common/src/sl_assert.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/common/src/sl_assert.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/common/src/sl_assert.d
OBJS += $(OUTPUT_DIR)/sdk/platform/common/src/sl_assert.o

$(OUTPUT_DIR)/sdk/platform/common/src/sl_slist.o: $(SDK_PATH)/platform/common/src/sl_slist.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/common/src/sl_slist.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/common/src/sl_slist.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/common/src/sl_slist.d
OBJS += $(OUTPUT_DIR)/sdk/platform/common/src/sl_slist.o

$(OUTPUT_DIR)/sdk/platform/common/src/sl_string.o: $(SDK_PATH)/platform/common/src/sl_string.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/common/src/sl_string.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/common/src/sl_string.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/common/src/sl_string.d
OBJS += $(OUTPUT_DIR)/sdk/platform/common/src/sl_string.o

$(OUTPUT_DIR)/sdk/platform/common/src/sli_cmsis_os2_ext_task_register.o: $(SDK_PATH)/platform/common/src/sli_cmsis_os2_ext_task_register.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/common/src/sli_cmsis_os2_ext_task_register.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/common/src/sli_cmsis_os2_ext_task_register.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/common/src/sli_cmsis_os2_ext_task_register.d
OBJS += $(OUTPUT_DIR)/sdk/platform/common/src/sli_cmsis_os2_ext_task_register.o

$(OUTPUT_DIR)/sdk/platform/emdrv/nvm3/src/nvm3_default_common_linker.o: $(SDK_PATH)/platform/emdrv/nvm3/src/nvm3_default_common_linker.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/emdrv/nvm3/src/nvm3_default_common_linker.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/emdrv/nvm3/src/nvm3_default_common_linker.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/emdrv/nvm3/src/nvm3_default_common_linker.d
OBJS += $(OUTPUT_DIR)/sdk/platform/emdrv/nvm3/src/nvm3_default_common_linker.o

$(OUTPUT_DIR)/sdk/platform/emdrv/nvm3/src/nvm3_lock.o: $(SDK_PATH)/platform/emdrv/nvm3/src/nvm3_lock.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/emdrv/nvm3/src/nvm3_lock.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/emdrv/nvm3/src/nvm3_lock.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/emdrv/nvm3/src/nvm3_lock.d
OBJS += $(OUTPUT_DIR)/sdk/platform/emdrv/nvm3/src/nvm3_lock.o

$(OUTPUT_DIR)/sdk/platform/emlib/src/em_core.o: $(SDK_PATH)/platform/emlib/src/em_core.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/emlib/src/em_core.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/emlib/src/em_core.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/emlib/src/em_core.d
OBJS += $(OUTPUT_DIR)/sdk/platform/emlib/src/em_core.o

$(OUTPUT_DIR)/sdk/platform/service/device_init/src/sl_device_init_nvic.o: $(SDK_PATH)/platform/service/device_init/src/sl_device_init_nvic.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/service/device_init/src/sl_device_init_nvic.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/service/device_init/src/sl_device_init_nvic.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/service/device_init/src/sl_device_init_nvic.d
OBJS += $(OUTPUT_DIR)/sdk/platform/service/device_init/src/sl_device_init_nvic.o

$(OUTPUT_DIR)/sdk/platform/service/iostream/src/sl_iostream.o: $(SDK_PATH)/platform/service/iostream/src/sl_iostream.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/service/iostream/src/sl_iostream.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/service/iostream/src/sl_iostream.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/service/iostream/src/sl_iostream.d
OBJS += $(OUTPUT_DIR)/sdk/platform/service/iostream/src/sl_iostream.o

$(OUTPUT_DIR)/sdk/platform/service/iostream/src/sl_iostream_rtt.o: $(SDK_PATH)/platform/service/iostream/src/sl_iostream_rtt.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/service/iostream/src/sl_iostream_rtt.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/service/iostream/src/sl_iostream_rtt.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/service/iostream/src/sl_iostream_rtt.d
OBJS += $(OUTPUT_DIR)/sdk/platform/service/iostream/src/sl_iostream_rtt.o

$(OUTPUT_DIR)/sdk/platform/service/sleeptimer/src/sl_sleeptimer.o: $(SDK_PATH)/platform/service/sleeptimer/src/sl_sleeptimer.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/service/sleeptimer/src/sl_sleeptimer.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/service/sleeptimer/src/sl_sleeptimer.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/service/sleeptimer/src/sl_sleeptimer.d
OBJS += $(OUTPUT_DIR)/sdk/platform/service/sleeptimer/src/sl_sleeptimer.o

$(OUTPUT_DIR)/sdk/platform/service/system/src/sl_system_init.o: $(SDK_PATH)/platform/service/system/src/sl_system_init.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/service/system/src/sl_system_init.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/service/system/src/sl_system_init.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/service/system/src/sl_system_init.d
OBJS += $(OUTPUT_DIR)/sdk/platform/service/system/src/sl_system_init.o

$(OUTPUT_DIR)/sdk/platform/service/system/src/sl_system_kernel.o: $(SDK_PATH)/platform/service/system/src/sl_system_kernel.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/platform/service/system/src/sl_system_kernel.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/platform/service/system/src/sl_system_kernel.c
CDEPS += $(OUTPUT_DIR)/sdk/platform/service/system/src/sl_system_kernel.d
OBJS += $(OUTPUT_DIR)/sdk/platform/service/system/src/sl_system_kernel.o

$(OUTPUT_DIR)/sdk/util/third_party/freertos/cmsis/Source/cmsis_os2.o: $(SDK_PATH)/util/third_party/freertos/cmsis/Source/cmsis_os2.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/util/third_party/freertos/cmsis/Source/cmsis_os2.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/util/third_party/freertos/cmsis/Source/cmsis_os2.c
CDEPS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/cmsis/Source/cmsis_os2.d
OBJS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/cmsis/Source/cmsis_os2.o

$(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/croutine.o: $(SDK_PATH)/util/third_party/freertos/kernel/croutine.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/util/third_party/freertos/kernel/croutine.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/util/third_party/freertos/kernel/croutine.c
CDEPS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/croutine.d
OBJS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/croutine.o

$(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/event_groups.o: $(SDK_PATH)/util/third_party/freertos/kernel/event_groups.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/util/third_party/freertos/kernel/event_groups.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/util/third_party/freertos/kernel/event_groups.c
CDEPS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/event_groups.d
OBJS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/event_groups.o

$(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/list.o: $(SDK_PATH)/util/third_party/freertos/kernel/list.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/util/third_party/freertos/kernel/list.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/util/third_party/freertos/kernel/list.c
CDEPS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/list.d
OBJS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/list.o

$(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/portable/GCC/ARM_CM4F/port.o: $(SDK_PATH)/util/third_party/freertos/kernel/portable/GCC/ARM_CM4F/port.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/util/third_party/freertos/kernel/portable/GCC/ARM_CM4F/port.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/util/third_party/freertos/kernel/portable/GCC/ARM_CM4F/port.c
CDEPS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/portable/GCC/ARM_CM4F/port.d
OBJS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/portable/GCC/ARM_CM4F/port.o

$(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/portable/MemMang/heap_4.o: $(SDK_PATH)/util/third_party/freertos/kernel/portable/MemMang/heap_4.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/util/third_party/freertos/kernel/portable/MemMang/heap_4.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/util/third_party/freertos/kernel/portable/MemMang/heap_4.c
CDEPS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/portable/MemMang/heap_4.d
OBJS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/portable/MemMang/heap_4.o

$(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/queue.o: $(SDK_PATH)/util/third_party/freertos/kernel/queue.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/util/third_party/freertos/kernel/queue.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/util/third_party/freertos/kernel/queue.c
CDEPS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/queue.d
OBJS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/queue.o

$(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/stream_buffer.o: $(SDK_PATH)/util/third_party/freertos/kernel/stream_buffer.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/util/third_party/freertos/kernel/stream_buffer.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/util/third_party/freertos/kernel/stream_buffer.c
CDEPS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/stream_buffer.d
OBJS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/stream_buffer.o

$(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/tasks.o: $(SDK_PATH)/util/third_party/freertos/kernel/tasks.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/util/third_party/freertos/kernel/tasks.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/util/third_party/freertos/kernel/tasks.c
CDEPS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/tasks.d
OBJS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/tasks.o

$(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/timers.o: $(SDK_PATH)/util/third_party/freertos/kernel/timers.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/util/third_party/freertos/kernel/timers.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/util/third_party/freertos/kernel/timers.c
CDEPS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/timers.d
OBJS += $(OUTPUT_DIR)/sdk/util/third_party/freertos/kernel/timers.o

$(OUTPUT_DIR)/sdk/util/third_party/segger/systemview/SEGGER/SEGGER_RTT.o: $(SDK_PATH)/util/third_party/segger/systemview/SEGGER/SEGGER_RTT.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/util/third_party/segger/systemview/SEGGER/SEGGER_RTT.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/util/third_party/segger/systemview/SEGGER/SEGGER_RTT.c
CDEPS += $(OUTPUT_DIR)/sdk/util/third_party/segger/systemview/SEGGER/SEGGER_RTT.d
OBJS += $(OUTPUT_DIR)/sdk/util/third_party/segger/systemview/SEGGER/SEGGER_RTT.o

$(OUTPUT_DIR)/project/_/_/generator/app.o: ../../generator/app.cpp
	@$(POSIX_TOOL_PATH)echo 'Building ../../generator/app.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ ../../generator/app.cpp
CXXDEPS += $(OUTPUT_DIR)/project/_/_/generator/app.d
OBJS += $(OUTPUT_DIR)/project/_/_/generator/app.o

$(OUTPUT_DIR)/project/_/_/generator/main.o: ../../generator/main.cpp
	@$(POSIX_TOOL_PATH)echo 'Building ../../generator/main.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ ../../generator/main.cpp
CXXDEPS += $(OUTPUT_DIR)/project/_/_/generator/main.d
OBJS += $(OUTPUT_DIR)/project/_/_/generator/main.o

$(OUTPUT_DIR)/project/_/_/generator/si917.o: ../../generator/si917.cpp
	@$(POSIX_TOOL_PATH)echo 'Building ../../generator/si917.cpp'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CXX) $(CXXFLAGS) -c -o $@ ../../generator/si917.cpp
CXXDEPS += $(OUTPUT_DIR)/project/_/_/generator/si917.d
OBJS += $(OUTPUT_DIR)/project/_/_/generator/si917.o

$(OUTPUT_DIR)/project/autogen/sl_event_handler.o: autogen/sl_event_handler.c
	@$(POSIX_TOOL_PATH)echo 'Building autogen/sl_event_handler.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ autogen/sl_event_handler.c
CDEPS += $(OUTPUT_DIR)/project/autogen/sl_event_handler.d
OBJS += $(OUTPUT_DIR)/project/autogen/sl_event_handler.o

$(OUTPUT_DIR)/project/autogen/sl_iostream_handles.o: autogen/sl_iostream_handles.c
	@$(POSIX_TOOL_PATH)echo 'Building autogen/sl_iostream_handles.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ autogen/sl_iostream_handles.c
CDEPS += $(OUTPUT_DIR)/project/autogen/sl_iostream_handles.d
OBJS += $(OUTPUT_DIR)/project/autogen/sl_iostream_handles.o

$(OUTPUT_DIR)/project/autogen/sl_si91x_button_instances.o: autogen/sl_si91x_button_instances.c
	@$(POSIX_TOOL_PATH)echo 'Building autogen/sl_si91x_button_instances.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ autogen/sl_si91x_button_instances.c
CDEPS += $(OUTPUT_DIR)/project/autogen/sl_si91x_button_instances.d
OBJS += $(OUTPUT_DIR)/project/autogen/sl_si91x_button_instances.o

$(OUTPUT_DIR)/project/autogen/sl_si91x_led_instances.o: autogen/sl_si91x_led_instances.c
	@$(POSIX_TOOL_PATH)echo 'Building autogen/sl_si91x_led_instances.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ autogen/sl_si91x_led_instances.c
CDEPS += $(OUTPUT_DIR)/project/autogen/sl_si91x_led_instances.d
OBJS += $(OUTPUT_DIR)/project/autogen/sl_si91x_led_instances.o

# Automatically-generated Simplicity Studio Metadata
# Please do not edit or delete these lines!
# SIMPLICITY_STUDIO_METADATA=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END_SIMPLICITY_STUDIO_METADATA
# END OF METADATA