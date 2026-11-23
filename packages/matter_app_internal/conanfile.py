import sys
from pathlib import Path

from conan import ConanFile

# Cache recipes import e/_shared. Checkout recipes import packages/_shared.
_recipe_dir = Path(__file__).resolve().parent
for _base in (_recipe_dir, _recipe_dir.parent):
    if (_base / "_shared").is_dir() and str(_base) not in sys.path:
        sys.path.insert(0, str(_base))
        break

from _shared import recipe_support

_QUALITIES = ("internal",)

_REQUIRED_ROOT_FILES = (
    "matter_app_internal.slsdk",
)

_PATH_MAPPINGS = (
    "packages/build_app.sh=>build_app.sh",
    "packages/_shared/release_stream_channel=>release_stream_channel",
)


class matter_app_internalRecipe(ConanFile):
    """Matter internal sample-app package."""

    name = "matter_app_internal"
    user = "silabs"
    license = "www.silabs.com/about-us/legal/master-software-license-agreement"
    author = "Silicon Laboratories Inc."
    homepage = "https://github.com/SiliconLabsSoftware/matter_extension/blob/main/README.md"
    url = "https://github.com/SiliconLabsSoftware/matter_extension"
    topics = "silabs"
    python_requires = "silabs_package_assistant/[~2]@silabs"
    release_stream_channel = "2026-12"
    description = "Matter internal sample-app package"
    sl_metadata = {
        "slack_channel": "#matter-development",
        "team": "MATTER",
        "confluence_doc": "",
        "jira_project": "https://jira.silabs.com/projects/MATTER/summary",
        "maintainers": [],
    }
    revision_mode = "scm"

    options = {
        "compatibleVersion": ["ANY"],
        "subPackage": [True, False],
        "releaseNotesUrl": ["ANY"],
        "packageType": ["ANY"],
        "sdkLtsTag": ["ANY"],
    }
    default_options = {
        "compatibleVersion": "ANY",
        "subPackage": False,
        "releaseNotesUrl": "",
        "packageType": "sdk",
        "sdkLtsTag": "",
    }

    def get_version(self):
        return recipe_support.matter_get_version(self)

    def set_version(self):
        recipe_support.set_version(self)

    def requirements(self):
        pass

    def layout(self):
        recipe_support.apply_layout(self)

    def export(self):
        recipe_support.export_recipe_files(self)

    def package_id(self):
        self.info.clear()

    def package(self):
        recipe_support.matter_package_files(
            self,
            kind="app",
            required_root_files=_REQUIRED_ROOT_FILES,
            path_mappings=_PATH_MAPPINGS,
            rewrite_wiseconnect=True,
            qualities=_QUALITIES,
        )

    def build(self):
        recipe_support.write_filelists(
            self,
            kind="app",
            required_root_files=_REQUIRED_ROOT_FILES,
            path_mappings=_PATH_MAPPINGS,
            qualities=_QUALITIES,
        )

    def package_info(self):
        recipe_support.apply_package_info(self)
