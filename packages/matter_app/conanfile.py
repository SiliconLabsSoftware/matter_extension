import os
import sys
from conan.tools.files import copy
from pathlib import Path

## repo_root now provided by shared base recipe (MatterBaseRecipe.repo_root)
# For logging and error handling, use functions:
# self.output.success, self.output.info, self.output.warning, self.output.error
# See: https://docs.conan.io/2/reference/conanfile/attributes.html#output-contents

try:
    # Prefer recipe dir (Conan cache e/) so exported e/_shared is found; else packages/.
    _recipe_dir = Path(__file__).resolve().parent
    for _base in (_recipe_dir, _recipe_dir.parent):
        if (_base / "_shared").is_dir() and str(_base) not in sys.path:
            sys.path.insert(0, str(_base))
            break
except Exception:
    pass
from _shared.base_recipe import MatterBaseRecipe


class matter_appRecipe(MatterBaseRecipe):
    name = "matter_app"
    # version set dynamically in MatterBaseRecipe.set_version() from matter.slce + SL_PRERELEASE*
    description = "matter sample-app package"
    # App SDK root marker + Studio templates (same pattern as wifi_app.slsdk).
    _REQUIRED_ROOT_FILES = (
        "matter_app.slsdk",
        "matter_templates.xml",
    )
    # Other attributes
    # revision_mode = "scm"

    # Custom SLT metadata
    # Reference: https://confluence.silabs.com/spaces/SS/pages/669417743/SLT+options+in+conanfile.py
    """
    Available options and their values:
    packageType (string):
        - sdk: SDK packages
        - toolchain: Toolchain packages
        - apack: APACK packages
        - tools: Tool packages
        - system: System packages (not for user-installable packages)
        - software: General software packages (default)
    subPackage (boolean):
        - Only applicable for archive packages
        - Should be set to False for Conan packages
    releaseNotesUrl (string):
        - URL to the release notes document
    compatibleVersion (string):
        - Version compatibility information
    sdkLtsTag (string):
        - Long Term Support (LTS) tag for SDK packages
    """
    # Dictionary to declare properties
    options = {
      "compatibleVersion": ["ANY"],
      "subPackage": [True, False],
      "releaseNotesUrl": ["ANY"],
      "packageType": ["ANY"],
      "sdkLtsTag": ["ANY"]
    }

    # Dictionary to define properties values.
    # Alternative is to set values in def configure(self) of recipe
    default_options = {
      "compatibleVersion": "ANY",
      "subPackage": False,
      "releaseNotesUrl": "",
      "packageType": "sdk",
      "sdkLtsTag": ""
    }

    # Centralized folder reference (mirrors matter recipe pattern). Avoids relying
    # on self.source_folder so repo-relative operations stay consistent.
    @property
    def matter_app_folder(self) -> str:
        return str(self.repo_root)

    def requirements(self):
        # Range on line version.
        self.requires(f"matter/{self.matter_conan_range}@{self.user}")

    def layout(self):
        pass

    def deploy(self):
        pass

    def export(self):
        self.export_shared_recipe_support()

    def package_id(self):
        # Completely clear all the info, resulting ``package_id`` will be the same
        self.info.clear()

    def package(self):
        # Define the source folder for the matter_app component (property-backed)
        matter_app_folder = self.matter_app_folder
        repo_root = self.repo_root

        silabs_package_assistant = self.python_requires["silabs_package_assistant"].module
        files_to_package = self._collect_app_package_files(
            desired_qualities=["production", "evaluation", "experimental"],
            desired_packages=["matter"],
            assistant=silabs_package_assistant,
            seed={"License"},
        )

        # Get all .a files from files_to_package and copy them
        static_libraries = {file for file in files_to_package if file.endswith(".a")}
        files_to_package -= static_libraries
        for file in static_libraries:
            copy(self, pattern=file, src=matter_app_folder, dst=os.path.join(self.package_folder, "."))

        # Copy slc files using silabs_package_assistant
        silabs_package_assistant.copy_files(
            files_to_package=files_to_package,
            src_folder=matter_app_folder,
            dst_folder=os.path.join(self.package_folder, "."),
        )

        # Package-only builder at package root: <pkg>/build_app.sh
        build_app_src = repo_root / "packages" / "build_app.sh"
        if not build_app_src.is_file():
            raise FileNotFoundError(f"missing {build_app_src}")
        copy(
            self,
            pattern="build_app.sh",
            src=str(build_app_src.parent),
            dst=os.path.join(self.package_folder, "."),
        )

        if (repo_root / "conan-matter_app.lock").is_file():
            copy(self, pattern="conan-matter_app.lock", src=matter_app_folder, dst=os.path.join(self.package_folder, "."))

        silabs_package_assistant.generate_metadata(self, files_to_package)

    def build(self):
        # Define the source folder for the matter_app component (property-backed)
        repo_root = self.repo_root

        silabs_package_assistant = self.python_requires["silabs_package_assistant"].module
        files_to_package = self._collect_app_package_files(
            desired_qualities=["production", "evaluation", "experimental"],
            desired_packages=["matter"],
            assistant=silabs_package_assistant,
            seed={"License"},
        )

        # Repo source path; packaged as <pkg>/build_app.sh (see package()).
        if (repo_root / "packages" / "build_app.sh").is_file():
            files_to_package.add("packages/build_app.sh")

        with open("matter_app-filter-repo-filelist.txt","w") as filelistfile:
            for file in sorted(files_to_package):
                filelistfile.write(file+'\n')
        # Map repo path → package-root layout for filter-repo consumers.
        git_path_mapping = ["packages/build_app.sh:build_app.sh"]
        with open("matter_app-filter-repo-pathmap.txt","w") as pathmapfile:
            for mapping in git_path_mapping:
                pathmapfile.write(mapping+'\n')

    def package_info(self):
        # Reference: https://confluence.silabs.com/pages/viewpage.action?spaceKey=SWARCH&title=Package+Manager%3A+Conan+Metadata+for+SLT+Integration

        # SDK Packages
        self.buildenv_info.append_path("SLC_SDK_PACKAGE_PATH", self.package_folder)
