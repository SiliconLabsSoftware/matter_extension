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


class matter_internalRecipe(MatterBaseRecipe):
    name = "matter_internal"
    # version set dynamically in MatterBaseRecipe.set_version() from matter.slce + SL_PRERELEASE*
    description = "Matter internal components package"
    _REQUIRED_ROOT_FILES = (
        "matter_internal.slsdk",
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
        "sdkLtsTag": ["ANY"],
    }

    # Dictionary to define properties values.
    # Alternative is to set values in def configure(self) of recipe
    default_options = {
        "compatibleVersion": "ANY",
        "subPackage": False,
        "releaseNotesUrl": "",
        "packageType": "sdk",
        "sdkLtsTag": "",
    }

    @property
    def matter_internal_folder(self) -> str:
        return str(self.repo_root)

    def requirements(self):
        self.requires(f"matter/{self.matter_conan_range}@{self.user}")

    def layout(self):
        pass

    def deploy(self):
        pass

    def export(self):
        self.export_shared_recipe_support()

    def package_id(self):
        self.info.clear()

    def _collect_internal_package_files(self, assistant) -> set[str]:
        """Gather quality:internal .slcc (+ inputs) for packaging."""
        files_to_package: set[str] = {"License"}
        files_to_package.update(
            self._gather_internal_slcc_files(desired_packages=["matter"])
        )
        slce_file = self.repo_root / "matter.slce"
        if slce_file.is_file():
            try:
                files_to_package.update(
                    assistant.find_slc_files_to_release(
                        slc_sdk_or_extension_def_file=str(slce_file.name),
                        desired_qualities=["internal"],
                        fail_on_missing_files=False,
                        include_slcp=False,
                        include_slcc=True,
                        desired_packages=["matter"],
                    )
                )
            except Exception as e:
                self.output.warning(
                    f"find_slc_files_to_release for internal qualities failed: {e}"
                )
        files_to_package.update(self._gather_required_root_files())
        files_to_package = self._existing_repo_relative_files(files_to_package)
        files_to_package.update(self._gather_required_root_files())
        self._require_root_files(files_to_package)
        return files_to_package

    def package(self):
        matter_folder = self.matter_internal_folder
        repo_root = self.repo_root
        os.chdir(repo_root)

        silabs_package_assistant = self.python_requires[
            "silabs_package_assistant"
        ].module
        files_to_package = self._collect_internal_package_files(
            silabs_package_assistant
        )

        static_libraries = {
            file for file in files_to_package if file.endswith(".a")
        }
        files_to_package -= static_libraries
        for file in static_libraries:
            copy(
                self,
                pattern=file,
                src=matter_folder,
                dst=os.path.join(self.package_folder, "."),
            )

        silabs_package_assistant.copy_files(
            files_to_package=files_to_package,
            src_folder=matter_folder,
            dst_folder=os.path.join(self.package_folder, "."),
        )

        if (repo_root / "conan-matter_internal.lock").is_file():
            copy(
                self,
                pattern="conan-matter_internal.lock",
                src=matter_folder,
                dst=os.path.join(self.package_folder, "."),
            )

        silabs_package_assistant.generate_metadata(self, files_to_package)

    def build(self):
        os.chdir(self.repo_root)

        silabs_package_assistant = self.python_requires[
            "silabs_package_assistant"
        ].module
        files_to_package = self._collect_internal_package_files(
            silabs_package_assistant
        )

        with open("matter_internal-filter-repo-filelist.txt", "w") as filelistfile:
            for file in sorted(files_to_package):
                filelistfile.write(file + "\n")
        with open("matter_internal-filter-repo-pathmap.txt", "w") as pathmapfile:
            pass

    def package_info(self):
        # Reference: https://confluence.silabs.com/pages/viewpage.action?spaceKey=SWARCH&title=Package+Manager%3A+Conan+Metadata+for+SLT+Integration
        self.buildenv_info.append_path(
            "SLC_SDK_PACKAGE_PATH", self.package_folder
        )
