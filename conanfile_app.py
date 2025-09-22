import os
from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.files import copy, update_conandata
from typing import Iterable, Optional, Generator
import sys
import yaml
from pathlib import Path
# For logging and error handling, use functions:
# self.output.success, self.output.info, self.output.warning, self.output.error
# See: https://docs.conan.io/2/reference/conanfile/attributes.html#output-contents

class matter_appRecipe(ConanFile):
    # Attributes: https://docs.conan.io/2/reference/conanfile/attributes.html
    # Package reference
    user = "silabs"
    name = "matter_app"
    version = "2.6.2-alpha.2"

    # Basic Conan metadata
    description = "matter SampleApp package"
    license = "www.silabs.com/about-us/legal/master-software-license-agreement"
    author = "Silicon Laboratories Inc."
    homepage = "https://github.com/SiliconLabsSoftware/matter_extension/blob/main/README.md"  # Ex: https://stash.silabs.com/projects/<space>/repos/<project>/browse/README.md
    url = (
        "https://github.com/SiliconLabsSoftware/matter_extension"
    )  # Ex: https://stash.silabs.com/projects/<space>/repos/<project>/browse
    topics = "silabs"  # You can add more topics

    # Python module for .slc files parsing/expansion
    python_requires = "silabs_package_assistant/[>=1]@silabs"

    # Custom Silabs metadata
    sl_metadata = {
        "slack_channel": "#matter-development",
        "team": "MATTER",
        "confluence_doc": "",
        "jira_project": "https://jira.silabs.com/projects/MATTER/summary",  # Ex: https://jira.silabs.com/projects/<space>/summary
        "maintainers": [
            {"name": "sashaha", "email": "sashaha@silabs.com"},
        ],
    }
    # Other attributes
    revision_mode = "scm"

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

    def requirements(self):
        pass

    def layout(self):
        pass

    def deploy(self):
        pass

    def export(self):
        pass

    def package_id(self):
        # Completely clear all the info, resulting ``package_id`` will be the same
        self.info.clear()

    def package(self):
        # Define the source folder for the matter_app component
        matter_app_folder = self.source_folder

        # Define the files to be included in the package
        files_to_package = {"License.txt"}

        
        silabs_package_assistant = self.python_requires["silabs_package_assistant"].module

        slcp_files = [str(p) for p in Path(os.getcwd()).rglob("*.slcp") if "third_party" not in p.parts]
        slcw_files = [str(p) for p in Path(os.getcwd()).rglob("*.slcw") if "third_party" not in p.parts]

        for slcp_file in slcp_files + slcw_files:
            # slcp_related_files should return empty list if the desired_quality and desired_packages are not matched
            slcp_related_files = silabs_package_assistant.list_files_in_slc_file(
                slc_file_path=slcp_file,
                desired_qualities=['production', 'evaluation'],
                desired_packages=['matter'],
                fail_on_missing_files=False,
            )
            if (len(slcp_related_files) > 0):
                files_to_package.update(slcp_file)
                files_to_package.update(slcp_related_files)

        files_to_package = {file for file in files_to_package if os.path.exists(file) and not os.path.isdir(file)}


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

        if os.path.exists("conan-matter_app.lock"):
            copy(self, pattern="conan-matter_app.lock", src=matter_app_folder, dst=os.path.join(self.package_folder, "."))

        silabs_package_assistant.generate_metadata(self, files_to_package)



    def build(self):
        # Define the source folder for the matter_app component
        matter_app_folder = self.source_folder

        # Define the files to be included in the package
        files_to_package = {"License.txt"}
        git_extra_files = []

        
        silabs_package_assistant = self.python_requires["silabs_package_assistant"].module

        slcp_files = [str(p) for p in Path(os.getcwd()).rglob("*.slcp") if "third_party" not in p.parts]
        slcw_files = [str(p) for p in Path(os.getcwd()).rglob("*.slcw") if "third_party" not in p.parts]

        for slcp_file in slcp_files + slcw_files:
            # slcp_related_files should return empty list if the desired_quality and desired_packages are not matched
            slcp_related_files = silabs_package_assistant.list_files_in_slc_file(
                slc_file_path=slcp_file,
                desired_qualities=['production', 'evaluation'],
                desired_packages=['matter'],
                fail_on_missing_files=False,
            )
            if (len(slcp_related_files) > 0):
                files_to_package.update(slcp_file)
                files_to_package.update(slcp_related_files)

        files_to_package = {file for file in files_to_package if os.path.exists(file) and not os.path.isdir(file)}


        if git_extra_files:
          files_to_package.update(git_extra_files)
        with open("matter_app-filter-repo-filelist.txt","w") as filelistfile:
            for file in files_to_package:
                filelistfile.write(file+'\n')
        git_path_mapping = []
        with open("matter_app-filter-repo-pathmap.txt","w") as pathmapfile:
            for mapping in git_path_mapping:
                pathmapfile.write(mapping+'\n')





    def package_info(self):
        # Reference: https://confluence.silabs.com/pages/viewpage.action?spaceKey=SWARCH&title=Package+Manager%3A+Conan+Metadata+for+SLT+Integration

        # SDK Packages
        self.buildenv_info.append_path("SLC_SDK_PACKAGE_PATH", self.package_folder)

