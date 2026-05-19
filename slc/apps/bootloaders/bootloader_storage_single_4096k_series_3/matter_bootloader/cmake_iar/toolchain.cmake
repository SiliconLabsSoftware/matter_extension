set(CMAKE_SYSTEM_NAME                   Generic)
set(CMAKE_SYSTEM_PROCESSOR              arm)
set(CMAKE_TRY_COMPILE_TARGET_TYPE       STATIC_LIBRARY)

if(WIN32)
  set(EXE_SUFFIX ".exe")
else()
  set(EXE_SUFFIX "")
endif()

if(DEFINED ENV{IAR_ARM_DIR})
  set(TOOLCHAIN_DIR "$ENV{IAR_ARM_DIR}/arm/bin/")
elseif(WIN32)
  set(TOOLCHAIN_DIR "/arm/bin/")
elseif(APPLE)
  set(TOOLCHAIN_DIR "/arm/bin/")
else()
  set(TOOLCHAIN_DIR "/arm/bin/")
endif()

if(DEFINED ENV{POST_BUILD_EXE})
  set(POST_BUILD_EXE "$ENV{POST_BUILD_EXE}")
elseif(WIN32)
  set(POST_BUILD_EXE "")
elseif(APPLE)
  set(POST_BUILD_EXE "")
else()
  set(POST_BUILD_EXE "/home/chbansal/.silabs/slt/installs/archive/commander/commander")
endif()

if(DEFINED ENV{NINJA_EXE_PATH})
  set(CMAKE_MAKE_PROGRAM "$ENV{NINJA_EXE_PATH}" CACHE FILEPATH "" FORCE)
elseif(WIN32)
  set(NINJA_RUNTIME_PATH "")
elseif(APPLE)
  set(NINJA_RUNTIME_PATH "")
else()
  set(NINJA_RUNTIME_PATH "/home/chbansal/.silabs/slt/installs/conan/p/ninja1b9fed093d653/p/ninja")
endif()
# Use default lookup mechanisms if the OS specific values are not set above
if (NINJA_RUNTIME_PATH)
	set(CMAKE_MAKE_PROGRAM ${NINJA_RUNTIME_PATH} CACHE FILEPATH "" FORCE)
endif()

set(CMAKE_C_COMPILER    ${TOOLCHAIN_DIR}iccarm${EXE_SUFFIX})
set(CMAKE_CXX_COMPILER  ${TOOLCHAIN_DIR}iccarm${EXE_SUFFIX})
set(CMAKE_ASM_COMPILER  ${TOOLCHAIN_DIR}iasmarm${EXE_SUFFIX})
set(CMAKE_LINKER        ${TOOLCHAIN_DIR}ilinkarm${EXE_SUFFIX})
set(CMAKE_OBJCOPY       ${TOOLCHAIN_DIR}ielftool${EXE_SUFFIX})

set(OBJCOPY_SREC_CMD    "--srec")
set(OBJCOPY_IHEX_CMD    "--ihex")
set(OBJCOPY_BIN_CMD     "--bin")

set(CMAKE_C_STANDARD_REQUIRED   OFF)
set(CMAKE_CXX_STANDARD_REQUIRED OFF)
set(CMAKE_C_EXTENSIONS          OFF)

set(CMAKE_C_FLAGS_RELEASE               "" CACHE STRING "")
set(CMAKE_CXX_FLAGS_RELEASE             "" CACHE STRING "")

# Response file support
# IAR cannot consume Ninja Multi-Config generated response files at the moment 
# SET(CMAKE_C_USE_RESPONSE_FILE_FOR_OBJECTS   1)
# SET(CMAKE_CXX_USE_RESPONSE_FILE_FOR_OBJECTS 1)
# SET(CMAKE_NINJA_FORCE_RESPONSE_FILE         1 CACHE INTERNAL "")

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM   NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY   ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE   ONLY)

set(CMAKE_EXECUTABLE_SUFFIX     .out)
set(CMAKE_EXECUTABLE_SUFFIX_C   .out)
set(CMAKE_EXECUTABLE_SUFFIX_CXX .out)
