"""
Artifact processing module.

This module handles all artifact processing operations including:
- Downloading artifacts from GitHub Actions
- Extracting artifact files
- Processing individual binary artifacts
- Managing artifact uploads to UBAI
"""

import os
import requests
import shutil
import sys
import zipfile

# Add the workspace root to Python path to enable importing internal modules
workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

import internal.config as config
from internal.github.github_workflow import _make_github_api_request
from internal.artifacts.ubai_client import upload_to_ubai
from internal.artifacts.artifactory_client import upload_to_artifactory


def download_and_upload_artifacts(workflow_id, branch_name, run_number, sqa=False):
    """
    Download artifacts from GitHub Actions and upload them to UBAI and Artifactory.
    
    Args:
        workflow_id (int): Workflow run ID to download artifacts from.
        branch_name (str): Branch name for artifacts.
        run_number (int): Build number for artifacts.
        sqa (bool): Whether to upload SQA artifacts (default: False).
        
    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If downloading or uploading fails
    """
    _validate_artifact_parameters(workflow_id, branch_name, run_number)
    print(f"Starting artifact download and upload process for workflow {workflow_id}")
    try:
        artifact_info = _download_and_extract_artifacts(workflow_id)
        delete_artifacts(workflow_id)
        print("Uploading individual artifacts to UBAI.")
        _upload_individual_artifacts(artifact_info['extracted_folder'], branch_name, run_number)
        print("Uploading merged artifacts to UBAI and Artifactory.")
        _upload_merged_artifacts(artifact_info['artifact_file'], artifact_info['artifact_name'], 
                               branch_name, run_number)
        print("Artifact download and upload process completed successfully.")
    except Exception as e:
        print(f"Error during artifact processing: {e}")
        raise RuntimeError(f"Failed to process artifacts: {e}")


def upload_binaries_individually_to_ubai(binaries_folder, branch_name, run_number):
    """
    Upload individual binary files from the extracted artifact folder to UBAI.
    
    Args:
        binaries_folder (str): Path to the folder containing binaries.
        branch_name (str): Branch name for the upload.
        run_number (int): Build number for the upload.
        
    Raises:
        ValueError: If parameters are invalid
        RuntimeError: If upload fails
    """
    _validate_binaries_upload_parameters(binaries_folder, branch_name, run_number)
    build_type = _extract_build_type(binaries_folder)
    print(f"Starting individual binary uploads for build type: {build_type}")
    
    try:
        for artifact in os.listdir(binaries_folder):
            artifact_path = os.path.join(binaries_folder, artifact)
            print(f"Processing artifact: {artifact}")
            _process_individual_artifact(artifact, artifact_path, build_type, branch_name, run_number)
        print("Individual binary uploads completed successfully.")
    except Exception as e:
        error_msg = f"Failed to upload individual binaries: {e}"
        print(error_msg)
        raise RuntimeError(error_msg)


def _validate_artifact_parameters(workflow_id, branch_name, run_number):
    """
    Validate input parameters for artifact processing.
    
    Args:
        workflow_id (int): Workflow run ID
        branch_name (str): Branch name
        run_number (int): Build number
        
    Raises:
        ValueError: If any parameter is invalid
    """
    if not workflow_id or workflow_id <= 0:
        raise ValueError("Workflow ID must be a positive integer")
    if not branch_name or not branch_name.strip():
        raise ValueError("Branch name cannot be empty")
    if not run_number or run_number <= 0:
        raise ValueError("Run number must be a positive integer")


def _download_and_extract_artifacts(workflow_id):
    """
    Download artifacts from GitHub Actions and extract them locally.
    
    Args:
        workflow_id (int): Workflow run ID to download artifacts from
        
    Returns:
        dict: Information about the downloaded and extracted artifacts
        
    Raises:
        RuntimeError: If downloading or extraction fails
    """
    artifact_info = _get_artifact_info(workflow_id)
    artifact_file = _download_artifact(artifact_info['download_url'], artifact_info['name'])
    extracted_folder = _extract_artifact(artifact_file)
    return {
        'artifact_file': artifact_file,
        'artifact_name': artifact_info['name'],
        'extracted_folder': extracted_folder
    }

def delete_artifacts(workflow_id):
    """
    Deletes the specified artifacts from the build server.
    """
    # Implement the logic to delete artifacts based on the workflow_id
    artifact_info = _get_artifact_info(workflow_id)
    # Use the artifact URL for deletion (not the download URL)
    artifact_url = artifact_info['url']
    print(f"Making DELETE request to: {artifact_url}")
    
    # Make DELETE request to delete the artifact
    response = requests.delete(url=artifact_url, headers=config.github_headers)
    
    if response.status_code not in [204, 200]:
        error_msg = f"Failed to delete artifact. Status: {response.status_code}, Response: {response.text}"
        print(error_msg)
        raise RuntimeError(error_msg)
    
    print(f"Successfully deleted artifact: {artifact_info['name']}")


def _get_artifact_info(workflow_id):
    """
    Get artifact information from GitHub Actions API.
    
    Args:
        workflow_id (int): Workflow run ID
        
    Returns:
        dict: Artifact information containing download_url, name, id, and url
        
    Raises:
        RuntimeError: If API request fails or no artifacts found
    """
    workflow_artifact_url = f"{config.actions_runs_url}/{workflow_id}/artifacts"
    print(f"Fetching artifacts from URL: {workflow_artifact_url}")
    response = _make_github_api_request(workflow_artifact_url)
    artifacts_data = response.json()
    if not artifacts_data.get('artifacts'):
        raise RuntimeError(f"No artifacts found for workflow {workflow_id}")
    artifact = artifacts_data['artifacts'][0]
    return {
        'download_url': artifact['archive_download_url'],
        'name': artifact['name'] + '.zip',
        'id': artifact['id'],
        'url': artifact['url']
    }


def _download_artifact(download_url, artifact_name):
    """
    Download an artifact from GitHub Actions.
    
    Args:
        download_url (str): URL to download the artifact from
        artifact_name (str): Name of the artifact file
        
    Returns:
        str: Path to the downloaded artifact file
        
    Raises:
        RuntimeError: If download fails
    """
    print(f"Downloading artifact {artifact_name} from URL: {download_url}")
    
    # Clean up existing files/folders before downloading
    artifact_file = os.path.join('.', artifact_name)
    extracted_folder = os.path.join('.', artifact_name.replace('.zip', ''))
    
    # Delete existing artifact file if it exists
    if os.path.exists(artifact_file):
        print(f"Removing existing artifact file: {artifact_file}")
        os.remove(artifact_file)
    
    # Delete existing extracted folder if it exists
    if os.path.exists(extracted_folder):
        print(f"Removing existing extracted folder: {extracted_folder}")
        shutil.rmtree(extracted_folder)
    
    response = _make_github_api_request(download_url)
    with open(artifact_file, 'wb') as f:
        f.write(response.content)
    print(f"Successfully downloaded {artifact_name}")
    return artifact_file


def _extract_artifact(artifact_file):
    """
    Extract a downloaded artifact ZIP file.
    
    Args:
        artifact_file (str): Path to the artifact ZIP file
        
    Returns:
        str: Path to the extracted folder
        
    Raises:
        RuntimeError: If extraction fails
    """
    artifact_name = os.path.basename(artifact_file)
    extracted_folder = os.path.join('.', artifact_name.replace('.zip', ''))
    print(f"Extracting {artifact_name} to {extracted_folder}")
    try:
        os.makedirs(extracted_folder, exist_ok=True)
        with zipfile.ZipFile(artifact_file, 'r') as zip_ref:
            zip_ref.extractall(extracted_folder)
        print(f"Successfully extracted {artifact_name}")
        return extracted_folder
    except Exception as e:
        raise RuntimeError(f"Failed to extract {artifact_name}: {e}")


def _upload_individual_artifacts(extracted_folder, branch_name, run_number):
    """
    Upload individual binary artifacts to UBAI.
    
    Args:
        extracted_folder (str): Path to the extracted artifacts folder
        branch_name (str): Branch name for the upload
        run_number (int): Build number for the upload
        
    Raises:
        RuntimeError: If upload fails
    """
    try:
        upload_binaries_individually_to_ubai(extracted_folder, branch_name, run_number)
    except Exception as e:
        raise RuntimeError(f"Failed to upload individual artifacts: {e}")


def _upload_merged_artifacts(artifact_file, artifact_name, branch_name, run_number):
    """
    Upload the merged artifact to both UBAI and Artifactory.
    
    Args:
        artifact_file (str): Path to the artifact file
        artifact_name (str): Name of the artifact
        branch_name (str): Branch name for the upload
        run_number (int): Build number for the upload
        
    Raises:
        RuntimeError: If upload fails
    """
    try:
        upload_to_ubai(
            file_path=artifact_file,
            app_name="matter",
            stack="matter",
            target="matter",
            branch_name=branch_name,
            run_number=run_number
        )
        upload_to_artifactory(artifact_file, artifact_name, branch_name, str(run_number))
    except Exception as e:
        raise RuntimeError(f"Failed to upload merged artifacts: {e}")


def _validate_binaries_upload_parameters(binaries_folder, branch_name, run_number):
    """
    Validate input parameters for binary uploads.
    
    Args:
        binaries_folder (str): Path to the binaries folder
        branch_name (str): Branch name
        run_number (int): Build number
        
    Raises:
        ValueError: If any parameter is invalid
    """
    if not binaries_folder or not os.path.exists(binaries_folder):
        raise ValueError(f"Binaries folder does not exist: {binaries_folder}")
    
    if not os.path.isdir(binaries_folder):
        raise ValueError(f"Binaries folder must be a directory: {binaries_folder}")
    
    if not branch_name or not branch_name.strip():
        raise ValueError("Branch name cannot be empty")
    
    if not run_number or run_number <= 0:
        raise ValueError("Run number must be a positive integer")


def _extract_build_type(binaries_folder):
    """
    Extract build type from the binaries folder name.
    
    Args:
        binaries_folder (str): Path to the binaries folder
        
    Returns:
        str: The build type (e.g., 'standard', 'release')
        
    Raises:
        ValueError: If build type cannot be extracted
    """
    try:
        return binaries_folder.split('artifacts-')[1]
    except (IndexError, AttributeError):
        raise ValueError(f"Could not extract build type from folder name: {binaries_folder}")


def _process_individual_artifact(artifact_name, artifact_path, build_type, branch_name, run_number):
    """
    Process an individual artifact based on its type.
    
    Args:
        artifact_name (str): Name of the artifact
        artifact_path (str): Path to the artifact
        build_type (str): Build type (e.g., 'standard', 'release')
        branch_name (str): Branch name for upload
        run_number (int): Build number for upload
    """
    if artifact_name == "chip-tool":
        _upload_chip_tool(artifact_path, branch_name, run_number)
    elif artifact_name == "chip-ota-provider-app":
        _upload_chip_ota_provider(artifact_path, branch_name, run_number)
    elif artifact_name == "provision.zip":
        _upload_provision_zip(artifact_path, branch_name, run_number)
    elif artifact_name == "ota-scripts.zip":
        _upload_ota_scripts(artifact_path, branch_name, run_number)
    elif os.path.isdir(artifact_path):
        if artifact_name == "WiFi-Firmware":
            _upload_wifi_firmware(artifact_path, branch_name, run_number)
        else:
            _upload_board_artifacts(artifact_name, artifact_path, build_type, branch_name, run_number)


def _upload_chip_tool(artifact_path, branch_name, run_number):
    """Upload chip-tool artifact to UBAI."""
    print("Uploading chip-tool to UBAI.")
    upload_to_ubai(artifact_path, "Chiptool", "linux-arm64-ipv6only-clang", branch_name, run_number)


def _upload_chip_ota_provider(artifact_path, branch_name, run_number):
    """Upload chip-ota-provider-app artifact to UBAI."""
    print("Uploading chip-ota-provider-app to UBAI.")
    upload_to_ubai(artifact_path, "OTA", "linux-arm64-ipv6only-clang", branch_name, run_number)


def _upload_provision_zip(artifact_path, branch_name, run_number):
    """Upload provision.zip artifact to UBAI."""
    print("Uploading provision to UBAI.")
    upload_to_ubai(artifact_path, "matter_provision", "matter", branch_name, run_number)


def _upload_ota_scripts(artifact_path, branch_name, run_number):
    """Upload ota-scripts.zip artifact to UBAI."""
    print("Uploading ota-scripts to UBAI.")
    upload_to_ubai(artifact_path, "matter", "matter", branch_name, run_number)


def _upload_wifi_firmware(wifi_firmware_path, branch_name, run_number):
    """
    Upload WiFi firmware artifacts to UBAI.
    
    Args:
        wifi_firmware_path (str): Path to the WiFi-Firmware directory
        branch_name (str): Branch name for upload
        run_number (int): Build number for upload
    """
    print("Processing WiFi-Firmware artifacts.")
    for board_folder in os.listdir(wifi_firmware_path):
        board_path = os.path.join(wifi_firmware_path, board_folder)
        if os.path.isdir(board_path):
            _upload_wifi_firmware_files(board_path, board_folder, branch_name, run_number)


def _upload_wifi_firmware_files(board_path, board_folder, branch_name, run_number):
    """
    Upload WiFi firmware files for a specific board.
    
    Args:
        board_path (str): Path to the board directory
        board_folder (str): Board folder name
        branch_name (str): Branch name for upload
        run_number (int): Build number for upload
    """
    ubai_app_name = f"WiFi-Firmware-{board_folder}"
    for dirpath, _, filenames in os.walk(board_path):
        for fw_file in filenames:
            if fw_file.endswith('.rps'):
                fw_file_path = os.path.join(dirpath, fw_file)
                print(f"Uploading WiFi firmware: {fw_file_path}")
                upload_to_ubai(fw_file_path, ubai_app_name, board_folder, branch_name, run_number)


def _upload_board_artifacts(board_id, board_path, build_type, branch_name, run_number):
    """
    Upload board-specific artifacts to UBAI.
    
    Args:
        board_id (str): Board identifier
        board_path (str): Path to the board directory
        build_type (str): Build type
        branch_name (str): Branch name for upload
        run_number (int): Build number for upload
    """
    board_id_upper = board_id.upper()
    print(f"Processing board ID: {board_id_upper}")
    for app_name_folder in os.listdir(board_path):
        app_name_path = os.path.join(board_path, app_name_folder)
        print(f"Sample App Path: {app_name_path}")
        if os.path.isdir(app_name_path):
            _process_board_app(app_name_folder, app_name_path, board_id_upper, build_type, branch_name, run_number)


def _process_board_app(app_name_folder, app_name_path, board_id, build_type, branch_name, run_number):
    """
    Process a board application and upload its artifacts.
    
    Args:
        app_name_folder (str): Application folder name
        app_name_path (str): Path to the application directory
        board_id (str): Board identifier
        build_type (str): Build type
        branch_name (str): Branch name for upload
        run_number (int): Build number for upload
    """
    app_info = _determine_app_info(app_name_folder, board_id, build_type)
    print(f"Sample App Name: {app_info['app_name']}")
    artifact_folder = os.path.join(app_name_path, 'artifact')
    if os.path.exists(artifact_folder) and os.path.isdir(artifact_folder):
        _upload_board_artifact_files(artifact_folder, app_info, board_id, branch_name, run_number)


def _determine_app_info(app_name_folder, board_id, build_type):
    """
    Determine application information based on folder name.
    
    Args:
        app_name_folder (str): Application folder name
        board_id (str): Board identifier
        build_type (str): Build type
        
    Returns:
        dict: Application information containing app_name and cmp_type
    """
    if "bootloader" in app_name_folder:
        return {
            'app_name': f"{board_id}-bootloader",
            'cmp_type': ""
        }
    elif "thread" in app_name_folder:
        return {
            'app_name': f"{board_id}-OpenThread-{build_type}",
            'cmp_type': ""
        }
    elif "zigbee-matter-light" in app_name_folder:
        cmp_type = "-thread-sequential" if "sequential" in app_name_folder else "-thread-concurrent"
        return {
            'app_name': f"{board_id}-OpenThread-{build_type}",
            'cmp_type': cmp_type
        }
    else:
        return {
            'app_name': f"{board_id}-WiFi-{build_type}",
            'cmp_type': ""
        }


def _upload_board_artifact_files(artifact_folder, app_info, board_id, branch_name, run_number):
    """
    Upload board artifact files to UBAI.
    
    Args:
        artifact_folder (str): Path to the artifact folder
        app_info (dict): Application information
        board_id (str): Board identifier
        branch_name (str): Branch name for upload
        run_number (int): Build number for upload
    """
    for file_name in os.listdir(artifact_folder):
        file_path = os.path.join(artifact_folder, file_name)
        if os.path.isfile(file_path) and file_name.endswith(('.s37', '.rps')):
            new_file_name = _generate_new_file_name(file_name, app_info, board_id)
            new_file_path = os.path.join(artifact_folder, new_file_name)
            os.rename(file_path, new_file_path)
            print(f"Renamed file {file_name} to {new_file_name}.")
            upload_to_ubai(new_file_path, app_info['app_name'], board_id, branch_name, run_number)


def _generate_new_file_name(file_name, app_info, board_id):
    """
    Generate a new file name based on the application type and board ID.
    
    Args:
        file_name (str): Original file name
        app_info (dict): Application information
        board_id (str): Board identifier
        
    Returns:
        str: New file name
    """
    file_ext = file_name.split(".")[-1]
    if "bootloader" in app_info['app_name']:
        return f"{board_id.lower()}-bootloader.{file_ext}"
    else:
        sample_app = _extract_sample_app_name(file_name)
        cmp_type = app_info['cmp_type']
        if "." not in sample_app:
            return f"{sample_app}{cmp_type}.{file_ext}"
        else:
            sample_app_base = sample_app.rsplit(".", 1)[0]
            return f"{sample_app_base}{cmp_type}.{file_ext}"


def _extract_sample_app_name(file_name):
    """
    Extract the sample app name from the file name.
    
    Args:
        file_name (str): Original file name
        
    Returns:
        str: Extracted sample app name
    """
    if "internal-bootloader" in file_name:
        return file_name.split("-internal-bootloader")[0]
    elif "bootloader" in file_name:
        return file_name.split("-bootloader")[0]
    else:
        return file_name 