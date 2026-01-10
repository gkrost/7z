# 7-Zip Code Quality Issues

This directory contains detailed issue reports for code quality problems found in the 7-Zip codebase. Each issue is in a separate markdown file that can be used to create GitHub issues.

## Quick Start

Each file in this directory is a standalone issue report that can be copy-pasted directly into a GitHub issue. The issues are prioritized and categorized for easy triage.

## Issue Index

### High Priority (Security/Correctness)

1. **[issue-01-unsafe-string-functions.md](issue-01-unsafe-string-functions.md)**
   - Replace unsafe C string functions (sprintf, strcpy, etc.) with safe alternatives
   - **Category**: Security Vulnerability
   - **Impact**: Buffer overflow vulnerabilities

2. **[issue-03-unsafe-atomic-hack.md](issue-03-unsafe-atomic-hack.md)**
   - Replace USE_HACK_UNSAFE_ATOMIC with proper atomic operations
   - **Category**: Potential Race Condition
   - **Impact**: Concurrency bugs, memory corruption

### Medium Priority (Maintainability/Future Compatibility)

3. **[issue-02-dead-code-if0-blocks.md](issue-02-dead-code-if0-blocks.md)**
   - Remove or document 139 disabled code blocks (#if 0)
   - **Category**: Dead Code
   - **Impact**: Code maintenance, clarity

4. **[issue-04-deprecated-getversion-api.md](issue-04-deprecated-getversion-api.md)**
   - Update deprecated Windows GetVersion() API usage
   - **Category**: Deprecated API
   - **Impact**: Future Windows compatibility

5. **[issue-05-deprecated-arm-crypto-macros.md](issue-05-deprecated-arm-crypto-macros.md)**
   - Update deprecated ARM crypto feature detection macros
   - **Category**: Deprecated Macros
   - **Impact**: Future ARM compiler compatibility

6. **[issue-06-compiler-workarounds.md](issue-06-compiler-workarounds.md)**
   - Document and review compiler-specific workarounds
   - **Category**: Compiler Workarounds / Technical Debt
   - **Impact**: Code maintainability, compiler support

### Low Priority (Code Cleanliness)

7. **[issue-07-commented-debug-code.md](issue-07-commented-debug-code.md)**
   - Clean up commented-out debug code and defines
   - **Category**: Dead Code / Debug Code
   - **Impact**: Code readability

8. **[issue-08-naked-functions.md](issue-08-naked-functions.md)**
   - Review and document naked function usage
   - **Category**: Legacy Assembly
   - **Impact**: Code maintainability, portability

## Statistics

- **Total Issues**: 8
- **High Priority**: 2
- **Medium Priority**: 4
- **Low Priority**: 2
- **Total C/C++ files**: ~999
- **Files with issues**: 50+

## How to Use These Issues

### Creating GitHub Issues

1. Choose an issue file from the list above
2. Copy the entire content of the markdown file
3. Create a new GitHub issue
4. Paste the content as the issue description
5. Add appropriate labels (security, bug, enhancement, etc.)
6. Assign to appropriate milestone

### Issue Labels Suggestions

- `security` - For issues 01, 03
- `technical-debt` - For issues 02, 06, 07
- `deprecated` - For issues 04, 05
- `maintenance` - For issues 02, 07, 08
- `legacy-code` - For issues 06, 08
- `platform-specific` - For issues 04, 05, 08

### Recommended Order of Resolution

**Phase 1: Security (Immediate)**
1. Issue #01: Unsafe string functions
2. Issue #03: Unsafe atomic operations

**Phase 2: Deprecation (Next release)**
3. Issue #04: GetVersion API
4. Issue #05: ARM crypto macros

**Phase 3: Technical Debt (Ongoing)**
5. Issue #06: Compiler workarounds
6. Issue #02: Dead code blocks

**Phase 4: Cleanup (Low priority)**
7. Issue #07: Commented debug code
8. Issue #08: Naked functions

## Contributing

When working on these issues:

1. **Test thoroughly** across all supported platforms
2. **Maintain backward compatibility** unless explicitly dropping old platform support
3. **Update documentation** in DOC/ directory
4. **Add tests** where applicable
5. **Follow existing code style**
6. **Reference the issue** in commit messages

## Related Documents

- `../CODE_QUALITY_ISSUES.md` - Comprehensive analysis report
- `../DOC/readme.txt` - Project README
- `../DOC/src-history.txt` - Source code history

## Notes

This analysis was performed on 7-Zip 25.01 sources. Some issues may be intentional for compatibility with older systems or compilers. Always consult with maintainers before making significant changes.
