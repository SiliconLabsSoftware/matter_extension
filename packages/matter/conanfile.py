import os
from pathlib import Path
from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.files import copy, update_conandata
from typing import Iterable, Optional, Generator
import yaml
# For logging and error handling, use functions:
# self.output.success, self.output.info, self.output.warning, self.output.error
# See: https://docs.conan.io/2/reference/conanfile/attributes.html#output-contents

_RECIPE_PATH = Path(__file__).resolve()
_REPO_ROOT = _RECIPE_PATH.parents[2]


class matterRecipe(ConanFile):
    name = "matter"
    user = "silabs"
    slce_file = os.path.join(_REPO_ROOT, "matter.slce")
    license = "www.silabs.com/about-us/legal/master-software-license-agreement"
    author = "Silicon Laboratories Inc."
    homepage = "https://github.com/SiliconLabsSoftware/matter_extension/blob/main/README.md"
    url = "https://github.com/SiliconLabsSoftware/matter_extension"
    topics = ("silabs",)
    python_requires = "silabs_package_assistant/[>=1]@silabs"

    sl_metadata = {
        "slack_channel": "#matter-development",
        "team": "MATTER",
        "confluence_doc": "",
        "jira_project": "https://jira.silabs.com/projects/MATTER/summary",
        "maintainers": [],
    }
    # Specific description (can override base if needed)
    description = "Matter extension for Simplicity SDK Suite"

    def set_version(self):
        silabs_package_assistant = self.python_requires["silabs_package_assistant"].module

        if not self.version:
            self.version = silabs_package_assistant.get_version(self.slce_file)
        # if not self.channel:
        #     self.channel = silabs_package_assistant.get_channel()
        self.revision_mode = "scm"
        
        self.output.info(f"Resolved context: {self.name}, {self.version}, {self.channel}, {self.user}")

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

    # Provide a unified folder reference for the recipe logic without needing
    # to override __init__ (Conan discourages custom __init__ implementations).
    @property
    def matter_folder(self) -> str:
        return str(self.repo_root)

    @property
    def repo_root(self) -> Path:
        return _REPO_ROOT

    def requirements(self):
        self.requires("openthread/[>=3.0.0 <3.0.1, include_prerelease]@silabs", run=True)
        self.requires("multiprotocol/[>=1.0.0 <1.0.1, include_prerelease]@silabs", run=True)
        self.requires("zigbee/[>=9.0.0 <9.0.1, include_prerelease]@silabs", run=True)
        self.requires("bluetooth_le_host/[>=11.0.0 <11.0.1, include_prerelease]@silabs", run=True)
        self.requires("platform_nwp_siwx91x/[>=4.0.0 <4.0.1, include_prerelease]@silabs", run=True)
        self.requires("bluetooth_le_siwx91x/[>=4.0.0 <4.0.1, include_prerelease]@silabs", run=True)
        self.requires("lwip/[>=1.0.0 <1.0.1, include_prerelease]@silabs", run=True)

    def slt_requirements(self):
        req = {}
        req["zap"] = "~"
        req["slc-cli"] = "~"
        return req

    def layout(self):
        pass

    def deploy(self):
        pass

    def export(self):
        pass

    def package_id(self):  # unified content-only id
        self.info.clear()

    def package(self):
        # Define the source folder for the matter component (centralized via property)
        matter_folder = self.matter_folder
        self.output.info("[package] Starting packaging step. Source root: %s" % matter_folder)

        # Define the files to be included in the package
        files_to_package = {"License"}
        extra_files = []
        self.output.info("[package] Seed file set initialized with %d item(s)." % len(files_to_package))

        # Process matter.slce.extra (shared helper)
        extra_info = self._process_slce_extra()
        files_to_package.update(extra_info["extra_files_including_descriptor"])  # includes descriptor itself
        self.output.info(
            "[package] Added %d extra file(s) from matter.slce.extra (including descriptor). Total so far: %d" % (
                len(extra_info["extra_files_including_descriptor"]), len(files_to_package)
            )
        )

        silabs_package_assistant = self.python_requires[
            "silabs_package_assistant"
        ].module

        slce_file = self._get_local_slce_file()
        self.output.info(f"[package] Using SLCE definition: {slce_file}")
        self.output.info("[package] File set before scanning SLCCs: %d" % len(files_to_package))

        files = silabs_package_assistant.find_slc_files_to_release(
            slc_sdk_or_extension_def_file=slce_file,
            desired_qualities=["production", "evaluation", "experimental", "internal"],
            fail_on_missing_files=False,
            include_slcp=False,
            include_slcc=True,
            # Defaults to slce extension ID;
            # SLCCs with slcc:package field set to
            # the package names in desired_packages will be included
            desired_packages=["matter"],
        )
        files_to_package.update(files)
        self.output.info(
            "[package] Added %d SLC-derived file(s). Aggregate set size: %d" % (
                len(files), len(files_to_package)
            )
        )

        files_to_package = {
            file
            for file in files_to_package
            if os.path.exists(file) and not os.path.isdir(file)
        }
        self.output.info(
            "[package] Filtered to existing non-directory paths: %d" % len(files_to_package)
        )

        # Get all .a files from files_to_package and copy them
        static_libraries = {
            file for file in files_to_package if file.endswith(".a")
        }
        files_to_package -= static_libraries
        if static_libraries:
            self.output.info(
                "[package] Identified %d static library file(s) to copy separately." % len(static_libraries)
            )
        else:
            self.output.info("[package] No static libraries detected in file set.")
        for file in static_libraries:
            copy(
                self,
                pattern=file,
                src=matter_folder,
                dst=os.path.join(self.package_folder, "."),
            )
            self.output.info(f"[package] Copied static library: {file}")

        # Copy slc files using silabs_package_assistant
        self.output.info(
            "[package] Copying remaining %d file(s) via silabs_package_assistant.copy_files" % len(files_to_package)
        )
        silabs_package_assistant.copy_files(
            files_to_package=files_to_package,
            src_folder=matter_folder,
            dst_folder=os.path.join(self.package_folder, "."),
        )
        self.output.info("[package] Completed copy of non-library files.")

        if os.path.exists("conan-matter.lock"):
            copy(
                self,
                pattern="conan-matter.lock",
                src=matter_folder,
                dst=os.path.join(self.package_folder, "."),
            )
            self.output.info("[package] Included conan-matter.lock in package.")
        else:
            self.output.info("[package] conan-matter.lock not present; skipping.")
        self.output.info("[package] Generating metadata (component + dependency info)...")
        silabs_package_assistant.generate_metadata(self, files_to_package)
        self.output.success("[package] Packaging phase complete.")

    def build(self):
        pass

    def package_info(self):
        # Reference: https://confluence.silabs.com/pages/viewpage.action?spaceKey=SWARCH&title=Package+Manager%3A+Conan+Metadata+for+SLT+Integration

        # SDK Packages
        self.buildenv_info.append_path(
            "SLC_SDK_PACKAGE_PATH", self.package_folder
        )

    # ------------------------- Helpers -------------------------
    def _process_slce_extra(self, filename: str = "packages/matter/matter.slce.extra") -> dict:
        """Parse matter.slce.extra and collect extra packaging metadata.

        Returns a dictionary with keys:
            extra_files_including_descriptor: set of files (descriptor + validated extra_files)
            git_extra_files: list of additional git export file paths (may be empty)
            git_path_mapping: list of path mapping entries (may be empty or None)

        Missing or malformed YAML gracefully degrades with warnings.
        """
        filename = os.path.join(self.repo_root, filename)
        os.chdir(self.repo_root)
        result = {
            "extra_files_including_descriptor": set(),
            "git_extra_files": [],
            "git_path_mapping": [],
        }
        if not os.path.exists(filename):
            return result

        result["extra_files_including_descriptor"].add(filename)
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception as e:
            self.output.warning(f"Failed to parse {filename}: {e}")
            return result

        # extra_files
        extra_files = data.get("extra_files") or []
        for path in extra_files:
            if os.path.exists(path):
                result["extra_files_including_descriptor"].add(path)
            else:
                self.output.warning(
                    f"matter.slce.extra: referenced extra file missing and skipped: {path}"
                )

        # git extras
        git_extra_files = data.get("git_extra_files") or []
        if git_extra_files:
            result["git_extra_files"] = git_extra_files

        # path mapping
        git_path_mapping = data.get("git_path_mapping") or []
        if git_path_mapping:
            result["git_path_mapping"] = git_path_mapping

        return result

    def _get_local_slce_file(self, filename: str = "matter.slce") -> str:
        """Return relative path to required SLCE definition, raising if missing.

        Keeps logic centralized so build() and package() stay DRY.
        """
        filename = os.path.join(self.repo_root, filename)
        if not os.path.exists(filename):
            raise FileNotFoundError(f"SLCE file not found: {filename}")
        # Maintain previous usage of a relative string path
        return f"{filename}"