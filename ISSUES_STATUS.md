# GitHub Issues Status Tracker

This document tracks the status of GitHub issues that should be created from the markdown files in the `issues/` folder.

## Issue Creation Status

Last updated: 2026-01-12

| # | Priority | Title | File | Status | GitHub Issue # | Labels |
|---|----------|-------|------|--------|----------------|--------|
| 1 | High | Replace unsafe C string functions with safe alternatives | `issue-01-unsafe-string-functions.md` | ⏳ Pending | - | `security`, `high-priority`, `bug` |
| 2 | High | Replace USE_HACK_UNSAFE_ATOMIC with proper atomic operations | `issue-03-unsafe-atomic-hack.md` | ⏳ Pending | - | `security`, `concurrency`, `high-priority`, `bug` |
| 3 | Medium | Remove or document 139 disabled code blocks (#if 0) | `issue-02-dead-code-if0-blocks.md` | ⏳ Pending | - | `technical-debt`, `maintenance`, `medium-priority` |
| 4 | Medium | Update deprecated Windows GetVersion() API usage | `issue-04-deprecated-getversion-api.md` | ⏳ Pending | - | `deprecated`, `platform-specific`, `medium-priority` |
| 5 | Medium | Update deprecated ARM crypto feature detection macros | `issue-05-deprecated-arm-crypto-macros.md` | ⏳ Pending | - | `deprecated`, `platform-specific`, `medium-priority` |
| 6 | Medium | Document and review compiler-specific workarounds | `issue-06-compiler-workarounds.md` | ⏳ Pending | - | `technical-debt`, `legacy-code`, `medium-priority` |
| 7 | Low | Clean up commented-out debug code and defines | `issue-07-commented-debug-code.md` | ⏳ Pending | - | `technical-debt`, `maintenance`, `low-priority` |
| 8 | Low | Review and document naked function usage | `issue-08-naked-functions.md` | ⏳ Pending | - | `legacy-code`, `platform-specific`, `low-priority` |

## Status Legend

- ⏳ **Pending** - Issue ready to be created
- ✅ **Created** - Issue has been created on GitHub
- 🚧 **In Progress** - Someone is working on this issue
- ✔️ **Resolved** - Issue has been closed/fixed
- ❌ **Cancelled** - Issue will not be created/addressed

## How to Update This Document

After creating issues using the automated scripts or manually:

1. Update the "Status" column from ⏳ Pending to ✅ Created
2. Fill in the "GitHub Issue #" column with the issue number
3. Update the "Last updated" date at the top

## Instructions for Creating Issues

### Automated Creation

Use one of the provided scripts:

```bash
# Using bash script
./create-github-issues.sh

# Using Python script  
python3 create_github_issues.py
```

See `GITHUB_ISSUES_GUIDE.md` for detailed instructions.

### Manual Creation

For each issue:
1. Go to https://github.com/gkrost/7z/issues/new
2. Use the title from the table above
3. Copy the content from the corresponding markdown file as the issue body
4. Add the labels listed in the table
5. Submit the issue
6. Update this tracker with the issue number

## Priority-Based Creation Order

### Phase 1: High Priority (Security) - Create Immediately
- Issue #1: Unsafe string functions
- Issue #2: Unsafe atomic operations

### Phase 2: Medium Priority - Create for Next Release
- Issue #3: Dead code blocks
- Issue #4: Deprecated GetVersion API
- Issue #5: Deprecated ARM crypto macros
- Issue #6: Compiler workarounds

### Phase 3: Low Priority - Create for Future Work
- Issue #7: Commented debug code
- Issue #8: Naked functions

## Notes

- All issue files are located in the `issues/` folder
- Each file is a standalone issue report that can be copied directly to GitHub
- Issues are sorted by priority (High → Medium → Low)
- See `issues/README.md` for detailed overview of all issues
- See `CODE_QUALITY_ISSUES.md` for comprehensive analysis

## Related Files

- `create-github-issues.sh` - Bash script for automated issue creation
- `create_github_issues.py` - Python script for automated issue creation
- `GITHUB_ISSUES_GUIDE.md` - Comprehensive guide for issue creation
- `issues/README.md` - Overview of all code quality issues
- `CODE_QUALITY_ISSUES.md` - Full analysis report
