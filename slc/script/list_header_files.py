import os
import sys
import re
import yaml

'''
    This script is to be ran after gen_components.py has been ran to generate the core Matter components. It will modify
    the components within slc/component/matter-core-sdk to explicitly list their included header files using the
    "file_list:" SLC specification. This is needed when performing the "copy-contents" step on project generation.

    This script recursviely searches the provided directory for any .slcc files. It removes any "include:" section
    and populates the "include:" section with a list of any header files within the directories that
    the .c or .cpp files under the "source:" section reside in

    As of Matter Extension v2.2.0-1.2, the following manual code changes must be performed after the script has ran:
        
        List the header files withinin the directories shown in the corresponding component
            libclusterobjects.slcc  --->   src/app/ids
            libchipdatamodel.slcc   --->   src/app/data-model
            dnssd.slcc              --->   src/lib/dnssd/platform
            app_common.slcc         --->   src/app/util 

        The file_list entry should include the directory in which the file lives (not just the file).
        For example, while adding the .h files in app_common.slcc the format should be:
        -   path: src/app
            file_list:
            -   path: util/attribute-table.h
'''

rootDir  = os.getcwd()
dirToSearch = rootDir + "/slc/component/matter-core-sdk"

# These directories do not include any source files within the components
includeWholeDir =    [rootDir + "/src/include/platform",
                      rootDir + "/src/include/platform/internal",
                      rootDir + "/src/platform/logging",
                      rootDir + "/src/include/platform/internal/testing"]

# These files are manually maintained and not generated via this script
manualFiles = ["matter_nlassert.slcc", "matter_includes.slcc", "matter_nlio.slcc"]

# Returns dictionary of slcc files to included header files
def find_slcc_files(directory):
    if not os.path.exists(directory):
        raise ValueError("Directory does not exist.")
 
    slccFiles = []
    # Recursively search the directory for .slcc files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".slcc"):
                slccFiles.append(os.path.join(root, file)) 
    return slccFiles


# Returns include directories in the provided slcc file
def get_included_dirs(file_path):
    includeDirectories = []
    try:
        with open(file_path, 'r') as file:
            # Add directories of any source files within the .slcc to search
            for line in file:
                line = line.strip()
                line = line.split(" ")[-1]
                line = rootDir + "/" + line
                if line.endswith(".c") or line.endswith(".cpp"):
                    includeDirectories.append(os.path.dirname(line))
    except:
        pass
    
    return includeDirectories

def add_key_value_to_yaml(file_path: str, foundIncludesDirs):
    try:
        # Open the YAML file for reading and writing
        with open(file_path, 'r+') as file:
            yaml_data = yaml.safe_load(file)
 
            # Check if the outer key exists in the YAML data
            if "include" not in yaml_data:
                yaml_data["include"] = []

            relFileName = file_path.split("/")[-1]

            # Do not change manual files
            if relFileName in manualFiles:
                return
                
            print("\nAdding includes for: " + relFileName)

            # Add whole include directory to efr32 components 
            if (relFileName == "efr32.slcc" or relFileName == "efr32_wifi.slcc"):
                for dir in includeWholeDir:
                    relativeDir = dir.replace(rootDir + "/", '')
                    yaml_data["include"].append({"path":relativeDir})
                    print("Adding directory: " + relativeDir)
                    file_list = []
                    # Add whole include directory to efr32 components 
                    for file_name in os.listdir(dir):
                        if file_name.endswith(".h") or file_name.endswith(".hpp") or file_name.endswith(".ipp"):
                            file_list.append({"path":file_name})
                    yaml_data["include"].append({"file_list":file_list})

            # Add include files for the given directories
            for dir in foundIncludesDirs:
                if os.path.exists(dir):
                    relativeDir = dir.replace(rootDir + "/", '')
                    yaml_data["include"].append({"path":relativeDir})
                    print("Adding directory: " + relativeDir)
                    file_list = []
                    for file_name in os.listdir(dir):
                            if file_name.endswith(".h") or file_name.endswith(".hpp") or file_name.endswith(".ipp"):
                                file_list.append({"path":file_name})
                    yaml_data["include"].append({"file_list":file_list})
 
            file.seek(0)
            yaml.dump(yaml_data, file, Dumper=yaml.SafeDumper, default_flow_style=False, indent=4)
            file.truncate()
 
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

def recursive_replace_string(directory_path: str):

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
 
            with open(file_path, 'r') as f:
                content = f.read()
                new_content = content.replace("-   file_list:", "    file_list:")
 
            with open(file_path, 'w') as f:
                f.write(new_content)

# Main function
slccFiles = find_slcc_files(dirToSearch)

for slccFile in slccFiles:
    foundHeaders = []
    foundIncDirs = get_included_dirs(slccFile)
    # Add file paths to slcc files
    add_key_value_to_yaml(slccFile, set(foundIncDirs))

# Fix Formatting
recursive_replace_string(dirToSearch)
