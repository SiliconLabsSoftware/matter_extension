####################################################################
# Automatically-generated file. Do not edit!                       #
# Makefile Version 19                                              #
####################################################################

BASE_SDK_PATH = /home/chbansal/Development/bleeding_edge_latest/matter_extension/third_party/simplicity_sdk
BASE_PKG_PATH = /home/chbansal/.silabs/slt/installs
UNAME:=$(shell $(POSIX_TOOL_PATH)uname -s | $(POSIX_TOOL_PATH)sed -e 's/^\(CYGWIN\).*/\1/' | $(POSIX_TOOL_PATH)sed -e 's/^\(MINGW\).*/\1/')
ifeq ($(UNAME),MINGW)
# Translate "C:/super" into "/C/super" for MinGW make.
SDK_PATH := /$(shell $(POSIX_TOOL_PATH)echo $(BASE_SDK_PATH) | sed s/://)
PKG_PATH := /$(shell $(POSIX_TOOL_PATH)echo $(BASE_PKG_PATH) | sed s/://)
endif
SDK_PATH ?= $(BASE_SDK_PATH)
PKG_PATH ?= $(BASE_PKG_PATH)
COPIED_SDK_PATH ?= 

# This uses the explicit build rules below
PROJECT_SOURCE_FILES =

C_SOURCE_FILES   += $(filter %.c, $(PROJECT_SOURCE_FILES))
CXX_SOURCE_FILES += $(filter %.cpp, $(PROJECT_SOURCE_FILES))
CXX_SOURCE_FILES += $(filter %.cc, $(PROJECT_SOURCE_FILES))
ASM_SOURCE_FILES += $(filter %.s, $(PROJECT_SOURCE_FILES))
ASM_SOURCE_FILES += $(filter %.S, $(PROJECT_SOURCE_FILES))
LIB_FILES        += $(filter %.a, $(PROJECT_SOURCE_FILES))

C_DEFS += \

ASM_DEFS += \

INCLUDES += \

GROUP_START =-Wl,--start-group
GROUP_END =-Wl,--end-group

PROJECT_LIBS = \

LIBS += $(GROUP_START) $(PROJECT_LIBS) $(GROUP_END)

LIB_FILES += $(filter %.a, $(PROJECT_LIBS))

C_FLAGS += \

CXX_FLAGS += \

ASM_FLAGS += \

LD_FLAGS += \


####################################################################
# Pre/Post Build Rules                                             #
####################################################################
pre-build:
	# No pre-build defined

post-build: $(OUTPUT_DIR)/$(PROJECTNAME).out
ifeq ($(POST_BUILD_EXE),)
		$(error POST_BUILD_EXE is not defined. Post-Build cannot run. Please set the STUDIO_ADAPTER_PACK_PATH to the post-build tool when generating or override the variable for this makefile)
endif
	@$(POSIX_TOOL_PATH)echo 'Running Project Post-Build'
	$(ECHO) @"$(POST_BUILD_EXE)" postbuild "./matter_bootloader_internal_series_3.slpb" --parameter build_dir:"$(OUTPUT_DIR)"

####################################################################
# SDK Build Rules                                                  #
####################################################################
# Automatically-generated Simplicity Studio Metadata
# Please do not edit or delete these lines!
# SIMPLICITY_STUDIO_METADATA=eJzNVg1v2jgY/isomqb1VOIAg7Y5ynRXmMQJDkTodKdliozjgq+OndlO2wnx3/faCV9rd2p1N2lSldqP/X4/72vWXjQcT0fDq+H87ySaX/eHk2TaH0de6HXfPWQ8jmt3VGkmxWXsNfwg9gChgsiUiSVA1/P39fPYe9eL41h0cyX/ocTAFYEzCscF8TOZFpz6mpoi969klkkxLa9NpTa/F4ynfoaNoSpZSGm4xCksmQBAYJ5oqhjVSctfEuKMg42cKvMlIvAfTGxtes4FuAB/3RvG6d6L56jXPF84/QvwyDAbrlEFddCSCqqwoekORIfGcojDSqWRoXnv1RsCQWIBZk6su9tDWL/+XEjz66s3lcsnaLf8Exw9cT6Ud+ByvZ5jBTA4WnmVJilT4VaJQwA4KYEuOnbD1QNV6t2u9iMK+mNKWabXO/Wms8kfg6t5MptM5kDJdezNBqPf5sMPg+TwKPZCUOhtQOIxnceT/vVoYBn9EeQVzeQdTUHiBnNNT2OvKvjggfAipRpOPn7aw5EsFCnRlxDJaigT5XzbJjIcjx1Yg0oIHVboJUTrrYzJQ4Tu7+99zTheaB94hLRGVYp9SqSi9uaeonHFRwuy1O3/546zmvM0OzLVs2SqdZmAhFki6VrutJUO+b/Yr63gnn/bsHuxt88sJMZq3Jz+t6r8NJn+mXP8CToDmozR9D1MRl31wm6uVddOdy04xWbl0vl8xoOwVGzJ4Ggn7dBq3ADQgB2RIC+M3XWa5+3zoB00nHtPvEOzyXQwmw9d766f5YuzurbJ0Rj4FBlJbj9gxfACorZwaD/rjf1unHd9eoMLbl4ouDmYTdHkenY12L2Y347Xp4frbrRW/HzQ7PKImfctX6olagZBA/01HkVkRTNcZ0IbLAhQvQYSoXboSBJsSoui4Lz2XX5HpkiZrOjt/dtLarln39CXv6C1QtlIrHCIVjKjiKwWWGjMUZ/eUS7zDMqPIK3UJiWh6ZImHEioDaqs0AdgiE0h0pwgnOca7Q0frhNtpMIgr0ETp8nb4KJzu3MIPXL6MfLdMFCZA2DrDVsWyuV3m4wdZWqQXMqPkIXEKoWZC93KFowz8+XStgF0rzJPwEZKTlaYiSfOdHr7LQp13JYUTn3gAoEvg3XYDJodv+MHflJvt9+eNS5aZxf1ZrsdXLTOmx1YwbrTOeu0qvJCcDBWiWK5Da3XRYc7Fzs6Cr539HNCeJuvDu+imw===END_SIMPLICITY_STUDIO_METADATA
# END OF METADATA