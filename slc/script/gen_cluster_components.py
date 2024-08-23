#!/usr/bin/env python3

#This script is creates cluster components from the src/app/clusters directory
#USAGE : python3 slc/script/gen_cluster_components.py
#"Warning!! Check for manual changes in matter_icd_management.slcc, matter_ota_requestor.slcc, matter_air_quality.slcc
# TODO: Update script to include src/app/icd files

import os
import pathlib
import shutil
import json

root  = str(pathlib.Path(os.path.realpath(__file__)).parent.parent.parent)
os.chdir(root)
cluster_dir_path = "src/app/clusters"
cluster_xml_path = ["src/app/zap-templates/zcl/data-model/chip" , "src/app/zap-templates/zcl/data-model/draft"] 

# Create a dictionary of all the clusters from Cluster_Dir_Path with the headers, source files,
# and if it is a server cluster or not
cluster_data = {}

subdirs = os.listdir(cluster_dir_path)

for subdir in subdirs:
    headers = []
    sources = []
    clustercomponentname = ""
    clustername = ""
    clientOrServer = ""

    for file in os.listdir(os.path.join(cluster_dir_path, subdir)):
        # Check if the file is a header file
        if file.endswith(".h") or file.endswith(".hpp") or file.endswith(".ipp"):
            headers.append(file)
        # Check if the file is a source file
        elif file.endswith(".c") or file.endswith(".cpp"):
            sources.append(os.path.join(cluster_dir_path, subdir, file))
        
        # Replace hyphens with underscores in the subdirectory name to form the cluster component name
        clustercomponentname = subdir.replace("-", "_")
        clustername = clustercomponentname
        
        # Determine if the cluster is a server or client
        if "server" in clustercomponentname:
            clientOrServer = " Server"
            clustername = clustercomponentname.replace("_server", "")
        if "client" in clustername:
            clientOrServer = " Client"
            clustername = clustercomponentname.replace("_client", "")
        
        # Set the include path for the cluster
        include = os.path.join(cluster_dir_path, subdir)

    # If a cluster component name is found and there are source or header files
    if clustercomponentname != "":
        if len(sources) + len(headers) > 0:
            # Populate the cluster data dictionary with the relevant information
            cluster_data[clustercomponentname] = {}
            cluster_data[clustercomponentname]["clustername"] = clustername
            cluster_data[clustercomponentname]["headers"] = headers
            cluster_data[clustercomponentname]["include"] = include
            cluster_data[clustercomponentname]["sources"] = sources
            cluster_data[clustercomponentname]["clientOrServer"] = clientOrServer

# Get the categories of clusters through the chip data
# Create list of clusternames
clusternames = []
for clustercomponentname in cluster_data.keys():
    # Append each cluster name to the clusternames list
    clusternames.append(cluster_data[clustercomponentname]["clustername"])

namecategories = {}
#create dictionary with categories and names mapped to clustername
for xml_path in cluster_xml_path:
    for xmlfile in os.listdir(xml_path):
        filename = xmlfile.split(".")[0]

        # Handle special cases for filename differences
        if "ota" in filename:
            clustername = "ota_requestor"
        elif "occupancy" in filename:
            clustername = "occupancy_sensor"
        elif "test" in filename:
            clustername = "test_cluster"
        elif "scene" in filename:
            clustername = "scenes"
        elif "onoff" in filename:
            clustername = "on_off"
        elif "binding" in filename:
            clustername = "bindings"
        elif "laundry-washer" in filename:
            clustername = "laundry_washer_controls"
        else:
            # Replace specific substrings to standardize the cluster name
            clustername = filename.replace("-cluster", "").replace("-", "_")

        # Skip if the clustername is not in the clusternames list
        if clustername not in clusternames:
            continue

        # Construct the full file path
        filepath = os.path.join(root, xml_path, xmlfile)
        with open(filepath) as f:
            data = f.read()
            content = data.split("\n")
            category = ""
            name = ""
            for line in content:
                # Extract the category from the <domain> tag
                if "<domain>" in line:
                    category = line.split("<domain>")[-1].split("<")[0]
                    # Standardize the category if it contains "Measurement"
                    if "Measurement" in category:
                        category = "Measurement"
                # Extract the name from the <name> tag
                if "<name>" in line:
                    name = line.split("<name>")[-1].split("<")[0]
            # If both category and name are found, store them in the dictionary
            if category != "" and name != "":
                if "ota" in clustername:
                    namecategories[clustername] = {}
                    namecategories[clustername]["category"] = category
                    namecategories[clustername]["name"] = name
                    clustername = "ota_provider"
                    namecategories[clustername] = {}
                    namecategories[clustername]["category"] = category
                    namecategories[clustername]["name"] = name.replace("Requestor", "Provider")
                else:
                    namecategories[clustername] = {}
                    namecategories[clustername]["category"] = category
                    namecategories[clustername]["name"] = name
            else :
                namecategories[clustername] = {}
                namecategories[clustername]["category"] = "General"
                namecategories[clustername]["name"] = clustername

#add category and name from xml to the cluster_data           
#For the except condition check the name of the xml files and update the above loop to match clustername
for clustercomponentname in cluster_data.keys():
    try:
        clustername = cluster_data[clustercomponentname]["clustername"]
        cluster_data[clustercomponentname]["category"] = namecategories[clustername]["category"]
        cluster_data[clustercomponentname]["name"] = namecategories[clustername]["name"]
    except:
        print("xml not found for", clustercomponentname)
# Create slcc from the cluster_data dictionary
component_dir = os.path.join(root, "slc", "component", "matter-clusters")
shutil.rmtree(component_dir, ignore_errors=True)
os.makedirs(component_dir)

for clustercomponentname in sorted(cluster_data.keys()):
    filedata = [""]
    clustername = cluster_data[clustercomponentname]["clustername"]
    
    try:
        # Special cases for filename differences
        if "client" in clustername:
            category = cluster_data[clustername.replace("_client", "")]["category"]
        else:
            category = cluster_data[clustercomponentname]["category"]
    except:
        category = "General"
    
    category_str = "category: Clusters|{}".format(category)
    filedata.append(category_str)
    try:
        name = cluster_data[clustercomponentname]["name"].replace("_", " ").replace("matter ", "")
    except:
        name = clustername.replace("_", " ").replace("matter ", "").title()
    if "ota" in clustername:
        name = name.replace('Ota', 'OTA')
    
    label = "{}{} Cluster".format(name, cluster_data[clustercomponentname]['clientOrServer'])
    description = "description: >\n  Implementation of the {}.".format(label)
    description += f"\n  The user has to enable the {label} in the Zigbee Cluster Configurator (ZAP) in order to enable this functionality."
    filedata.append(description)
    
    if cluster_data[clustercomponentname]['clientOrServer'] == " Client":
        clustername = clustername + "_client"
    
    id_str = "matter_" + clustername
    id = "id: {}".format(id_str)
    filedata.append(id)
    filedata.append("package: Matter")
    
    label_str = "label: {}".format(label)
    filedata.append(label_str)
    # special case as only component with experimental quality
    if clustername == "scenes":
        filedata.append("quality: experimental")
    else:
        filedata.append("quality: production")

    filedata.append("metadata:")
    filedata.append("  sbom:")
    filedata.append('    license: "Apache 2.0"')
    filedata.append("provides:")
    provides = "  - name: {}".format(id_str)
    filedata.append(provides)

    if len(cluster_data[clustercomponentname]["sources"]) > 0:
        filedata.append("source:")
        for src in cluster_data[clustercomponentname]["sources"]:
            path = "  - path: {}".format(src)
            filedata.append(path)

    if len(cluster_data[clustercomponentname]["headers"]) > 0:
        filedata.append("include:")
        path = "  - path: {}".format(cluster_data[clustercomponentname]["include"])
        filedata.append(path)
        filedata.append("    file_list:")
        for header in cluster_data[clustercomponentname]["headers"]:
            path = "      - path: {}".format(header)
            filedata.append(path)

    filedata.append("template_contribution:")
    filedata.append("  - name: component_catalog")
    value = "    value: {}".format(id_str)
    filedata.append(value)

    # special cases for component with specific defines
    if clustername == "time_synchronization":
        filedata.append("define:")
        filedata.append("  - name: TIME_SYNC_ENABLE_TSC_FEATURE")
        filedata.append("    value: 0")

    clustername = "matter_" + clustername
    with open(component_dir + "/{}.slcc".format(clustername), 'w') as f:
        f.write("\n".join(filedata))
        # print("created = ","slc/component/matter-clusters/{}.slcc".format(clustername))



# Create the cluster-to-component-dependencies.json
jsonfilepath = os.path.join(root, "src/app/zap-templates/cluster-to-component-dependencies.json")
lst = []

# Iterate over each cluster component name in the cluster_data dictionary
for clustercomponentname in cluster_data.keys():
    # Initialize an empty dictionary to store the dependencies for the current cluster component
    dependanciesDic = {}
    
    # Get the cluster name for the current cluster component
    clustername = cluster_data[clustercomponentname]["clustername"]
    
    try:
        # Try to get the cluster code by converting the name to lowercase
        clusterCode = cluster_data[clustercomponentname]["name"].lower()
    except:
        # If an exception occurs, generate the cluster code by replacing parts of the cluster name
        clusterCode = clustername.replace("matter_", "")
        clusterCode = clusterCode.replace("_", " ")
    
    # Determine if the cluster is a server or client and adjust the cluster code accordingly
    if cluster_data[clustercomponentname]["clientOrServer"] == "" or cluster_data[clustercomponentname]["clientOrServer"] == " Server":
        clusterCode = clusterCode + "-server"
    else:
        clusterCode = clusterCode + "-client"
        clustername = clustername + "_client"
    
    # Create the value string for the dependency
    value_str = "%extension-matter%matter_" + clustername
    
    # Special case handling for OTA requestor
    if "matter_ota_requestor" in value_str:
        clusterCode = clusterCode.replace("provider", "requestor")
    
    # Add the cluster code and value to the dependencies dictionary
    dependanciesDic["clusterCode"] = clusterCode
    value = [value_str]
    dependanciesDic["value"] = value
    
    # Append the dependencies dictionary to the list
    lst.append(dependanciesDic)

# Convert the list of dependencies to a JSON object with indentation for readability
json_object = json.dumps(lst, indent=2)

# Write the JSON object to the specified file
with open(jsonfilepath, "w") as outfile:
    outfile.write(json_object)

print("Warning!! Check for manual changes in matter_icd_management.slcc, matter_ota_requestor.slcc, matter_air_quality.slcc")
print("Check by running git diff on the above files and any other files that may have been manually changed")