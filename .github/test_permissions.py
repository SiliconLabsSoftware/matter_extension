#!/usr/bin/env python3
"""
Test script to validate GitHub Actions workflow permissions setup.
This script checks that the workflows have the correct permissions for artifact deletion.
"""

import yaml
import os
import sys

def test_workflow_permissions():
    """Test that workflows have the required permissions for artifact deletion."""
    workflows_dir = ".github/workflows"
    
    if not os.path.exists(workflows_dir):
        print("ERROR: No workflows directory found")
        return False
    
    required_permission = "actions: write"
    test_passed = True
    
    for workflow_file in os.listdir(workflows_dir):
        if workflow_file.endswith('.yml') or workflow_file.endswith('.yaml'):
            workflow_path = os.path.join(workflows_dir, workflow_file)
            print(f"Checking {workflow_file}...")
            
            with open(workflow_path, 'r') as f:
                try:
                    workflow = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    print(f"  ERROR: Invalid YAML syntax: {e}")
                    test_passed = False
                    continue
            
            # Check if permissions are defined
            if 'permissions' not in workflow:
                print(f"  WARNING: No permissions defined in {workflow_file}")
                continue
            
            permissions = workflow['permissions']
            
            # Check for actions: write permission
            if 'actions' in permissions and permissions['actions'] == 'write':
                print(f"  ✓ Found required 'actions: write' permission")
            else:
                print(f"  ✗ Missing 'actions: write' permission")
                test_passed = False
    
    return test_passed

def test_artifact_cleanup_workflow():
    """Test that the artifact cleanup workflow has the correct API calls."""
    cleanup_workflow_path = ".github/workflows/cleanup-artifacts.yml"
    
    if not os.path.exists(cleanup_workflow_path):
        print("ERROR: cleanup-artifacts.yml not found")
        return False
    
    with open(cleanup_workflow_path, 'r') as f:
        content = f.read()
    
    # Check for required GitHub API calls
    required_calls = [
        "actions.listArtifactsForRepo",
        "actions.deleteArtifact"
    ]
    
    test_passed = True
    for call in required_calls:
        if call in content:
            print(f"  ✓ Found required API call: {call}")
        else:
            print(f"  ✗ Missing required API call: {call}")
            test_passed = False
    
    return test_passed

if __name__ == "__main__":
    print("Testing GitHub Actions workflow permissions setup...")
    print("=" * 50)
    
    print("\n1. Testing workflow permissions...")
    permissions_ok = test_workflow_permissions()
    
    print("\n2. Testing artifact cleanup functionality...")
    cleanup_ok = test_artifact_cleanup_workflow()
    
    print("\n" + "=" * 50)
    if permissions_ok and cleanup_ok:
        print("✓ All tests passed! Workflows are properly configured for artifact deletion.")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Please check the workflow configuration.")
        sys.exit(1)