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

# BEGIN_SIMPLICITY_STUDIO_METADATA=eJzNVQ1v2jgY/ivImk7rqcQUVrpmlOmuMIkTHIjQ6aaliozjgq+OndlO2wnx3++1E77W7rRqmzQJGeex/X487/PaKxQNRpPh4HIw+5BEs6veYJxMeqMIhajz9iETcVy7Y9pwJS9idBI0YgQIk1SlXC4Aupq9q7+O0dtuHMeyk2v1L6MWtkiSMVguaJCptBAsMMwWeXCpskzJSbltooz9s+AiDTJiLdPJXCkrFElhyiUAkojEMM2ZSVrBglLvHHzkTNvPEYV/cLHxiXwIsAF+nRsu2C6KbzFvRD739ucQkeUuXasL5qEFk0wTy9ItiPed5ZCHO5VGluXdFy8pJEkkuDly4W4WYf7bp0LZNy9eViEf4e30bwj0yMdQ7oHN9XpONMAQaBVVmqRchxsjHgHgqAQ6+DAMXw9cmfdftZ9R0J9TypJedIwm0/Ff/ctZMh2PZyDJVYym/eEfs8H7frK/FKMwRkEQozWceSzo0bh3New7TX8EC5pl6o6lcOaGCMOOY1SVvP9ARZEyAysfr3dwpApNS/Q5UnIWSqp8dBsqw9HIgzWohTRhhV5AvmhpbR5ifH9/HxguyNwEoCRsDK5IDhhVmrmdO5HGlSIdyFP//YN7zlnO0+zAVdfJqdbhEghzUjK13FsrAwp+d6Or4U6Bm7S7MdoxC8Q4i+vj76vKL8P0r8zxNXQGtBln6Tu4G43rhesnmwX6atKfzga+X1bfpHhP+8oFZAjUMLKK3r4nmpM5eHJw6IbV2o1rH1yP3ZBC2GceXO/dCNH4anrZ375TX15qT19p2wut0sSD4RcHarhvBUovcLPROMH/jIYRXbKM1Lk0lkgK8qrBidB4dKgosaVHWQhR+6qmIlukXFWSQv/3frl6u5fr+e9WrdAuE3c4xEuVMUyXcyINEbjH7phQecakxUArc6QkLF2wRMCTZiyuvLAHy6SjEBtBMclzg3eO9+eJsUoTOG/AkmDJq8Z5+3YbEH4U9GPkq2ngkgOq5A1fFNrzuyFjK5kakMvEATJXRKdwz0GH8DkX3H6GZcc10fYJ2Col6JJw+cSaSW+/RKGOm5LCagBaoDBymIfNRrMdtINGkNRPT1+dnZy3zs7rzdPTxnnrdbMNM5i322ftVlVeSA6uMqp57lLrdvD+l88dHyTfPXjEJVr/B2dochA==END_SIMPLICITY_STUDIO_METADATA