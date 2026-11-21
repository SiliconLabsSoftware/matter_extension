import sys
from pathlib import Path

from conan import ConanFile
from conan.tools.files import update_conandata
from conan.tools.scm import Git

# Cache recipes import e/_shared. Checkout recipes import packages/_shared.
_recipe_dir = Path(__file__).resolve().parent
for _base in (_recipe_dir, _recipe_dir.parent):
    if (_base / "_shared").is_dir() and str(_base) not in sys.path:
        sys.path.insert(0, str(_base))
        break

from _shared import recipe_support

_QUALITIES = ("production", "evaluation", "experimental")

_REQUIRED_ROOT_FILES = (
    "matter.slsdk",
    "src/app/zap-templates/app-templates.json",
    "src/app/zap-templates/zcl/zcl.json",
)


class matterRecipe(ConanFile):
    """Matter stack package."""

    name = "matter"
    user = "silabs"
    license = "www.silabs.com/about-us/legal/master-software-license-agreement"
    author = "Silicon Laboratories Inc."
    homepage = "https://github.com/SiliconLabsSoftware/matter_extension/blob/main/README.md"
    url = "https://github.com/SiliconLabsSoftware/matter_extension"
    topics = "silabs"
    python_requires = "silabs_package_assistant/[~2]@silabs"
    release_stream_channel = "2026-12"
    description = "Matter extension for Simplicity SDK Suite"
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
        channel = self.release_stream_channel
        # Thread / multiprotocol stack
        self.requires(f"thread/[>=3.2.0 <3.2.1,include_prerelease]@{self.user}/{channel}")
        self.requires(f"multiprotocol/[>=1.2.0 <1.2.1,include_prerelease]@{self.user}/{channel}")
        self.requires(f"zigbee/[>=9.2.0 <9.2.1,include_prerelease]@{self.user}/{channel}")
        self.requires(f"bluetooth_le_host/[>=11.2.0 <11.2.1,include_prerelease]@{self.user}/{channel}")
        self.requires(f"cpc/[>=4.10.0 <4.10.1,include_prerelease]@{self.user}/{channel}")
        # Wi-Fi
        self.requires(f"wifi/[>=4.2.0 <4.2.1,include_prerelease]@{self.user}/{channel}")
        self.requires(f"bluetooth_le_siwx91x/[>=4.2.0 <4.2.1,include_prerelease]@{self.user}/{channel}")

    def slt_requirements(self):
        return {"zap": "~", "slc-cli": "~"}

    def layout(self):
        recipe_support.apply_layout(self)

    def export(self):
        recipe_support.export_recipe_files(
            self,
            extra_filename="matter.slce.extra",
        )
        # Add commit info to the package for revision / git commit correspondence
        git = Git(self)
        scm_commit = git.get_commit(repository=False)
        self.output.info(f"Obtained commit {scm_commit}")
        update_conandata(
            self,
            {
                "sources": {
                    "commit": scm_commit,
                    "url": "git@github.com:SiliconLabsSoftware/matter_extension.git",
                }
            },
        )

    def package_id(self):
        self.info.clear()

    def package(self):
        recipe_support.matter_package_files(
            self,
            kind="stack",
            required_root_files=_REQUIRED_ROOT_FILES,
            extra_filename="matter.slce.extra",
            skip_sample_apps=True,
            qualities=_QUALITIES,
        )

    def build(self):
        recipe_support.write_filelists(
            self,
            kind="stack",
            required_root_files=_REQUIRED_ROOT_FILES,
            extra_filename="matter.slce.extra",
            skip_sample_apps=True,
            qualities=_QUALITIES,
        )

    def package_info(self):
        recipe_support.apply_package_info(self)
