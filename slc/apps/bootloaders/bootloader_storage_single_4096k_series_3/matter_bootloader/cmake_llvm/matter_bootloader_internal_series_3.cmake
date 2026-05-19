####################################################################
# Automatically-generated file. Do not edit!                       #
####################################################################

set(SDK_PATH "/home/chbansal/Development/bleeding_edge_latest/matter_extension/third_party/simplicity_sdk")
set(COPIED_SDK_PATH "")
set(PKG_PATH "/home/chbansal/.silabs/slt/installs")

add_library(slc OBJECT
)

target_include_directories(slc PUBLIC
)

target_compile_definitions(slc PUBLIC
)

target_link_libraries(slc PUBLIC
    "-Wl,--start-group"
    "-Wl,--end-group"
)
target_compile_options(slc PUBLIC
)

set(post_build_command ${POST_BUILD_EXE} postbuild "./matter_bootloader_internal_series_3.slpb" --parameter build_dir:"$<TARGET_FILE_DIR:matter_bootloader_internal_series_3>")

target_link_options(slc INTERFACE
)

# BEGIN_SIMPLICITY_STUDIO_METADATA=eJzNVQ1v2jgY/ivImk7rqcQUVrpmlOmuMIkTHIjQ6aaliozjgq+OndlO2wnx3++1E77W7rRqmzQJGeex/X487/PaKxQNRpPh4HIw+5BEs6veYJxMeqMIhajz9iETcVy7Y9pwJS9idBI0YgQIk1SlXC4Aupq9q7+O0dtuHMeyk2v1L6MWtkiSMVguaJCptBAsMMwWeXCpskzJSbltooz9s+AiDTJiLdPJXCkrFElhyiUAkojEMM2ZSVqBEHeZ9w5Ocqbt54jCP/jYOEU+BtgAv84NF2wXxrfYNyKfe/tzCMlyl6/VBfPQgkmmiWXpFsT7znJIxJ1KI8vy7ouXFLIkEtwcuXA3izD/7VOh7JsXL6uQj/B2+jcEeuRjKPfA5no9JxpgCLSKKk1SrsONEY8AcFQCHXwYhi8Irsz7r9rPqOhPqmXJLzpGk+n4r/7lLJmOxzMQ5SpG0/7wj9ngfT/ZX4pRGKMgiNEazjyW9Gjcuxr2nao/ggXNMnXHUjhzQ4RhxzGqat5/oKJImYGVj9c7OFKFpiX6HC05CyVXProNl+Fo5MEaFEOasEIvIF+0tDYPMb6/vw8MF2RuApASNgZXLAeMKs3czp1K40qSDuSp//7RXedM52l24KvrBFXrcAmMOTGZWu7NlREFv7vRFXGnwU3e3RjtqAVmnMX18feV5Zeh+pcm+Rp6AxqNs/QdXI/GdcP1k+0CnTXpT2cD3zGrb9K8533lAjIEihhZRW/fE83JHDw5OHTDau3GtQ+ux25IIewzD6737oRofDW97G/fqi/vtadvte2dVoniwfCLAznctwKlF7jZaJzgf0bDiC5ZRupcGkskBX3V4ERoPDpUlNjSoyyEqH1VVJEtUq4qTaH/e8Jcvd3j9fynq1Zol4k7HOKlyhimyzmRhgjcY3dMqDxj0mKglTlSEpYuWCLgVTMWV17Yg2XSUYiNoJjkucE7x/vzxFilCZw3YEmw5FXjvH27DQg/Cvox8tU0cMkBVfKGLwrt+d2QsZVMDchl4gCZK6JTuOmgQ/icC24/w7Ljmmj7BGyVEnRJuHxizaS3X6JQx01JYTUALVAYOczDZqPZDtpBI0jqp6evzk7OW2fn9ebpaeO89brZhhnM2+2zdqsqLyQHdxnVPHepdTt4/8vnjg+S7x684xKt/wNovXRI=END_SIMPLICITY_STUDIO_METADATA