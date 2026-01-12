# Building 7-Zip from Source

This guide provides detailed instructions for building 7-Zip from source on different platforms.

**Note**: For detailed information about compiler versions, compatibility, and compiler-specific workarounds, see [COMPILER_REQUIREMENTS.md](COMPILER_REQUIREMENTS.md).

## Table of Contents

- [Prerequisites](#prerequisites)
- [Building on Windows](#building-on-windows)
- [Building on Linux/macOS](#building-on-linuxmacos)
- [Build Targets](#build-targets)
- [Build Options](#build-options)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Windows

- **Visual Studio 2017 or later** (minimum: VS 2017, recommended: VS 2019/2022)
  - **Minimum MSVC version**: _MSC_VER 1910 (Visual Studio 2017)
  - Older versions (VS2010-2015) may work with compiler workarounds, but are not tested
  - See [COMPILER_REQUIREMENTS.md](COMPILER_REQUIREMENTS.md) for detailed version info and workarounds
- **Microsoft Macro Assembler**:
  - `ml.exe` for x86
  - `ml64.exe` for x64
  - Available in Windows SDK for Windows Vista or later

### Linux/macOS

- **GCC 7 or later** or **Clang 5 or later**
  - **Minimum GCC version**: 7.0 (GCC 5+ may work with workarounds)
  - **Minimum Clang version**: 5.0 (Clang 3.8+ may work with workarounds)
  - See [COMPILER_REQUIREMENTS.md](COMPILER_REQUIREMENTS.md) for detailed version info and workarounds
- **Make** utility
- **Optional**: Assembler for optimized builds
  - [Asmc Macro Assembler](https://github.com/nidud/asmc) (recommended for x86/x64)
  - [UASM](https://github.com/Terraspace/UASM) (alternative for x86/x64)
  - GNU assembler (built-in for ARM64)

## Building on Windows

### Method 1: Command Line (Recommended for Release Builds)

This method provides the best optimization.

#### 1. Set up Visual Studio Environment

For x64 build:
```cmd
cd CPP\7zip
%comspec% /k "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
```

For x86 build:
```cmd
%comspec% /k "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsamd64_x86.bat"
```

For ARM64 build:
```cmd
%comspec% /k "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsamd64_arm64.bat"
```

#### 2. Build All Components

```cmd
nmake
```

#### 3. Build Specific Component

To build just the standalone console version (7zz.exe):
```cmd
cd Bundles\Alone2
nmake
```

To build the console version (7z.exe):
```cmd
cd UI\Console
nmake
```

To build 7za.exe (limited format support):
```cmd
cd Bundles\Alone
nmake
```

### Method 2: Visual Studio IDE

The upstream build uses `nmake` makefiles. For IDE-based development/debugging,
create a Visual Studio **NMake** project (or open a folder) and point it at the
same `nmake` commands you use on the command line.

**Note**: IDE usage is convenient for development and debugging, but release binaries should be built via `nmake` for consistent results.

### Build Options for Windows

You can define these macros when building:

- `PLATFORM=x64` or `x86` or `arm64` or `arm` or `ia64`
- `MY_DYNAMIC_LINK=1` - For dynamic linking to msvcrt.dll (default is static)

Example:
```cmd
nmake PLATFORM=x64
```

## Building on Linux/macOS

### Quick Build (No Assembly Optimization)

The easiest way to build on Unix-like systems:

```bash
cd CPP/7zip/Bundles/Alone2
make -j -f makefile.gcc
```

The resulting binary will be `b/g/7zz` (or `b/g_arm64/7zz` on ARM64).

### Optimized Builds

For best performance, use the specialized makefiles with assembly code:

#### GCC without Assembly
```bash
cd CPP/7zip/Bundles/Alone2
make -j -f ../../cmpl_gcc.mak
```

#### Clang without Assembly
```bash
make -j -f ../../cmpl_clang.mak
```

#### x86-64 with ASMC Assembler (Fastest)
```bash
make -j -f ../../cmpl_gcc_x64.mak
```

#### ARM64 with Assembly
```bash
make -j -f ../../cmpl_gcc_arm64.mak
```

#### macOS ARM64 (Apple Silicon)
```bash
make -j -f ../../cmpl_mac_arm64.mak
```

### Installing ASMC Assembler for x86/x64

For optimized x86/x64 builds on Linux, install ASMC:

> **⚠️ Security Note**: The instructions below clone and install third-party software from GitHub. For production builds, consider using distribution packages if available, or pin to a specific release tag and verify signatures/checksums. Installing from arbitrary HEAD commits without verification may pose supply-chain security risks.

**Option 1: Install from source (development/testing)**
```bash
# Clone a specific release tag instead of HEAD for reproducibility
git clone --depth 1 --branch v2.60 https://github.com/nidud/asmc.git
cd asmc/source
make
sudo make install
```

**Option 2: Manual installation without sudo**
```bash
git clone --depth 1 https://github.com/nidud/asmc.git
cd asmc/source
make
# Install to local directory instead of system-wide
mkdir -p ~/bin
cp asmc ~/bin/
export PATH="$HOME/bin:$PATH"
```

Or install UASM:

> **⚠️ Security Note**: Similar to ASMC, installing from arbitrary commits without verification may pose security risks. Consider pinning to a release or using a local installation path.

**Option 1: Install from source (development/testing)**
```bash
# Clone a specific release or commit for reproducibility
git clone --depth 1 https://github.com/Terraspace/UASM.git
cd UASM
make -f gcc64.mak
sudo cp uasm /usr/local/bin/
```

**Option 2: Manual installation without sudo**
```bash
git clone --depth 1 https://github.com/Terraspace/UASM.git
cd UASM
make -f gcc64.mak
# Install to local directory
mkdir -p ~/bin
cp uasm ~/bin/
export PATH="$HOME/bin:$PATH"
```

### Using UASM

If you prefer UASM over ASMC:

```bash
UASM="$PWD/GccUnixR/uasm"
cd CPP/7zip/Bundles/Alone2
make -f makefile.gcc -j IS_X64=1 USE_ASM=1 MY_ASM="$UASM"
```

### Build Options for Linux/macOS

Environment variables for makefile.gcc:

- `USE_JWASM=1` - Use JWasm instead of ASMC (note: JWasm doesn't support AES instructions)
- `DISABLE_RAR=1` - Remove all RAR support from build
- `DISABLE_RAR_COMPRESS=1` - Remove RAR decompression codecs (keeps RAR archive listing)

Examples:

```bash
# Build without RAR support
make -j -f makefile.gcc DISABLE_RAR=1

# Build without RAR decompression (only listing)
make -j -f makefile.gcc DISABLE_RAR_COMPRESS=1
```

## Build Targets

### Available Binaries

| Binary | Description | Location |
|--------|-------------|----------|
| **7zz.exe/7zz** | Standalone console version, all formats | `CPP/7zip/Bundles/Alone2` |
| **7za.exe** | Standalone console, limited formats (7z/xz/cab/zip/gzip/bzip2/tar) | `CPP/7zip/Bundles/Alone` |
| **7zr.exe** | Standalone console, 7z format only | `CPP/7zip/Bundles/Alone7z` |
| **7z.exe** | Console version (Windows) | `CPP/7zip/UI/Console` |
| **7zG.exe** | GUI version (Windows) | `CPP/7zip/UI/GUI` |
| **7zFM.exe** | File Manager (Windows) | `CPP/7zip/UI/FileManager` |
| **7z.dll** | Format handler DLL, all formats | `CPP/7zip/Bundles/Format7zF` |
| **7za.dll** | Format handler DLL, 7z format | `CPP/7zip/Bundles/Format7z` |

### Self-Extracting Modules (Windows)

| Module | Description | Location |
|--------|-------------|----------|
| **7zCon.sfx** | Console SFX module | `CPP/7zip/Bundles/SFXCon` |
| **7z.sfx** | Windows SFX module | `CPP/7zip/Bundles/SFXWin` |
| **7zS.sfx** | Setup SFX module | `CPP/7zip/Bundles/SFXSetup` |

## Troubleshooting

### Windows Issues

**Problem**: `ml.exe` or `ml64.exe` not found
- **Solution**: Install Windows SDK or ensure the SDK bin directory is in your PATH

**Problem**: Unsupported compiler version
- **Solution**: 7-Zip requires Visual Studio 2017 or later. Please upgrade your compiler.

### Linux/macOS Issues

**Problem**: Assembly errors with ASMC/UASM
- **Solution**: Build without assembly optimization using `makefile.gcc` or `cmpl_gcc.mak`

**Problem**: `make: command not found`
- **Solution**: Install build tools:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install build-essential
  
  # macOS
  xcode-select --install
  ```

**Problem**: Compiler not found
- **Solution**: Install GCC or Clang:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install gcc g++
  
  # macOS (installs clang)
  xcode-select --install
  ```

### Performance Issues

If your build is slower than expected:
- Use the `-j` flag with make for parallel compilation: `make -j`
- On Windows, ensure you're using the makefile method, not Visual Studio IDE
- Consider using assembly-optimized builds for x86-64 or ARM64

## Testing Your Build

After building, test the binary:

```bash
# Linux/macOS
./b/g/7zz --help

# Windows
7zz.exe --help
```

Create a test archive:
```bash
# Linux/macOS
./b/g/7zz a test.7z /path/to/files

# Windows
7zz.exe a test.7z C:\path\to\files
```

## Next Steps

- See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for code structure
- See [docs/API.md](docs/API.md) for using 7-Zip libraries in your projects
