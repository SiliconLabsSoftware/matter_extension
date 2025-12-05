#!/usr/bin/env python3

"""
sl_setup_env.py

Environment setup script for Matter project using Silicon Labs Configurator.

This script installs the required tools to create a Matter project using Silicon Labs Configurator.
It also generates a .env file that can be sourced or used to set the needed environment variables for your shell or command prompt.

Tools installed:
  - arm-gcc toolchain
  - slc-cli
  - zap
  - Java
  - ninja
  - Simplicity Commander

Usage:
  python3 sl_setup_env.py [--verbose]
"""

import argparse
import logging
import os
import sys
import tarfile
import dload
import stat
import subprocess
import shutil
import json
import re
from datetime import datetime
from zipfile import ZipFile
from pathlib import Path
from sl_create_new_app import createApp
from script.get_zap_version import get_zap_version


if sys.version_info < (3, 9):
    logging.error("This script requires Python 3.9 or higher!")
    sys.exit(1)


# Full refactor: encapsulate all setup steps in MatterEnvSetup class
class MatterEnvSetup:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.setup_logging()
        self.set_root_paths()
        self.set_platform_vars()
        self.set_tool_urls_and_paths()
        self.MINIMUM_ZAP_REQUIRED = get_zap_version()

    def setup_logging(self):
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(level=level, format='[%(levelname)s] %(message)s')

    def set_root_paths(self):
        if "SILABS_MATTER_ROOT" not in os.environ:
            logging.info("Using default path for Matter root")
            self.silabs_chip_root = Path(__file__).resolve().parents[1]
        else:
            logging.info("Using ENV path for Matter root")
            self.silabs_chip_root = os.environ["SILABS_MATTER_ROOT"]
        self.tools_folder_path = os.path.join(self.silabs_chip_root, "slc", "tools")
        os.makedirs(self.tools_folder_path, exist_ok=True)

    def sync_submodules(self):
        logging.info("Syncing and checking out submodules")
        try:
            subprocess.run(["git", "submodule", "sync"])
            subprocess.run(["git", "submodule", "update", "--init"])
        except Exception as e:
            logging.error(f"Cannot checkout submodules: {e}")
            sys.exit(1)
        logging.info("Submodules checked out successfully\n")

    def set_platform_vars(self):
        platform = sys.platform
        self.platform = platform
        if platform == "win32":
            self._platform = "win"
            self.__platform = "windows"
        elif platform == "darwin":
            self._platform = "mac"
            self.__platform = "mac"
        elif platform == "linux":
            self._platform = platform
            self.__platform = platform
        else:
            logging.error(f"ERROR: Platform {platform} is not supported")
            sys.exit()

    def set_tool_urls_and_paths(self):
        # URLs and paths for all tools, platform-dependent
        p = self.platform
        t = self.tools_folder_path
        r = self.silabs_chip_root
        if p == "win32":
            self.arm_toolchain_url = "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.rel1/binrel/arm-gnu-toolchain-12.2.rel1-mingw-w64-i686-arm-none-eabi.zip?rev=709f3f15b2ee4763b186c10153ee6ca9&hash=8C0761A17A1E4861B96DDB604C177F5B"
            self.java_url = "https://corretto.aws/downloads/resources/21.0.7.6.1/amazon-corretto-21.0.7.6.1-windows-x64-jdk.zip"
            self.commander_path = os.path.join(t, "SimplicityCommander-Windows")
            self.os_name_commander = "Commander_win32"
            self.java_path = os.path.join(r, "slc", "tools", "jdk21.0.7_6")
            self.arm_gcc_dir = os.path.join(t, "gcc")
            self.arm_gcc_download_dir = os.path.join(t, "arm-gnu-toolchain-12.2.rel1-mingw-w64-i686-arm-none-eabi")
            self.ninja_path = os.path.join(t, "ninja", "ninja.exe")
        elif p == "darwin":
            self.arm_toolchain_url = "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.rel1/binrel/arm-gnu-toolchain-12.2.rel1-darwin-arm64-arm-none-eabi.tar.xz?rev=41f9ad86e18d43cf9999c4bada07f7df&hash=C458A8BF74CBA545BDCA38B7FB40AAF5"
            self.java_url = "https://corretto.aws/downloads/resources/21.0.7.6.1/amazon-corretto-21.0.7.6.1-macosx-x64.tar.gz"
            self.commander_path = os.path.join(t, "SimplicityCommander-Mac")
            self.os_name_commander = "Commander_osx"
            self.commander_app_path = os.path.join(self.commander_path, "Commander.app", "Contents", "MacOS")
            self.java_path = os.path.join(r, "slc", "tools", "amazon-corretto-21.jdk")
            self.arm_gcc_dir = os.path.join(t, "arm-gnu-toolchain-12.2.rel1-darwin-arm64-arm-none-eabi")
            self.ninja_path = os.path.join(t, "ninja", "ninja")
        elif p == "linux":
            self.arm_toolchain_url = "https://developer.arm.com/-/media/Files/downloads/gnu/12.2.rel1/binrel/arm-gnu-toolchain-12.2.rel1-x86_64-arm-none-eabi.tar.xz?rev=7bd049b7a3034e64885fa1a71c12f91d&hash=732D909FA8F68C0E1D0D17D08E057619"
            self.java_url = "https://corretto.aws/downloads/resources/21.0.7.6.1/amazon-corretto-21.0.7.6.1-linux-x64.tar.gz"
            self.commander_path = os.path.join(t, "SimplicityCommander-Linux")
            self.os_name_commander = "Commander_linux_x86_64"
            self.java_path = os.path.join(r, "slc", "tools", "amazon-corretto-21.0.7.6.1-linux-x64")
            self.commander_app_path = os.path.join(self.commander_path, "commander")
            self.arm_gcc_dir = os.path.join(t, "arm-gnu-toolchain-12.2.rel1-x86_64-arm-none-eabi")
            self.ninja_path = os.path.join(t, "ninja", "ninja")

        '''
        https://www.silabs.com/documents/public/software/slt-cli-1.0.1-mac-x64.zip
        https://www.silabs.com/documents/public/software/slt-cli-1.0.1-linux-x64.zip
        https://www.silabs.com/documents/public/software/slt-cli-1.0.1-windows-x64.zip
        '''
        self.slt_cli_url = f"https://www.silabs.com/documents/public/software/slt-cli-1.0.1-{self.__platform}-x64.zip"
        self.slt_cli_path = os.path.join(self.tools_folder_path, "slt")
        self.sisdk_root = os.path.join(r, "third_party", "simplicity_sdk")
        self.wiseconnect_root = os.path.join(r, "third_party", "wifi_sdk")
        self.slc_cli_path = os.path.join(r, "slc", "tools", "slc_cli")
        self.zap_path = os.path.join(r, "slc", "tools", "zap")
        self.arm_toolchain_path = os.path.join(self.arm_gcc_dir, "bin")

    def download_and_extract_slt_cli(self):
        if not os.path.isfile(self.slt_cli_path):
            logging.info(f"Downloading and unzipping slt-cli ...{self.slt_cli_url}")
            slt_zip_path = os.path.join(self.tools_folder_path, "slt.zip")
            dload.save(self.slt_cli_url, slt_zip_path)
            with ZipFile(slt_zip_path, 'r') as zObject:
                zObject.extractall(path=self.tools_folder_path)
            os.remove(slt_zip_path)
            os.chmod(self.slt_cli_path, stat.S_IEXEC)
        
        update_cmd = [self.slt_cli_path,"update","--self"]
        subprocess.run(update_cmd)

    def download_and_extract_zap(self, install_without_checking=False):
        ## Using Non-SLT zap as we often need newer zap than the one from SLT
        zap_url = f"https://github.com/project-chip/zap/releases/download/{self.MINIMUM_ZAP_REQUIRED}/zap-{self._platform}-x64.zip"
        if (not os.path.isfile(os.path.join(self.zap_path, "zap-cli")) and not os.path.isfile(os.path.join(self.zap_path, "zap.exe"))) or install_without_checking:
            logging.info("Downloading and unzipping zap ...")
            if self.platform == "darwin":
                dload.save(zap_url, self.zap_path + ".zip")
                command = f"unzip {self.zap_path}.zip -d {self.zap_path}"
                os.system(f"{command} > /dev/null 2>&1")
                os.remove(self.zap_path + ".zip")
                st = os.stat(os.path.join(self.zap_path, "zap-cli"))
                os.chmod(os.path.join(self.zap_path, "zap-cli"), st.st_mode | stat.S_IEXEC)
                zap_root = os.path.join(self.zap_path, "zap.app", "Contents", "MacOS", "zap")
                st = os.stat(zap_root)
                os.chmod(zap_root, st.st_mode | stat.S_IEXEC)
            elif self.platform == "linux":
                dload.save_unzip(zap_url, os.path.join(self.tools_folder_path, "zap"), delete_after=True)
                st = os.stat(os.path.join(self.tools_folder_path, "zap", "zap-cli"))
                os.chmod(os.path.join(self.tools_folder_path, "zap", "zap-cli"), st.st_mode | stat.S_IEXEC)
                st = os.stat(os.path.join(self.tools_folder_path, "zap", "zap"))
                os.chmod(os.path.join(self.tools_folder_path, "zap", "zap"), st.st_mode | stat.S_IEXEC)
            elif self.platform == "win32":
                dload.save_unzip(zap_url, os.path.join(self.tools_folder_path, "zap"), delete_after=True)
        else:
            logging.info("zap already installed")

    def check_and_update_zap_version(self):
        zap = os.path.join(self.zap_path, "zap-cli")
        command = f"{zap} --version"
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        installed_zap_version = re.search(r"Version:\s*([\d.]+)", output).group(1)
        min_zap = self.MINIMUM_ZAP_REQUIRED.replace("v", "").replace("-nightly", "")
        date_format = "%Y.%m.%d"
        installed_zap_version = datetime.strptime(installed_zap_version, date_format)
        min_zap = datetime.strptime(min_zap, date_format)
        if installed_zap_version < min_zap:
            logging.warning(
                f"Installed zap version is {installed_zap_version} which is less than Minimum Required level of {min_zap}")
            try:
                logging.info(f"Deleting old version of zap located at {self.zap_path}")
                shutil.rmtree(self.zap_path)
                self.download_and_extract_zap(True)
            except Exception as e:
                logging.error(
                    f"Error while deleting zap located at {self.zap_path}: {e}\nUsing older version of zap may lead to errors.")
    
    def write_env_file(self):
            env_path = os.path.expanduser(os.path.join(self.tools_folder_path, ".env"))
            arm_gcc_bin = os.path.join(self.paths.get('gcc-arm-none-eabi'), "bin")

            if self.platform == "darwin":
                java_path = os.path.join(self.paths.get('java21'), "jre", "Contents", "Home")
            else:
                java_path = os.path.join(self.paths.get('java21'), "jre")

            with open(env_path, "w") as outfile:
                outfile.write(f"STUDIO_ADAPTER_PACK_PATH={self.zap_path}\n")
                outfile.write(f"ARM_GCC_DIR={self.paths.get('gcc-arm-none-eabi')}\n")
                outfile.write(f"JAVA_HOME={self.paths.get('java21')}\n")
                outfile.write(f"ZAP_INSTALL_PATH={self.zap_path}\n")
                outfile.write(
                    f"TOOLS_PATH={arm_gcc_bin}:{self.paths.get('slc-cli')}:{os.path.join(java_path, 'bin')}:{self.paths.get('commander')}:\n")
                outfile.write(f"silabs_chip_root={self.silabs_chip_root}\n")
                outfile.write(f"NINJA_EXE_PATH={self.paths.get('ninja')}\n")
                outfile.write(f"SISDK_ROOT={self.sisdk_root}\n")
                outfile.write(f"WISECONNECT_ROOT={self.wiseconnect_root}\n")

    def trust_extensions(self):
        with open(os.path.expanduser(os.path.join(self.tools_folder_path, "environment_variables_vscode.txt")), "w") as outfile:
            outfile.write(f"NINJA_EXE_PATH = {self.paths.get('ninja')}\n")
        logging.info("\nEnvironment setup completed successfully")

    
    def install_tools(self,tool):
        tool_dir = subprocess.run([self.slt_cli_path, "where", tool], capture_output=True, text=True).stdout.strip()
        if not tool_dir:
            logging.info(f"Downloading {tool}")
            tool_install_command = [self.slt_cli_path, "install", tool]
            subprocess.run(tool_install_command)
            tool_dir = subprocess.run([self.slt_cli_path, "where", tool], capture_output=True, text=True).stdout.strip()
        logging.info(f"{tool} = {tool_dir}")
        return tool_dir

    def setup_tools(self):
        tools_list = ["slc-cli","java21","gcc-arm-none-eabi","commander","ninja"]
        self.paths = {}
        for tool in tools_list:
            self.paths[tool] = self.install_tools(tool)
        print(self.paths)
        self.download_and_extract_zap()
        self.check_and_update_zap_version()
        

    def run_setup(self):
        self.sync_submodules()
        self.download_and_extract_slt_cli()
        self.setup_tools()
        self.write_env_file()

def main():
    parser = argparse.ArgumentParser(description="Setup environment for Matter project using Silicon Labs Configurator.")
    parser.add_argument('--verbose', action='store_true', help='Enable verbose (debug) logging')
    args = parser.parse_args()
    env_setup = MatterEnvSetup(verbose=args.verbose)
    env_setup.run_setup()


if __name__ == "__main__":
    main()
