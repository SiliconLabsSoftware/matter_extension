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

def create_comment_body(result, status, commit_sha, branch_name, target_branch, sonar_output):
    """Create formatted comment body for GitHub PR"""
    
    # Determine status emoji and text
    if result == "PASS":
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
    
    comment_body = f"""## 🔍 SonarQube Static Analysis Results

**Result:** {result_emoji} {result_text}  
**Quality Gate Status:** {status}  
**Commit SHA:** `{commit_sha}`

### 📊 Analysis Summary
- **Branch:** `{branch_name}`
- **Target:** `{target_branch}`
- **Analysis Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

### 📋 Detailed Results
<details>
<summary>Click to view SonarQube output</summary>

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
    parser.add_argument("--result", required=True, choices=["PASS", "FAIL"], help="SonarQube analysis result")
    parser.add_argument("--status", required=True, help="SonarQube quality gate status")

    parser.add_argument("--branch_name", required=True, help="Source branch name")
    parser.add_argument("--target_branch", required=True, help="Target branch name")
    parser.add_argument("--sonar_output", required=True, help="SonarQube scanner output")
    
    args = parser.parse_args()
    
    try:
        # Create comment body
        comment_body = create_comment_body(
            args.result,
            args.status,
            args.commit_sha,
            args.branch_name,
            args.target_branch,
            args.sonar_output
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