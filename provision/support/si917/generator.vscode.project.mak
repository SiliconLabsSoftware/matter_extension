####################################################################
# Automatically-generated file. Do not edit!                       #
# Makefile Version 15                                              #
####################################################################

BASE_SDK_PATH = /Volumes/Resources/git/matter/stash/third_party/silabs/gecko_sdk
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
 '-DSL_BOARD_NAME="BRD4002A"' \
 '-DSL_BOARD_REV="A06"' \
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
 '-DFLASH_PAGE_SIZE=1' \
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
 '-DSL_BOARD_NAME="BRD4002A"' \
 '-DSL_BOARD_REV="A06"' \
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
 '-DFLASH_PAGE_SIZE=1' \
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

$(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/startup_si91x.o: $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/startup_si91x.c
	@$(POSIX_TOOL_PATH)echo 'Building $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/startup_si91x.c'
	@$(POSIX_TOOL_PATH)mkdir -p $(@D)
	$(ECHO)$(CC) $(CFLAGS) -c -o $@ $(SDK_PATH)/../../../../../stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/startup_si91x.c
CDEPS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/startup_si91x.d
OBJS += $(OUTPUT_DIR)/sdk/_/_/_/_/_/stash/wifi_sdk/components/device/silabs/si91x/mcu/core/chip/src/startup_si91x.o

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

# Automatically-generated Simplicity Studio Metadata
# Please do not edit or delete these lines!
# SIMPLICITY_STUDIO_METADATA=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=END_SIMPLICITY_STUDIO_METADATA
# END OF METADATA