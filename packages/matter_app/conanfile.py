import os
import sys
from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.files import copy, update_conandata
from typing import Iterable, Optional, Generator
import yaml
from pathlib import Path

## repo_root now provided by shared base recipe (MatterBaseRecipe.repo_root)
# For logging and error handling, use functions:
# self.output.success, self.output.info, self.output.warning, self.output.error
# See: https://docs.conan.io/2/reference/conanfile/attributes.html#output-contents

try:
    _recipe_dir = Path(__file__).resolve().parent
    for _base in (_recipe_dir, _recipe_dir.parent):
        if (_base / "_shared").is_dir() and str(_base) not in sys.path:
            sys.path.insert(0, str(_base))
            break
except Exception:
    pass
from _shared.base_recipe import (
    MatterBaseRecipe,
    is_matter_sdk_package_path,
    matter_sdk_export_stub,
)


class matter_appRecipe(MatterBaseRecipe):
    name = "matter_app"
    description = "matter sample-app package"

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
      "packageType": "software",
      "sdkLtsTag": ""
    }

    @property
    def matter_app_folder(self) -> str:
        return str(self.repo_root)

    def set_version(self):
        self.version = self.matter_package_version

    def requirements(self):
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

        # Define the files to be included in the package
        files_to_package = {"License"}

        
        silabs_package_assistant = self.python_requires["silabs_package_assistant"].module

        files_to_package.update(
            self._gather_slc_release_files(
                desired_qualities=["production", "evaluation"],
                desired_packages=["matter"],
                assistant=silabs_package_assistant,
            )
        )
        files_to_package.update(self._gather_app_support_files())
        files_to_package = self._filter_repo_files(files_to_package)

        static_libraries = {file for file in files_to_package if file.endswith(".a")}
        files_to_package -= static_libraries
        for file in static_libraries:
            copy(self, pattern=file, src=matter_app_folder, dst=os.path.join(self.package_folder, "."))

        silabs_package_assistant.copy_files(
            files_to_package=files_to_package,
            src_folder=matter_app_folder,
            dst_folder=os.path.join(self.package_folder, "."),
        )

        if os.path.exists("conan-matter_app.lock"):
            copy(self, pattern="conan-matter_app.lock", src=matter_app_folder, dst=os.path.join(self.package_folder, "."))

        silabs_package_assistant.generate_metadata(self, files_to_package)

    def build(self):
        matter_app_folder = self.matter_app_folder
        files_to_package = {"License"}
        git_extra_files = []

        silabs_package_assistant = self.python_requires["silabs_package_assistant"].module

        with matter_sdk_export_stub(self.repo_root):
            files_to_package.update(
                self._gather_slc_release_files(
                    desired_qualities=["production", "evaluation"],
                    desired_packages=["matter"],
                    assistant=silabs_package_assistant,
                )
            )
            files_to_package = self._filter_repo_files(files_to_package)

        if git_extra_files:
            files_to_package.update(git_extra_files)
        with open("matter_app-filter-repo-filelist.txt", "w") as filelistfile:
            for file in files_to_package:
                filelistfile.write(file + "\n")
        git_path_mapping = []
        with open("matter_app-filter-repo-pathmap.txt", "w") as pathmapfile:
            for mapping in git_path_mapping:
                pathmapfile.write(mapping + "\n")

    def package_info(self):
        pass

    # --------------------- Helpers ---------------------
    def _resolve_repo_file(self, file: str) -> Path:
        path = Path(file)
        if path.is_absolute():
            return path
        return self.repo_root / path

    def _file_exists_in_repo(self, file: str) -> bool:
        path = self._resolve_repo_file(file)
        return path.is_file()

    def _filter_repo_files(self, files: Iterable[str]) -> set[str]:
        return {
            file
            for file in files
            if not is_matter_sdk_package_path(file)
            and self._file_exists_in_repo(file)
        }

    def _gather_slc_release_files(
        self,
        desired_qualities: list[str],
        desired_packages: list[str],
        assistant,
    ) -> set:
        """Discover .slcp/.slcw files (excluding third_party) and collect related release files.

        Returns a set of file paths including the SLC definition file itself plus any related files
        when the assistant reports matches for the given qualities/packages.
        """
        collected: set[str] = set()
        root = self.repo_root
        with matter_sdk_export_stub(root):
            for slc_file in root.rglob("*.slc*"):
                if "third_party" in slc_file.parts:
                    continue
                if slc_file.suffix not in (".slcp", ".slcw"):
                    continue
                rel_path = str(slc_file.relative_to(root))
                try:
                    related = assistant.list_files_in_slc_file(
                        slc_file_path=rel_path,
                        desired_qualities=desired_qualities,
                        desired_packages=desired_packages,
                        fail_on_missing_files=True,
                    )
                except Exception as e:
                    self.output.warning(f"Failed processing {rel_path}: {e}")
                    continue
                collected.add(rel_path)
                if related:
                    collected.update(
                        path
                        for path in related
                        if not is_matter_sdk_package_path(path)
                    )
        return collected

    def _gather_app_support_files(self) -> set[str]:
        """Ship pkg.slt and user.slconf per app; one shared build-app.sh under slc/apps."""
        collected: set[str] = set()
        root = self.repo_root
        user_slconf = (
            "# Shipped with matter_app. Regenerated by matter-app-slconf after slt install.\n"
            'include = [\n'
            '  "autogen/slc-sdk.slconf"\n'
            "]\n"
        )

        build_script = root / "slc" / "apps" / "build-app.sh"
        if build_script.is_file():
            collected.add(str(build_script.relative_to(root)))

        for pkg_slt in root.rglob("pkg.slt"):
            if "third_party" in pkg_slt.parts:
                continue
            app_dir = pkg_slt.parent
            rel_pkg = str(pkg_slt.relative_to(root))
            collected.add(rel_pkg)

            user_path = app_dir / "user.slconf"
            if not user_path.is_file():
                user_path.write_text(user_slconf, encoding="utf-8")
            collected.add(str(user_path.relative_to(root)))

        return collected

