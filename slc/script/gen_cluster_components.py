#!/usr/bin/env python3

#This script is creates cluster components from the src/app/clusters directory
#USAGE : python3 slc/script/gen_cluster_components.py
#Check for manual changes in matter_color_control.slcc, matter_icd_management.slcc, matter_level_control.slcc,matter_on_off.slcc

import os
import pathlib
import shutil

root  = str(pathlib.Path(os.path.realpath(__file__)).parent.parent.parent)
os.chdir(root)
cluster_dir_path = "src/app/clusters"
cluster_xml_path = ["src/app/zap-templates/zcl/data-model/chip" , "src/app/zap-templates/zcl/data-model/draft"] 

#Create a dictionary of all the clusters from Cluster_Dir_Path with the headers , source files
# and if it is a server cluster or not
cluster_data = {}
for path, subdirs, files in os.walk(cluster_dir_path):
    headers = []
    sources = []
    clustercomponentname = ""
    clustername =""
    clientOrServer = ""
    for name in files:
        clustercomponentname = path.split("/")[-1].replace("-","_")
        clustername = clustercomponentname
        # check if the cluster is server cluster
        if "server" in clustercomponentname:
            clientOrServer = " Server"
            clustername = clustercomponentname.replace("_server","")
        if "client" in clustername:
            clientOrServer = " Client"
            clustername = clustercomponentname.replace("_client","")
        include = path
        if name.endswith(".h"):
            headers.append(name)
        elif name.endswith(".c") or name.endswith(".cpp"):
            sources.append(os.path.join(path,name))
    if clustercomponentname !="":
        if len(sources)+len(headers)>0:
            cluster_data[clustercomponentname] = {}
            cluster_data[clustercomponentname]["clustername"] = clustername
            cluster_data[clustercomponentname]["headers"] = headers
            cluster_data[clustercomponentname]["include"] = include
            cluster_data[clustercomponentname]["sources"] = sources
            cluster_data[clustercomponentname]["clientOrServer"]  = clientOrServer

#get the categories of clusters through the chip data
#create list of clusternames
clusternames = []
for clustercomponentname in cluster_data.keys():
    clusternames.append(cluster_data[clustercomponentname]["clustername"])

namecategories = {}

#create dictionary with categories and names mapped to clustername
for xml_path in cluster_xml_path:
    for xmlfile in os.listdir(xml_path):
        filename = xmlfile.split(".")[0]

        #special cases for filename differences
        if "ota" in filename:
            clustername = "ota_provider"
        elif "occupancy" in filename:
            clustername = "occupancy_sensor"
        elif "test" in filename:
            clustername = "test_cluster"
        elif "scene" in filename:
            clustername = "scenes"
        elif "onoff" in filename:
            clustername = "on_off"
        elif "laundry" in filename:
            clustername = "laundry_washer_controls"
        elif "binding" in filename:
            clustername = "bindings"
        else:
            clustername = filename.replace("-cluster","").replace("-","_")

        if clustername not in clusternames:
            continue
                
        filepath = os.path.join(root,xml_path,xmlfile)
        with open(filepath) as f:
            data = f.read()
            content = data.split("\n")
            category = ""
            name = ""
            for line in content:
                if "<domain>" in line:
                    category = line.split("<domain>")[-1].split("<")[0]
                    if "Measurement" in category: 
                        category = "Measurement"
                if "<name>" in line:
                    name = line.split("<name>")[-1].split("<")[0]
                if category!="" and name!="":
                    namecategories[clustername] = {}
                    namecategories[clustername]["category"] = category
                    namecategories[clustername]["name"] = name
                    break

#add category and name from xml to the cluster_data           
#For the except condition check the name of the xml files and update the above loop to match clustername
for clustercomponentname in cluster_data.keys():
    try:
        clustername = cluster_data[clustercomponentname]["clustername"]
        if "ota" in clustername:
            clustername = "ota_provider"
        cluster_data[clustercomponentname]["category"] = namecategories[clustername]["category"]
        cluster_data[clustercomponentname]["name"] = namecategories[clustername]["name"]
    except:
        print("xml not found for ",clustercomponentname)

#create slcc from the cluster_data dictionary
component_dir = os.path.join(root,"slc","component","matter-clusters")
shutil.rmtree(component_dir, ignore_errors=True)
os.makedirs(component_dir)
for clustercomponentname in sorted(cluster_data.keys()):
    filedata = [""]
    clustername = cluster_data[clustercomponentname]["clustername"]
    try:
        #special cases for filename differences
        if "ota" in clustername:
            category = cluster_data["ota_provider"]["category"]
        elif "client" in clustername:
            category = cluster_data[clustername.replace("_client","")]["category"]
        else:
            category = cluster_data[clustercomponentname]["category"]
    except:
        category="General"
    category_str = "category: Clusters|{}".format(category)
    filedata.append(category_str)
    name = clustername.replace("_"," ").replace("matter ","").title()
    if "Ota" in name:
        name = name.replace("Ota","OTA")
    label = "{}{} Cluster".format(name,cluster_data[clustercomponentname]['clientOrServer'])
    description = "description: >\n  Implementation of the {}.".format(label)
    description += f"\n  The user has to enable the {label} in the Zigbee Cluster Configurator (ZAP) in order to enable this functionality."
    filedata.append(description)
    if cluster_data[clustercomponentname]['clientOrServer'] == " Client":
        clustername = clustername+"_client"
    id_str = "matter_"+clustername
    id = "id: {}".format(id_str)
    filedata.append(id)
    filedata.append("package: Matter")
    label_str = "label: {}".format(label)
    filedata.append(label_str)
    #special case as only component with experimental quality
    if clustername == "scenes":
        filedata.append("quality: experimental")
    else:
        filedata.append("quality: production")
    filedata.append("provides:")
    provides = "  - name: {}".format(id_str)
    filedata.append(provides)
    if len(cluster_data[clustercomponentname]["sources"])>0:
        filedata.append("source:")
        for src in cluster_data[clustercomponentname]["sources"]:
            path = "  - path: {}".format(src)
            filedata.append(path)
    if len(cluster_data[clustercomponentname]["headers"])>0:
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
    #special cases as only component with a define
    if clustername=="time_synchronization":
        filedata.append("define:")
        filedata.append("  - name: TIME_SYNC_ENABLE_TSC_FEATURE")
        filedata.append("    value: 0")
    clustername = "matter_"+clustername
    with open(component_dir+"/{}.slcc".format(clustername), 'w') as f:
        f.write("\n".join(filedata))
        # print("created = ","slc/component/matter-clusters/{}.slcc".format(clustername))



#Create the cluster-to-component-dependemcies.json
import json
jsonfilepath = os.path.join(root,"src/app/zap-templates/cluster-to-component-dependencies.json")
lst = []
for clustercomponentname in cluster_data.keys():
    dependanciesDic = {}
    clustername = cluster_data[clustercomponentname]["clustername"]
    try:
        clusterCode = cluster_data[clustercomponentname]["name"].lower()
    except:
        clusterCode = clustername.replace("matter_","")
        clusterCode = clusterCode.replace("_"," ")
    if cluster_data[clustercomponentname]["clientOrServer"] == "" or cluster_data[clustercomponentname]["clientOrServer"] == " Server":
        clusterCode = clusterCode+"-server"
    else:
        clusterCode = clusterCode+"-client"
        clustername = clustername+"_client"
    value_str = "%extension-matter%matter_"+clustername
    if "matter_ota_requestor" in value_str:
        clusterCode = clusterCode.replace("provider","requestor")
    dependanciesDic["clusterCode"] = clusterCode
    value = [ value_str ]
    dependanciesDic["value"] = value
    lst.append(dependanciesDic)
json_object = json.dumps(lst, indent=2)
with open(jsonfilepath, "w") as outfile:
    outfile.write(json_object)