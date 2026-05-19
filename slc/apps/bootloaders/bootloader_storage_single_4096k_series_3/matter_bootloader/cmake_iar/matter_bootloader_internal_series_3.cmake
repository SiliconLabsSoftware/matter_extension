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
)
target_compile_options(slc PUBLIC
    $<$<COMPILE_LANGUAGE:C>:--cmse>
    $<$<COMPILE_LANGUAGE:CXX>:--cmse>
)

set(post_build_command ${POST_BUILD_EXE} postbuild "./matter_bootloader_internal_series_3.slpb" --parameter build_dir:"$<TARGET_FILE_DIR:matter_bootloader_internal_series_3>")

target_link_options(slc INTERFACE
)

# BEGIN_SIMPLICITY_STUDIO_METADATA=eJzNVQ1v2jgY/ivImk7rqcQUVrpmlOmuMIkTHIjQ6aaliozjgq+OndlO2wnx3++1E77W7rRqmzQJGeex/X487/PaKxQNRpPh4HIw+5BEs6veYJxMeqMIhajz9iETcVy7Y9pwJS9idBI0YgQIk1SlXC4Aupq9q7+O0dtuHMeyk2v1L6MWtkiSMVguaJCptBAsMMwWeXCpskzJSbltooz9s+AiDTJiLdPJXCkrFElhyiUAkojEMM2ZSVoBJ9o7Bx850/ZzROEfXGx8Ih8CbIBf54YLtoviW8wbkc+9/TlEZLlL1+qCeWjBJNPEsnQL4n1nOeThTqWRZXn3xUsKSRIJbo5cuJtFmP/2qVD2zYuXVchHeDv9GwI98jGUe2BzvZ4TDTAEWkWVJinX4caIRwA4KoEOPgzD1wNX5v1X7WcU9OeUsqQXHaPJdPxX/3KWTMfjGUhyFaNpf/jHbPC+n+wvxSiMURDEaA1nHgt6NO5dDftO0x/BgmaZumMpnLkhwrDjGFUl7z9QUaTMwMrH6x0cqULTEn2OlJyFkiof3YbKcDTyYA1qIU1YoReQL1pam4cY39/fB4YLMjcBKAkbgyuSA0aVZm7nTqRxpUgH8tR//+Cec5bzNDtw1XVyqnW4BMKclEwt99bKgILf3ehquFPgJu1ujHbMAjHO4vr4+6ryyzD9K3N8DZ0BbcZZ+g7uRuN64frJZoG+mvSns4Hvl9U3Kd7TvnIBGQI1jKyit++J5mQOnhwcumG1duPaB9djN6QQ9pkH13s3QjS+ml72t+/Ul5fa01fa9kKrNPFg+MWBGu5bgdIL3Gw0TvA/o2FElywjdS6NJZKCvGpwIjQeHSpKbOlRFkLUvqqpyBYpV5Wk0P+9X67e7uV6/rtVK7TLxB0O8VJlDNPlnEhDBO6xOyZUnjFpMdDKHCkJSxcsEfCkGYsrL+zBMukoxEZQTPLc4J3j/XlirNIEzhuwJFjyqnHevt0GhB8F/Rj5ahq45IAqecMXhfb8bsjYSqYG5DJxgMwV0Sncc9AhfM4Ft59h2XFNtH0CtkoJuiRcPrFm0tsvUajjpqSwGoAWKIwc5mGz0WwH7aARJPXT01dnJ+ets/N68/S0cd563WzDDObt9lm7VZUXkoOrjGqeu9S6Hbz/5XPHB8l3Dx5xidb/Ae0Wckw==END_SIMPLICITY_STUDIO_METADATA
