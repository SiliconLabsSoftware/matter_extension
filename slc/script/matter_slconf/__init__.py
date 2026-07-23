"""SLT slconf filtering and .slcp validation for Matter package builds."""

from .filters import (
    SLC_SDK_PATH_DENYLIST,
    THREAD_EXCLUDE_PACKAGES,
    WIFI_NCP_ONLY_PACKAGES,
    WIFI_SOC_EXCLUDE_PACKAGES,
    detect_app_stack_type,
    exclude_packages_for_app_type,
    filter_slc_sdk_paths,
    parse_slconf_path_comment_package,
    path_is_slc_extension_root,
)
from .slconf_io import (
    parse_pkg_slconf,
    parse_pkg_slconf_sdk_paths,
    slconf_sdk_path_lines,
    write_filtered_app_slconf,
)
from .validate import validate_slcp_against_slconf

__all__ = [
    "SLC_SDK_PATH_DENYLIST",
    "THREAD_EXCLUDE_PACKAGES",
    "WIFI_NCP_ONLY_PACKAGES",
    "WIFI_SOC_EXCLUDE_PACKAGES",
    "detect_app_stack_type",
    "exclude_packages_for_app_type",
    "filter_slc_sdk_paths",
    "path_is_slc_extension_root",
    "parse_pkg_slconf",
    "parse_pkg_slconf_sdk_paths",
    "parse_slconf_path_comment_package",
    "slconf_sdk_path_lines",
    "write_filtered_app_slconf",
    "validate_slcp_against_slconf",
]
