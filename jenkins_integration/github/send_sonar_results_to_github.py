#!/usr/bin/env python3
"""
Script to post SonarQube static analysis results to GitHub PR as a comment.
"""

import argparse
import json
import os
import requests
import sys
from datetime import datetime
import urllib.parse

def post_pr_comment(github_token, repo_owner, repo_name, pr_number, comment_body):
    """Post a comment to GitHub PR"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    payload = {"body": comment_body}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print(f"✅ Successfully posted SonarQube results to PR #{pr_number}")
        return True
    else:
        print(f"❌ Failed to post comment to PR #{pr_number}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def post_commit_status(github_token, repo_owner, repo_name, commit_sha, state, description, target_url):
    """Post commit status to GitHub"""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/statuses/{commit_sha}"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "state": state,
        "target_url": target_url,
        "description": description,
        "context": "ci/sonarqube-analysis"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print(f"✅ Successfully posted commit status for {commit_sha[:8]}")
        return True
    else:
        print(f"❌ Failed to post commit status for {commit_sha[:8]}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def fetch_sonarqube_quality_gate(sonar_token, sonar_url, project_key, branch_name=None, pr_key=None):
    """Fetch detailed quality gate information from SonarQube API"""
    try:
        headers = {"Authorization": f"Bearer {sonar_token}"}
        
        # Build the API URL for quality gate status
        if pr_key:
            # For pull requests
            api_url = f"{sonar_url}/api/qualitygates/project_status?projectKey={project_key}&pullRequest={pr_key}"
        elif branch_name:
            # For branches
            encoded_branch = urllib.parse.quote(branch_name, safe='')
            api_url = f"{sonar_url}/api/qualitygates/project_status?projectKey={project_key}&branch={encoded_branch}"
        else:
            # Main branch
            api_url = f"{sonar_url}/api/qualitygates/project_status?projectKey={project_key}"
        
        print(f"🔍 Fetching quality gate from: {api_url}")
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('projectStatus', {})
        else:
            print(f"⚠️  Failed to fetch quality gate details: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"⚠️  Error fetching quality gate details: {str(e)}")
        return None

def fetch_sonarqube_measures(sonar_token, sonar_url, project_key, branch_name=None, pr_key=None):
    """Fetch detailed measures from SonarQube API"""
    try:
        headers = {"Authorization": f"Bearer {sonar_token}"}
        
        # Metrics we want to fetch
        metrics = [
            "new_bugs", "new_vulnerabilities", "new_violations", "new_security_hotspots", 
            "new_code_smells", "new_coverage", "new_duplicated_lines_density",
            "bugs", "vulnerabilities", "violations", "security_hotspots", "code_smells",
            "coverage", "duplicated_lines_density", "ncloc"
        ]
        
        metric_keys = ",".join(metrics)
        
        if pr_key:
            api_url = f"{sonar_url}/api/measures/component?component={project_key}&pullRequest={pr_key}&metricKeys={metric_keys}"
        elif branch_name:
            encoded_branch = urllib.parse.quote(branch_name, safe='')
            api_url = f"{sonar_url}/api/measures/component?component={project_key}&branch={encoded_branch}&metricKeys={metric_keys}"
        else:
            api_url = f"{sonar_url}/api/measures/component?component={project_key}&metricKeys={metric_keys}"
        
        print(f"🔍 Fetching measures from: {api_url}")
        response = requests.get(api_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            measures = {}
            for measure in data.get('component', {}).get('measures', []):
                measures[measure['metric']] = measure.get('value', '0')
            return measures
        else:
            print(f"⚠️  Failed to fetch measures: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"⚠️  Error fetching measures: {str(e)}")
        return {}

def create_comment_body(status, commit_sha, branch_name, target_branch, sonar_output, quality_gate_details=None, measures=None):
    """Create formatted comment body for GitHub PR"""
    
    # Determine status emoji and text
    if status == "PASSED":
        result_emoji = "✅"
        result_text = "**PASSED**"
    else:
        result_emoji = "❌"
        result_text = "**FAILED**"
    
    # Truncate output if too long - show last 2000 characters for most relevant info
    max_output_length = 2000
    if len(sonar_output) > max_output_length:
        truncated_output = "[Output truncated - showing last 2000 characters]\n\n..." + sonar_output[-max_output_length:]
    else:
        truncated_output = sonar_output
    
    # Build quality gate details section
    quality_gate_section = ""
    if quality_gate_details:
        conditions = quality_gate_details.get('conditions', [])
        if conditions:
            quality_gate_section = "\n### 🎯 Quality Gate Conditions\n"
            for condition in conditions:
                metric_name = condition.get('metricKey', 'Unknown')
                status_icon = "✅" if condition.get('status') == 'OK' else "❌"
                actual_value = condition.get('actualValue', 'N/A')
                error_threshold = condition.get('errorThreshold', 'N/A')
                quality_gate_section += f"- {status_icon} **{metric_name}**: {actual_value} (threshold: {error_threshold})\n"
    
    # Build measures section
    measures_section = ""
    if measures:
        measures_section = "\n### 📊 Code Quality Metrics\n"
        
        # New code metrics (for PRs)
        new_metrics = []
        if measures.get('new_bugs') and measures.get('new_bugs') != '0':
            new_metrics.append(f"🐛 **New Bugs**: {measures['new_bugs']}")
        if measures.get('new_vulnerabilities') and measures.get('new_vulnerabilities') != '0':
            new_metrics.append(f"🔒 **New Vulnerabilities**: {measures['new_vulnerabilities']}")
        if measures.get('new_violations') and measures.get('new_violations') != '0':
            new_metrics.append(f"⚠️ **New Violations**: {measures['new_violations']}")
        if measures.get('new_security_hotspots') and measures.get('new_security_hotspots') != '0':
            new_metrics.append(f"🔥 **New Security Hotspots**: {measures['new_security_hotspots']}")
        if measures.get('new_code_smells') and measures.get('new_code_smells') != '0':
            new_metrics.append(f"💨 **New Code Smells**: {measures['new_code_smells']}")
        if measures.get('new_duplicated_lines_density'):
            new_metrics.append(f"📄 **New Duplicated Lines**: {measures['new_duplicated_lines_density']}%")
        
        if new_metrics:
            measures_section += "**New Code:**\n"
            for metric in new_metrics:
                measures_section += f"- {metric}\n"
            measures_section += "\n"
        
        # Overall metrics
        overall_metrics = []
        if measures.get('bugs'):
            overall_metrics.append(f"🐛 **Total Bugs**: {measures['bugs']}")
        if measures.get('vulnerabilities'):
            overall_metrics.append(f"🔒 **Total Vulnerabilities**: {measures['vulnerabilities']}")
        if measures.get('violations'):
            overall_metrics.append(f"⚠️ **Total Violations**: {measures['violations']}")
        if measures.get('code_smells'):
            overall_metrics.append(f"💨 **Total Code Smells**: {measures['code_smells']}")
        if measures.get('ncloc'):
            overall_metrics.append(f"📝 **Lines of Code**: {measures['ncloc']}")
        
        if overall_metrics:
            measures_section += "**Overall:**\n"
            for metric in overall_metrics:
                measures_section += f"- {metric}\n"

    comment_body = f"""## 🔍 SonarQube Static Analysis Results

**Result:** {result_emoji} {result_text}  
**Commit SHA:** `{commit_sha}`

### 📊 Analysis Summary
- **Branch:** `{branch_name}`
- **Target:** `{target_branch}`
- **Analysis Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}{quality_gate_section}{measures_section}
### 📋 Scanner Output
<details>
<summary>Click to view SonarQube scanner output</summary>

```
{truncated_output}
```

</details>

---
*🤖 Automated comment by Jenkins CI*"""

    return comment_body

def main():
    parser = argparse.ArgumentParser(description="Post SonarQube results to GitHub PR")
    parser.add_argument("--github_token", required=True, help="GitHub access token")
    parser.add_argument("--repo_owner", default="SiliconLabsSoftware", help="GitHub repository owner")
    parser.add_argument("--repo_name", default="matter_extension", help="GitHub repository name")
    parser.add_argument("--pr_number", required=True, help="Pull request number")
    parser.add_argument("--commit_sha", required=True, help="Git commit SHA")
    parser.add_argument("--status", required=True, choices=["PASSED", "FAILED"], help="SonarQube analysis result")

    parser.add_argument("--branch_name", required=True, help="Source branch name")
    parser.add_argument("--target_branch", required=True, help="Target branch name")
    parser.add_argument("--sonar_output", required=True, help="SonarQube scanner output")
    parser.add_argument("--sonar_token", help="SonarQube token for API access")
    parser.add_argument("--sonar_url", default="https://sonarqube.silabs.net", help="SonarQube server URL")
    parser.add_argument("--project_key", default="matter_extension", help="SonarQube project key")
    
    args = parser.parse_args()
    
    try:
        # Fetch detailed SonarQube information if token is provided
        quality_gate_details = None
        measures = None
        
        if args.sonar_token:
            print("🔍 Fetching detailed SonarQube quality gate information...")
            quality_gate_details = fetch_sonarqube_quality_gate(
                args.sonar_token, 
                args.sonar_url, 
                args.project_key, 
                args.branch_name, 
                args.pr_number
            )
            
            print("📊 Fetching SonarQube measures...")
            measures = fetch_sonarqube_measures(
                args.sonar_token, 
                args.sonar_url, 
                args.project_key, 
                args.branch_name, 
                args.pr_number
            )
        
        # Create comment body
        comment_body = create_comment_body(
            args.status,
            args.commit_sha,
            args.branch_name,
            args.target_branch,
            args.sonar_output,
            quality_gate_details,
            measures
        )
        
        # Post PR comment
        comment_success = post_pr_comment(
            args.github_token,
            args.repo_owner,
            args.repo_name,
            args.pr_number,
            comment_body
        )
        
        # Post PR comment only (skip commit status due to permissions)
        if comment_success:
            print("✅ GitHub PR comment posted successfully")
            sys.exit(0)
        else:
            print("❌ Failed to post GitHub PR comment")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error posting to GitHub: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()