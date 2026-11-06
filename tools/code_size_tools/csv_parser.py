#!/usr/bin/env python3
"""
CSV Parser - Parse code size data from CSV files.

This module provides functionality to parse code size CSV files and extract
categorized data for analysis.
"""

import csv
from pathlib import Path
from typing import Dict, List, Tuple

# Pattern-based category mappings
# Patterns are checked in order, first match wins
CATEGORY_PATTERNS: List[Tuple[str, str]] = [
    ("third_party/matter_sdk/src/app/clusters/", "Matter Data Model"),
    ("third_party/matter_sdk/src/platform/silabs", "Matter Silabs Abstraction Impl"),
    ("third_party/matter_sdk/examples", "Matter Examples Code"),
    ("util/third_party/mbedtls/", "MBedTLS"),
    ("third_party/mbedtls/library/", "MBedTLS"),
    ("util/third_party/freertos", "FreeRTOS"),
    ("SIMULATED EEPROM STORAGE", "NVM"),
    ("examples/", "Matter Examples Code"),
]

# Fallback category mappings based on File Name field
# Used when both Path In Source and UC Category 1 are empty
FILENAME_CATEGORY_PATTERNS: List[Tuple[str, str]] = [
    ("obj/third_party/connectedhomeip/src/platform/silabs/", "Matter Silabs Abstraction Impl"),
    ("obj/third_party/connectedhomeip/src/app/clusters/", "Matter Data Model"),
    ("obj/third_party/connectedhomeip/src/app/common/lib/libClusterObjects.a", "Matter Data Model"),
    ("obj/third_party/connectedhomeip/src/", "Matter"),
    ("arm-none-eabi/lib", "C/C++ Standard Library"),
    ("silabs-", "Matter Data Model"),
    ("multi-sensor", "Matter Data Model"),
    ("-common.", "Matter Examples Code"),
    ("util/third_party/openthread", "OpenThread"),
    ("util/third_party/openthread", "OpenThread"),
    ("third_party/connectedhomeip/src/app/clusters/", "Matter Data Model"),
    ("libopenthread-", "OpenThread"),
    ("src/credentials/lib/libCredentials.a", "Matter"),
    ("libCHIP.a", "Matter"),
    ("connectedhomeip/.environment/cipd/packages/arm/bin/", "C/C++ Standard Library"),
    ("sdk-copies/protocol/bluetooth", "Bluetooth"),
    ("sdk.", "Platform"),
    ("MessageDef.", "Matter"),
]

def get_category_from_filename(file_name: str) -> str:
    mbedtls_file_names = [
        "block_cipher.c",
        "hmac_drbg.c",
        "psa_crypto_ecp.c",
        "error.c",
        "mbedtls_ccm.c",
        "mbedtls_cmac.c",
        "mbedtls_ecdsa_ecdh.c",
        "mbedtls_sha.c",
        "sl_entropy_hardware.c",
        "sl_mbedtls.c",
        "sl_psa_crypto.c",
        "sli_psa_crypto.c",
        "aes.c",
        "asn1parse.c",
        "asn1write.c",
        "base64.c",
        "bignum.c",
        "bignum_core.c",
        "ccm.c",
        "cipher.c",
        "cipher_wrap.c",
        "cmac.c",
        "constant_time.c",
        "ecdh.c",
        "ecdsa.c",
        "ecjpake.c",
        "ecp.c",
        "ecp_curves.c",
        "hkdf.c",
        "md.c",
        "oid.c",
        "pem.c",
        "pk.c",
        "pk_ecc.c",
        "pk_wrap.c",
        "pkcs5.c",
        "pkparse.c",
        "pkwrite.c",
        "platform.c",
        "platform_util.c",
        "psa_crypto.c",
        "psa_crypto_aead.c",
        "psa_crypto_cipher.c",
        "psa_crypto_client.c",
        "psa_crypto_driver_wrappers_no_static.c",
        "psa_crypto_hash.c",
        "psa_crypto_mac.c",
        "psa_crypto_rsa.c",
        "psa_crypto_se.c",
        "psa_crypto_slot_management.c",
        "psa_crypto_storage.c",
        "psa_util.c",
        "sha256.c",
        "ssl_cache.c",
        "ssl_ciphersuites.c",
        "ssl_client.c",
        "ssl_cookie.c",
        "ssl_msg.c",
        "ssl_ticket.c",
        "ssl_tls.c",
        "ssl_tls12_client.c",
        "ssl_tls12_server.c",
        "threading.c",
        "x509.c",
        "x509_create.c",
        "x509_crl.c",
        "x509_crt.c",
        "x509_csr.c",
        "x509write_crt.c",
        "x509write_csr.c",
        ]
    freeRTOS_file_names = [
        "list.c.o",
        "queue.c.o",
        "timers.c.o",
        "tasks.c.o",
        "port.c.o",
        "tick_power_manager.c.o",
        "portasm.c.o",
        "heap_3.c.o",
        ]
    secure_element_files = "_se_manager"
    if secure_element_files in file_name:
        return "Secure Element"

    if "AppTask" in file_name:
        return "Matter Examples Code"
    if "Provision" in file_name:
        return "Silabs Matter Provisioning"
    if "ICD" in file_name:
        return "Matter ICD support" 
    if "command-handler" in file_name:
        return "Matter"
    if "sli_bgapi" in file_name or "bgapi" in file_name or "sli_bt_hci_event_table" in file_name:
        return "Bluetooth"
    if "DeviceInfoProviderImpl" in file_name:
        return "Matter Silabs Abstraction Impl"
    if "attribute-storage.o" in file_name or "CodegenDataModelProvider.o" in file_name or "EmberAttributeDataBuffer.o" in file_name or "privilege-storage.o" in file_name:
        return "Matter Data Model"
    if "attribute-table.o" in file_name or "Accessors.o" in file_name or "AttributePathExpandIterator" in file_name or "ThreadScanResponse." in file_name:
        return "Matter Data Model"
    if "CodegenDataModelProvider_Write.o" in file_name or "CodegenDataModelProvider_Read.o" in file_name or "AttributeListBuilder.o" in file_name:
        return "Matter Data Model"
    if "ember-io-storage.o" in file_name or "AdministratorCommissioningLogic" in file_name:
        return "Matter Data Model"
    if "GlobalAttributes" in file_name or "ActionReturnStatus"  in file_name or "ServiceNaming" in file_name or "StatusResponse" in file_name or "ember-strings" in file_name or "CodeDrivenInitShutdown" in file_name:
        return "Matter"
    if "CheckinMessage" in file_name:
        return "Matter ICD support"
    if "SilabsTestEventTriggerDelegate" in file_name or "SensorManager" in file_name:
        return "Matter Examples Code"
    if file_name.startswith("radio_") or "message_framer" in file_name or file_name.startswith("sl_rail_"):
        return "Platform"
    if file_name.startswith("error.") or "StorageDelegateWrapper" in file_name:
        return "Matter"
    if file_name.startswith("data-model-provider."):
        #with SLC this seems to be put in the Matter category
        return "Matter"
    if "DefaultTimerDelegate" in file_name:
        return "Matter"
    if file_name.startswith("data-model-provider."):
        return "Matter"
    if "DefaultAttributePersistenceProvider" in file_name:
        return "Matter"
    if file_name.startswith("encode-decode."):
        return "Matter"
    if "CheckInCounter" in file_name:
        return "Matter ICD support"
    if "callback-stub" in file_name:
        return "Matter Examples Code"
    if "sl_device_dma_s2" in file_name:
        return "Platform"
    if "sl_openthread" in file_name:
        return "OpenThread"
    if "CHIPMem-Platform" in file_name:
        return "Matter Silabs Abstraction Impl"
    if "CHIPPlatformMemory" in file_name or "EventsGenerator" in file_name or "CHIPMem" in file_name:
        return "Matter"
    if "DataModelCallbacks" in file_name:
        return "Matter Examples Code"
    if "AttributePersistence" in file_name:
        return "Matter"
    if "String.cpp" in file_name or file_name == "String.o":
        return "Matter"
    if "MatterCallbacks.cpp" in file_name:
        return "Matter"
    if "bit_utils" in file_name:
        return "OpenThread"
    if "MatterCallbacks." in file_name:
        return "Matter"
    if "attribute-metadata." in file_name:
        return "Matter"
    if "reporting.o" in file_name or file_name == "util.o":
        return "Matter Data Model"

    

    for mbedtls_file in mbedtls_file_names:
        if mbedtls_file in file_name:
            return "MBedTLS"
        elif mbedtls_file.replace(".c",".o") in file_name:
            return "MBedTLS"
    for freeRTOS_file in freeRTOS_file_names:
        if file_name.replace("sdk.","") == freeRTOS_file:
            return "FreeRTOS"
    if "cluster" in file_name.lower():
        return "Matter Data Model"
    return ""

def get_category_from_library_name(library_name: str,file_name: str) -> str:
    """
    Determine the category based on file name patterns.
    
    Args:
        file_name: The "File Name" value from CSV.
        
    Returns:
        The matched pattern category or empty string if no match.
    """
    if not library_name:
        category_name = get_category_from_filename(file_name) 
        if category_name:
            return category_name
        for pattern, category in FILENAME_CATEGORY_PATTERNS:
            if pattern in file_name:
                return category
    else:
        for pattern, category in FILENAME_CATEGORY_PATTERNS:
            if pattern in library_name:
                return category
            
    # print("Unclassified : ", file_name, "  ", library_name)
    return ""


def get_category(path_in_source: str, default_category: str, library_name: str, file_name: str) -> str:
    """
    Determine the category based on path patterns.
    
    Args:
        path_in_source: The "Path In Source" value from CSV.
        default_category: The default category from "UC Category 1".
        
    Returns:
        The matched pattern category or the default category.
    """
    # Corner case for gcc lib
    if "lib/gcc" in library_name:
        return "C/C++ Standard Library"

    # FIle name mapping is more precise but tedious to maintain
    category_name = get_category_from_filename(file_name) 
    if category_name:
        return category_name

    for pattern, category in CATEGORY_PATTERNS:
        if path_in_source.startswith(pattern):
            return category
    # Overrride Services category to Platform for Matter purposes
    if default_category == "Services":
        return "Platform"
    # CMSIS corner case
    if default_category == "RTOS":
        return "Platform"
    return default_category

def get_cleanup_name(file_name: str) -> str:
    """
    Clean up the file name by removing specific strings.
    
    Args:
        file_name: The original file name.
        
    Returns:
        The cleaned-up file name.
    """
    if file_name.endswith(".cpp.o"):
        file_name = file_name.replace(".cpp.o",".o")
    elif file_name.endswith(".c.o"):
        file_name = file_name.replace(".c.o",".o")
    elif file_name.endswith(".c.obj"):
        file_name = file_name.replace(".c.obj",".o")
    
    #corner case
    if ".out." in file_name:
        file_name = file_name.replace(".out.",".")

    if "AppTask.o" in file_name:
        print(file_name)

    if len(file_name.split(".")) > 2:
        # GN style e.g. manager.ICDManager.o
        return file_name.split(".")[1] + ".o"
    

    # corner cases for Data Model (blame SLC)
    if "operational-credentials-cluster.o" in file_name:
        return "OperationalCredentialsCluster.o"
    if "group-key-mgmt-cluster.o" in file_name:
        return "GroupKeyManagementCluster.o"
    if "general-commissioning-cluster.o" in file_name:
        return "GeneralCommissioningCluster.o"
    if "general-diagnostics-cluster.o" in file_name:
        return "GeneralDiagnosticsCluster.o"
    if "thread-network-diagnostics-server.o" in file_name:
        return "ThreadNetworkDiagnosticsCluster.o"
    if "thread-network-diagnostics-provider.o" in file_name:
        return "ThreadNetworkDiagnosticsProvider.o"
    if "descriptor-cluster.o" in file_name:
        return "DescriptorCluster.o"
    if "localization-configuration-cluster.o" in file_name:
        return "LocalizationConfigurationCluster.o"
    if "time-format-localization-cluster.o" in file_name:
        return "TimeFormatLocalizationCluster.o"

    return file_name


def parse_csv(csv_file: Path) -> Dict[str, List[Tuple[str, int]]]:
    """
    Parse CSV file and extract category data.
    
    Args:
        csv_file: Path to CSV file.
        
    Returns:
        Dictionary mapping category names to lists of (file_name, code_size) tuples.
        
    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the CSV file format is invalid.
    """
    category_data: Dict[str, List[Tuple[str, int]]] = {}
    
    # First, scan the entire CSV file to check if "efr32.a" is present
    use_filename_category = False
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_content = f.read()
        if "efr32.a" in csv_content:
            use_filename_category = True
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            default_category = row.get('UC Category 1', '').strip()
            path_in_source = row.get('Path In Source', '').strip()
            file_name = row.get('File Name', '').strip()
            code_size_str = row.get('Code Size', '0').strip()
            library_name = row.get('Library Name', '').strip()
            
            # Determine category based on path patterns
            category = get_category(path_in_source, default_category, library_name, file_name)
            
            # Corner case: if "efr32.a" was found anywhere in the CSV file,
            # try to determine category from file name
            if use_filename_category:
                filename_category = get_category_from_library_name(library_name, file_name)
                if filename_category:
                    category = filename_category
            # If still no category, assign to "Unclassified"
            if not category:
                # check if we can get category from filename
                filename_category = get_category_from_filename(file_name)
                if filename_category:
                    category = filename_category
                else:
                    category = "Unclassified"
            
            # Parse code size
            try:
                code_size = int(code_size_str)
            except (ValueError, TypeError):
                code_size = 0
            
            # Skip zero-size entries
            if code_size == 0:
                continue
            
            # Add to category data
            if category not in category_data:
                category_data[category] = []
            
            cleanup_name = get_cleanup_name(file_name)
            if cleanup_name:
                file_name = cleanup_name

            category_data[category].append((file_name, code_size))
    
    return category_data


def find_csv_file(folder_path: Path) -> Path:
    """
    Find the first CSV file in the specified folder.
    
    Args:
        folder_path: Path to folder to search.
        
    Returns:
        Path to the first CSV file found.
        
    Raises:
        FileNotFoundError: If no CSV file is found in the folder.
    """
    csv_files = list(folder_path.glob("*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV file found in folder: {folder_path}")
    
    return csv_files[0]
