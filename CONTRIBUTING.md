# Contributing to 7-Zip

Thank you for your interest in contributing to 7-Zip! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

- Be respectful and constructive in all interactions
- Focus on what is best for the community and the project
- Show empathy towards other community members

## How Can I Contribute?

### Types of Contributions

1. **Bug Fixes** - Fix issues in existing code
2. **Performance Improvements** - Optimize algorithms and code
3. **New Features** - Add support for new formats or capabilities
4. **Documentation** - Improve or translate documentation
5. **Testing** - Test on different platforms and configurations
6. **Code Review** - Review pull requests from other contributors

### Areas of Contribution

- **Compression Algorithms** - Improve LZMA, LZMA2, or other algorithms
- **Format Support** - Add or improve archive format handlers
- **Platform Support** - Improve compatibility with different OS/architectures
- **Security** - Find and fix security vulnerabilities
- **User Interface** - Improve GUI or command-line interface (Windows)
- **Performance** - Optimize code for speed or memory usage

## Development Setup

### Prerequisites

See [BUILDING.md](BUILDING.md) for detailed build instructions.

### Setting Up Your Development Environment

1. **Fork the repository** (if contributing via GitHub)

2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/7z.git
   cd 7z
   ```

3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Build the project** to ensure everything works:
   - Windows: See [BUILDING.md - Windows](BUILDING.md#building-on-windows)
   - Linux/macOS: See [BUILDING.md - Linux/macOS](BUILDING.md#building-on-linuxmacos)

## Coding Standards

### General Guidelines

- **Maintain consistency** - Follow the existing code style in the file you're editing
- **Keep changes minimal** - Make the smallest change necessary to fix an issue or add a feature
- **Comment wisely** - Add comments for complex logic, but let code be self-documenting when possible
- **Test thoroughly** - Test your changes on multiple platforms if possible

### C/C++ Style

Based on existing codebase patterns:

- **Naming Conventions**:
  - Types/Classes: `PascalCase` (e.g., `CMyClass`, `SMyStruct`)
  - Functions/Methods: `PascalCase` (e.g., `DoSomething()`)
  - Variables: `camelCase` or `lowerCase` depending on context
  - Constants/Macros: `UPPER_CASE` with underscores

- **Formatting**:
  - Use existing indentation style (typically 2 spaces)
  - Opening braces on same line for functions (K&R style in most files)
  - No trailing whitespace

- **Memory Management**:
  - Use appropriate allocation/deallocation pairs
  - Check for allocation failures
  - Avoid memory leaks

### Assembly Code

- Follow MASM syntax for x86/x64
- Follow GNU assembler syntax for ARM64
- Add comments explaining complex operations
- Test on target architectures

## Submitting Changes

### Before Submitting

1. **Build successfully** on your platform
2. **Test your changes** thoroughly:
   - Create and extract archives
   - Test with different compression methods
   - Test with large files and many files
   - Test edge cases

3. **Check for issues**:
   - No memory leaks (use valgrind on Linux, or similar tools)
   - No crashes or undefined behavior
   - No performance regressions

4. **Update documentation** if needed:
   - Update README.md if changing features
   - Update BUILDING.md if changing build process
   - Update relevant DOC/*.txt files if applicable

### Pull Request Process

1. **Commit your changes** with clear, descriptive commit messages:
   ```bash
   git commit -m "Fix memory leak in LZMA decoder"
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request** with:
   - **Clear title** describing the change
   - **Description** explaining:
     - What the change does
     - Why it's needed
     - How you tested it
     - Any potential impacts
   - **Reference issues** if fixing a reported bug

4. **Respond to feedback** - Be prepared to make changes based on code review

### Commit Message Guidelines

Good commit messages help understand the history:

```
Brief summary of changes (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain the problem this commit solves and why this approach
was taken.

Fixes: #123
```

## Reporting Bugs

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Use the latest version** to ensure the bug still exists
3. **Test with minimal configuration** to isolate the issue

### Bug Report Should Include

- **7-Zip version** (e.g., 25.01)
- **Platform/OS** (e.g., Windows 11, Ubuntu 22.04, macOS 14)
- **Architecture** (e.g., x64, ARM64)
- **Steps to reproduce** the issue
- **Expected behavior**
- **Actual behavior**
- **Sample files** if applicable (ensure no sensitive data)
- **Error messages** or crash logs

### Where to Report

- **GitHub Issues** (for this repository)
- **SourceForge Forum**: https://sourceforge.net/projects/sevenzip/forums
- **Official 7-Zip Website**: https://www.7-zip.org

### Security Issues

⚠️ **Do not report security vulnerabilities publicly**

For security issues:
1. Contact the maintainers privately
2. Provide detailed information about the vulnerability
3. Allow time for a fix before public disclosure

## Suggesting Enhancements

### Feature Requests

When suggesting new features:

- **Explain the use case** - Why is this feature needed?
- **Describe the feature** - What should it do?
- **Consider alternatives** - Are there existing ways to accomplish this?
- **Think about impacts** - How might this affect existing functionality?

### Enhancement Locations

- **New compression methods** - Discuss on forums first
- **New archive formats** - Ensure licensing compatibility
- **UI improvements** - Consider cross-platform implications
- **Performance** - Include benchmarks if possible

## License Compliance

When contributing code, ensure:

- **Your code is original** or properly attributed
- **Licensing is compatible** with GNU LGPL v2.1+
- **No proprietary algorithms** are used without permission
- **Third-party code** includes proper license headers
- **You have rights** to contribute the code

### License Headers

Add appropriate license headers to new files:

```cpp
// 7-Zip Source Code
// Copyright (C) 2025 [Your Name]
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 2.1 of the License, or (at your option) any later version.
```

## Getting Help

If you need help with development:

- **Read the documentation** in [DOC/](DOC/) directory
- **Study existing code** for examples
- **Ask on forums** - https://sourceforge.net/projects/sevenzip/forums
- **Check Architecture docs** - [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Recognition

Contributors are acknowledged in various ways:
- Credit in source code comments where appropriate
- Mention in release notes for significant contributions
- Community recognition and appreciation

## Additional Resources

- [BUILDING.md](BUILDING.md) - Build instructions
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Code structure
- [docs/API.md](docs/API.md) - API documentation
- [DOC/7zFormat.txt](DOC/7zFormat.txt) - 7z format specification
- [Official Website](https://www.7-zip.org) - Main 7-Zip website

---

Thank you for contributing to 7-Zip! 🎉
