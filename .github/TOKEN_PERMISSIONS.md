# GitHub Actions Token Permissions

This repository has been configured with GitHub Actions workflows that include proper token permissions for artifact management, including deletion capabilities.

## Token Permissions

The following permissions have been configured in the GitHub Actions workflows:

### CI Workflow (`ci.yml`)
- `contents: read` - Allows reading repository contents
- `actions: write` - **Enables artifact deletion and management**
- `packages: read` - Allows reading packages

### Artifact Cleanup Workflow (`cleanup-artifacts.yml`)
- `contents: read` - Allows reading repository contents  
- `actions: write` - **Enables artifact deletion and management**
- `metadata: read` - Allows reading metadata

## Key Permission: `actions: write`

The `actions: write` permission is specifically required for:
- Deleting artifacts via the GitHub API
- Managing workflow artifacts
- Cleanup operations on old build artifacts

## Workflows

### 1. CI Workflow
- Runs on push/PR to main/develop branches
- Builds and tests the Matter extension code
- Creates build artifacts
- Demonstrates artifact management permissions

### 2. Artifact Cleanup Workflow
- Runs daily at 2 AM UTC (configurable)
- Can be triggered manually with custom retention period
- Automatically deletes artifacts older than specified days (default: 7 days)
- Uses GitHub API with proper permissions to delete artifacts

## Usage

The artifact cleanup workflow can be triggered manually:
1. Go to Actions tab in GitHub
2. Select "Artifact Cleanup" workflow
3. Click "Run workflow"
4. Optionally specify custom retention period

## Security

These permissions follow the principle of least privilege:
- Only necessary permissions are granted
- `actions: write` is specifically for artifact management
- No administrative or sensitive permissions are included