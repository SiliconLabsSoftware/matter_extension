####Imports
import subprocess
import sys
import json
import os
import glob
from pathlib import Path
import shutil


# To be run in the root of the matter folder

# Defines
git_remove_submodules_commands = ["git rm ./third_party/{path}/repo*", "rm -rf .git/modules/{path}", "git config --remove-section submodule.{path}/repo*", "rm -rf ./third_party/{path}"]
git_submodule_to_remove = ["ameba", "bouffalolab", "cyw30739_sdk", "mbed-os-cypress-capsense-button", "mbed-mcu-boot", "mbed-os", "mbed-os-posix-socket", "nxp", "p6", "qpg_sdk", "simw-top-mini", "telink_sdk", "ti_simplelink_sdk", "tizen"]
folder_to_remove = ["Ameba", "CYW30739", "ESP32", "P6", "Tizen", "bouffalolab", "cc13x2_26x2", "cc32xx", "nrfconnect", "nxp", "qpg", "telink"]
examples_to_remove = folder_to_remove + ["mbed", "cc13x2x7_26x2x7"]

def remove_submodules():
    for module_name in git_submodule_to_remove:
        print("removing module " + module_name)
        for command in git_remove_submodules_commands:

            c = command.format(path=module_name)
            print("Running : " + c)
            try:
                subprocess.check_output(c, shell=True)
            except subprocess.CalledProcessError as e:
                print(e.output)

    try:
        subprocess.check_output("git commit -a -m \"Remove Submodules\"", shell=True)
    except subprocess.CalledProcessError as e:
        exit(1)


def clean_platform():
    for folder in folder_to_remove:
        shutil.rmtree("./src/platform/{name}".format(name=folder))

    try:
        subprocess.check_output("git commit -a -m \"Remove Platform Folders\"", shell=True)
    except subprocess.CalledProcessError as e:
        exit(1)

def clean_examples():
    for example in glob.glob("./examples/*"):
        for platform in glob.glob(example + "/*"):
            for competitor in map(str.lower, examples_to_remove):
                if competitor in platform:
                    if os.path.isdir(platform):
                        shutil.rmtree(platform)
                    else:
                        os.remove(platform)
    try:
        subprocess.check_output("git commit -a -m \"Remove Competitors examples\"", shell=True)
    except subprocess.CalledProcessError as e:
        exit(1)


remove_submodules()
clean_platform()
clean_examples()

