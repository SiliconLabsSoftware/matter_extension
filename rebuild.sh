#!/usr/bin/env bash

#rm -rf out/brd4187c

slc generate -d out/brd4187c/lighting-app-series-2-internal-solution --sdk-package-path /Users/lobelive/Documents/workspace/matter_extension/third_party/simplicity_sdk --sdk-package-path /Users/lobelive/Documents/workspace/matter_extension --sdk-package-path /Users/lobelive/Documents/workspace/matter_extension/third_party/wifi_sdk -w slc/apps/lighting-app/thread/lighting-app-series-2-internal.slcw --with brd4187c  --with=toolchain_llvm --generator-timeout=180 -o cmake

cmake -S out/brd4187c/lighting-app-series-2-internal-solution/lighting-app-series-2-internal_llvm_cmake -B out/brd4187c/lighting-app-series-2-internal-solution/lighting-app-series-2-internal_cmake/build -G Ninja

cmake --build out/brd4187c/lighting-app-series-2-internal-solution/lighting-app-series-2-internal_cmake/build --clean-first
