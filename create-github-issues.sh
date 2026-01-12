#!/bin/bash

# Script to create GitHub issues from the issues folder
# This script uses GitHub CLI (gh) to create issues from markdown files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISSUES_DIR="$SCRIPT_DIR/issues"
REPO="gkrost/7z"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed.${NC}"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI.${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

echo -e "${GREEN}Creating GitHub issues from markdown files in issues folder...${NC}"
echo ""

# Issue metadata (title, labels, priority)
declare -A issue_metadata

# Issue 01: Unsafe string functions
issue_metadata["issue-01-unsafe-string-functions.md"]="Replace unsafe C string functions with safe alternatives|security,high-priority,bug"

# Issue 02: Dead code
issue_metadata["issue-02-dead-code-if0-blocks.md"]="Remove or document 139 disabled code blocks (#if 0)|technical-debt,maintenance,medium-priority"

# Issue 03: Unsafe atomic hack
issue_metadata["issue-03-unsafe-atomic-hack.md"]="Replace USE_HACK_UNSAFE_ATOMIC with proper atomic operations|security,concurrency,high-priority,bug"

# Issue 04: Deprecated GetVersion API
issue_metadata["issue-04-deprecated-getversion-api.md"]="Update deprecated Windows GetVersion() API usage|deprecated,platform-specific,medium-priority"

# Issue 05: Deprecated ARM crypto macros
issue_metadata["issue-05-deprecated-arm-crypto-macros.md"]="Update deprecated ARM crypto feature detection macros|deprecated,platform-specific,medium-priority"

# Issue 06: Compiler workarounds
issue_metadata["issue-06-compiler-workarounds.md"]="Document and review compiler-specific workarounds|technical-debt,legacy-code,medium-priority"

# Issue 07: Commented debug code
issue_metadata["issue-07-commented-debug-code.md"]="Clean up commented-out debug code and defines|technical-debt,maintenance,low-priority"

# Issue 08: Naked functions
issue_metadata["issue-08-naked-functions.md"]="Review and document naked function usage|legacy-code,platform-specific,low-priority"

# Counter for created issues
created=0
skipped=0
failed=0

# Iterate through issue files
for issue_file in "$ISSUES_DIR"/issue-*.md; do
    if [ ! -f "$issue_file" ]; then
        continue
    fi
    
    filename=$(basename "$issue_file")
    
    # Skip if not in metadata
    if [ -z "${issue_metadata[$filename]}" ]; then
        echo -e "${YELLOW}Skipping $filename (no metadata)${NC}"
        ((skipped++))
        continue
    fi
    
    # Extract title and labels from metadata
    IFS='|' read -r title labels <<< "${issue_metadata[$filename]}"
    
    echo -e "${GREEN}Creating issue from: $filename${NC}"
    echo "  Title: $title"
    echo "  Labels: $labels"
    
    # Read the issue body from file
    body=$(cat "$issue_file")
    
    # Create the issue
    if gh issue create \
        --repo "$REPO" \
        --title "$title" \
        --body "$body" \
        --label "$labels"; then
        echo -e "${GREEN}✓ Created issue: $title${NC}"
        ((created++))
    else
        echo -e "${RED}✗ Failed to create issue: $title${NC}"
        ((failed++))
    fi
    
    echo ""
    
    # Small delay to avoid rate limiting
    sleep 1
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Summary:${NC}"
echo -e "  Created: ${GREEN}$created${NC}"
echo -e "  Skipped: ${YELLOW}$skipped${NC}"
echo -e "  Failed:  ${RED}$failed${NC}"
echo -e "${GREEN}========================================${NC}"

if [ $failed -gt 0 ]; then
    exit 1
fi
