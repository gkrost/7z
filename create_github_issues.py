#!/usr/bin/env python3
"""
Script to create GitHub issues from markdown files in the issues folder.
Can be used with GitHub CLI or GitHub API.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Issue metadata: filename -> (title, labels)
ISSUE_METADATA = {
    "issue-01-unsafe-string-functions.md": (
        "Replace unsafe C string functions with safe alternatives",
        ["security", "high-priority", "bug"]
    ),
    "issue-02-dead-code-if0-blocks.md": (
        "Remove or document 139 disabled code blocks (#if 0)",
        ["technical-debt", "maintenance", "medium-priority"]
    ),
    "issue-03-unsafe-atomic-hack.md": (
        "Replace USE_HACK_UNSAFE_ATOMIC with proper atomic operations",
        ["security", "concurrency", "high-priority", "bug"]
    ),
    "issue-04-deprecated-getversion-api.md": (
        "Update deprecated Windows GetVersion() API usage",
        ["deprecated", "platform-specific", "medium-priority"]
    ),
    "issue-05-deprecated-arm-crypto-macros.md": (
        "Update deprecated ARM crypto feature detection macros",
        ["deprecated", "platform-specific", "medium-priority"]
    ),
    "issue-06-compiler-workarounds.md": (
        "Document and review compiler-specific workarounds",
        ["technical-debt", "legacy-code", "medium-priority"]
    ),
    "issue-07-commented-debug-code.md": (
        "Clean up commented-out debug code and defines",
        ["technical-debt", "maintenance", "low-priority"]
    ),
    "issue-08-naked-functions.md": (
        "Review and document naked function usage",
        ["legacy-code", "platform-specific", "low-priority"]
    ),
}

# Repository information
REPO_OWNER = "gkrost"
REPO_NAME = "7z"
REPO_FULL = f"{REPO_OWNER}/{REPO_NAME}"


def check_gh_cli() -> bool:
    """Check if GitHub CLI is installed and authenticated."""
    try:
        subprocess.run(
            ["gh", "auth", "status"],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def create_issue_with_gh(title: str, body: str, labels: List[str]) -> bool:
    """Create a GitHub issue using GitHub CLI."""
    try:
        cmd = [
            "gh", "issue", "create",
            "--repo", REPO_FULL,
            "--title", title,
            "--body", body,
        ]
        
        # Add labels
        for label in labels:
            cmd.extend(["--label", label])
        
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        
        print(f"✓ Created issue: {title}")
        print(f"  URL: {result.stdout.strip()}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create issue: {title}")
        print(f"  Error: {e.stderr}")
        return False


def generate_issue_json(title: str, body: str, labels: List[str]) -> Dict:
    """Generate JSON for creating issue via API."""
    return {
        "title": title,
        "body": body,
        "labels": labels
    }


def main():
    """Main function to create GitHub issues."""
    script_dir = Path(__file__).parent
    issues_dir = script_dir / "issues"
    
    if not issues_dir.exists():
        print(f"Error: Issues directory not found: {issues_dir}")
        sys.exit(1)
    
    print("=" * 60)
    print("GitHub Issue Creator for 7-Zip Code Quality Issues")
    print("=" * 60)
    print()
    
    # Check for GitHub CLI
    use_gh_cli = check_gh_cli()
    
    if not use_gh_cli:
        print("⚠ GitHub CLI (gh) not found or not authenticated.")
        print("  This script will generate JSON files instead.")
        print("  Install gh from: https://cli.github.com/")
        print()
        
        # Create output directory for JSON files
        output_dir = script_dir / "generated_issues"
        output_dir.mkdir(exist_ok=True)
        print(f"  JSON files will be saved to: {output_dir}")
        print()
    
    created = 0
    skipped = 0
    failed = 0
    
    # Process each issue file
    for filename, (title, labels) in ISSUE_METADATA.items():
        issue_file = issues_dir / filename
        
        if not issue_file.exists():
            print(f"⚠ Skipping {filename} (file not found)")
            skipped += 1
            continue
        
        print(f"Processing: {filename}")
        print(f"  Title: {title}")
        print(f"  Labels: {', '.join(labels)}")
        
        # Read issue body
        body = issue_file.read_text(encoding='utf-8')
        
        if use_gh_cli:
            # Create issue using GitHub CLI
            if create_issue_with_gh(title, body, labels):
                created += 1
            else:
                failed += 1
        else:
            # Generate JSON file
            issue_json = generate_issue_json(title, body, labels)
            json_filename = filename.replace('.md', '.json')
            json_path = output_dir / json_filename
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(issue_json, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Generated JSON: {json_path}")
            created += 1
        
        print()
    
    # Print summary
    print("=" * 60)
    print("Summary:")
    print(f"  Created: {created}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed:  {failed}")
    print("=" * 60)
    
    if not use_gh_cli:
        print()
        print("To create issues from JSON files, use:")
        print(f"  for file in generated_issues/*.json; do")
        print(f"    gh issue create --repo {REPO_FULL} \\")
        print(f"      --title \"$(jq -r .title $file)\" \\")
        print(f"      --body \"$(jq -r .body $file)\" \\")
        print(f"      --label \"$(jq -r '.labels | join(\",\")' $file)\"")
        print(f"  done")
    
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
