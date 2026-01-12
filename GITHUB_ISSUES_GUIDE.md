# GitHub Issue Creation Guide

This directory contains scripts and documentation for creating GitHub issues from the markdown files in the `issues/` folder.

## Overview

The `issues/` folder contains 8 detailed issue reports for code quality problems found in the 7-Zip codebase. This guide explains how to create GitHub issues from these files.

## Quick Start

### Option 1: Using the Bash Script (Recommended for Unix/Linux/macOS)

```bash
./create-github-issues.sh
```

### Option 2: Using the Python Script (Cross-platform)

```bash
python3 create_github_issues.py
```

### Option 3: Manual Creation

Follow the steps in the "Manual Issue Creation" section below.

## Prerequisites

### For Automated Scripts:

1. **GitHub CLI (gh)** - Required for automated issue creation
   - Install from: https://cli.github.com/
   - Authenticate: `gh auth login`

2. **Bash** (for bash script) or **Python 3.6+** (for Python script)

### For Manual Creation:

- Access to the GitHub repository
- Permissions to create issues

## Issues to Create

The following 8 issues should be created from the markdown files:

| Priority | File | Title | Labels |
|----------|------|-------|--------|
| High | `issue-01-unsafe-string-functions.md` | Replace unsafe C string functions with safe alternatives | `security`, `high-priority`, `bug` |
| High | `issue-03-unsafe-atomic-hack.md` | Replace USE_HACK_UNSAFE_ATOMIC with proper atomic operations | `security`, `concurrency`, `high-priority`, `bug` |
| Medium | `issue-02-dead-code-if0-blocks.md` | Remove or document 139 disabled code blocks (#if 0) | `technical-debt`, `maintenance`, `medium-priority` |
| Medium | `issue-04-deprecated-getversion-api.md` | Update deprecated Windows GetVersion() API usage | `deprecated`, `platform-specific`, `medium-priority` |
| Medium | `issue-05-deprecated-arm-crypto-macros.md` | Update deprecated ARM crypto feature detection macros | `deprecated`, `platform-specific`, `medium-priority` |
| Medium | `issue-06-compiler-workarounds.md` | Document and review compiler-specific workarounds | `technical-debt`, `legacy-code`, `medium-priority` |
| Low | `issue-07-commented-debug-code.md` | Clean up commented-out debug code and defines | `technical-debt`, `maintenance`, `low-priority` |
| Low | `issue-08-naked-functions.md` | Review and document naked function usage | `legacy-code`, `platform-specific`, `low-priority` |

## Automated Issue Creation

### Using Bash Script

```bash
# Make sure the script is executable
chmod +x create-github-issues.sh

# Run the script
./create-github-issues.sh
```

The script will:
1. Check if GitHub CLI is installed and authenticated
2. Read each issue markdown file
3. Create a GitHub issue with appropriate title and labels
4. Display a summary of created issues

### Using Python Script

```bash
# Make sure the script is executable
chmod +x create_github_issues.py

# Run the script
python3 create_github_issues.py
```

If GitHub CLI is not available, the script will generate JSON files in the `generated_issues/` directory that can be used to create issues later.

## Manual Issue Creation

If you prefer to create issues manually or the automated scripts don't work:

1. Navigate to the GitHub repository issues page:
   https://github.com/gkrost/7z/issues

2. Click "New issue"

3. For each file in the `issues/` folder:
   - Copy the title from the table above
   - Copy the entire content of the markdown file as the issue body
   - Add the labels listed in the table above
   - Click "Submit new issue"

## Verifying Issue Creation

After running the scripts, verify that issues were created:

```bash
# List all open issues
gh issue list --repo gkrost/7z

# Or visit the GitHub issues page
# https://github.com/gkrost/7z/issues
```

## Troubleshooting

### GitHub CLI Not Authenticated

```bash
gh auth login
```

Follow the prompts to authenticate with GitHub.

### Permission Denied

Make sure you have permission to create issues in the repository. If not, contact the repository owner.

### Script Fails

If the automated scripts fail, use the manual creation method or check the error messages for specific issues.

### Rate Limiting

If you encounter rate limiting issues, the scripts include small delays between issue creation. If needed, you can increase these delays in the script.

## Additional Information

### Issue Labels

You may need to create the following labels in the repository if they don't exist:

- `security` (red, high importance)
- `high-priority` (red)
- `medium-priority` (yellow)
- `low-priority` (green)
- `bug` (red)
- `technical-debt` (gray)
- `maintenance` (blue)
- `deprecated` (orange)
- `platform-specific` (purple)
- `concurrency` (red)
- `legacy-code` (gray)

To create labels via GitHub CLI:

```bash
gh label create security --color "d73a4a" --description "Security vulnerability"
gh label create high-priority --color "d73a4a" --description "High priority"
gh label create medium-priority --color "fbca04" --description "Medium priority"
gh label create low-priority --color "0e8a16" --description "Low priority"
# ... and so on
```

### Milestones

Consider creating milestones for organizing these issues:

- **Security Fixes** (for issues 01 and 03)
- **Deprecation Updates** (for issues 04 and 05)
- **Technical Debt Cleanup** (for issues 02, 06, 07, 08)

## Related Documentation

- `issues/README.md` - Detailed overview of all code quality issues
- `CODE_QUALITY_ISSUES.md` - Comprehensive analysis report
- Individual issue files in `issues/` folder

## Support

If you encounter any problems with issue creation, please:

1. Check that you have the latest version of GitHub CLI
2. Verify you're authenticated: `gh auth status`
3. Check repository permissions
4. Try manual issue creation as a fallback
