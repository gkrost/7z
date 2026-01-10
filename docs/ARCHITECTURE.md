# 7-Zip Architecture Documentation

This document provides an overview of the 7-Zip source code architecture and organization.

## Table of Contents

- [High-Level Architecture](#high-level-architecture)
- [Directory Structure](#directory-structure)
- [Core Components](#core-components)
- [Archive Formats](#archive-formats)
- [Compression Methods](#compression-methods)
- [Platform Abstraction](#platform-abstraction)
- [Build System](#build-system)

## High-Level Architecture

7-Zip uses a modular architecture with clear separation between:

1. **Compression/Decompression Engines** - Core algorithms (LZMA, LZMA2, etc.)
2. **Format Handlers** - Archive format readers/writers (7z, ZIP, TAR, etc.)
3. **User Interfaces** - Console, GUI, File Manager (Windows)
4. **Platform Layer** - OS-specific functionality
5. **Common Utilities** - Shared code (buffers, streams, etc.)

### Component Interaction

```
┌─────────────────────────────────────────┐
│         User Interface Layer            │
│  (Console, GUI, File Manager, DLLs)     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Archive Handler Layer           │
│  (7z, ZIP, TAR, RAR, CAB, ISO, etc.)    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│      Compression/Crypto Layer           │
│   (LZMA, LZMA2, PPMd, BCJ, AES, etc.)   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│       Platform Abstraction Layer        │
│     (File I/O, Threading, Memory)       │
└─────────────────────────────────────────┘
```

## Directory Structure

### Top-Level Layout

```
7z/
├── Asm/          Assembly-optimized implementations
├── C/            C language implementations
├── CPP/          C++ implementations (main codebase)
└── DOC/          Documentation files
```

### Asm/ - Assembly Optimizations

Performance-critical code in assembly for different architectures:

```
Asm/
├── x86/          x86 32-bit assembly (MASM syntax)
├── x64/          x86-64 assembly (MASM syntax)
└── arm64/        ARM64 assembly (GNU syntax)
```

**Optimized Components**:
- **CRC** calculation
- **SHA-1/SHA-256** hashing
- **AES** encryption/decryption
- **LZMA** decoder components

### C/ - C Implementation

Pure C implementations for portability and performance:

```
C/
├── 7z*           7z ANSI-C decoder
├── Lzma*         LZMA encoder/decoder
├── Xz*           XZ format support
├── Threads.*     Threading abstraction
├── Alloc.*       Memory allocation
├── Aes.*         AES encryption
├── Sha*.c        SHA hashing
└── Util/         Example utilities
    ├── 7z/       7z decoder test app
    ├── Lzma/     LZMA utility
    └── LzmaLib/  LZMA library
```

### CPP/ - C++ Implementation

Main codebase with full functionality:

```
CPP/
├── Common/       Common C++ utilities
├── Windows/      Windows-specific code
└── 7zip/         Main 7-Zip code
    ├── Archive/  Archive format handlers
    ├── Bundle/   Bundled executables & DLLs
    ├── Common/   7-Zip common code
    ├── Compress/ Compression codecs
    ├── Crypto/   Encryption modules
    └── UI/       User interfaces
```

## Core Components

### CPP/Common/ - Common Utilities

Fundamental utility classes used throughout:

- **String Handling**: `MyString.h`, `MyString.cpp`
- **Buffers**: `MyBuffer.h`
- **File I/O**: `MyTypes.h`
- **Containers**: `MyVector.h`, `MyList.h`
- **Wildcards**: `Wildcard.cpp`
- **Integer Conversion**: `IntToString.cpp`

### CPP/Windows/ - Windows Platform Layer

Windows-specific implementations:

- **File Operations**: `FileDir.cpp`, `FileFind.cpp`, `FileIO.cpp`
- **File Attributes**: `FileInfo.cpp`
- **DLL Loading**: `DLL.cpp`
- **Registry**: `Registry.cpp`
- **Resources**: `ResourceString.cpp`
- **Synchronization**: `Synchronization.cpp`

### CPP/7zip/Common/ - 7-Zip Common

Core 7-Zip functionality:

- **Stream Abstractions**: `StreamObjects.cpp`, `StreamUtils.cpp`
- **File Streams**: `FileStreams.cpp`
- **Progress Callbacks**: `ProgressUtils.cpp`
- **Filter Streams**: `FilterCoder.cpp`
- **Multi-threading**: `OutMemStream.cpp`

## Archive Formats

Located in `CPP/7zip/Archive/`, each format has its own subdirectory:

### Major Formats

| Format | Directory | Read | Write | Notes |
|--------|-----------|------|-------|-------|
| **7z** | `7z/` | ✓ | ✓ | Native format, full features |
| **ZIP** | `Zip/` | ✓ | ✓ | Wide compatibility |
| **TAR** | `Tar/` | ✓ | ✓ | Unix archive format |
| **GZIP** | `GZip/` | ✓ | ✓ | Single file compression |
| **BZIP2** | `BZip2/` | ✓ | ✓ | Single file compression |
| **XZ** | `Xz/` | ✓ | ✓ | LZMA2 compression |
| **RAR** | `Rar/` | ✓ | ✗ | Decompression only |
| **CAB** | `Cab/` | ✓ | ✓ | Microsoft cabinet |
| **ISO** | `Iso/` | ✓ | ✗ | CD/DVD images |
| **WIM** | `Wim/` | ✓ | ✓ | Windows Imaging |

### Format Handler Structure

Each format handler typically contains:

```
FormatName/
├── Handler.cpp        Main format handler
├── Header.h          Format-specific constants
├── In.cpp            Archive reading
├── Out.cpp           Archive writing (if supported)
├── Update.cpp        Archive updating
└── [Format]Register.cpp  Registration
```

### Handler Interface

Archive handlers implement interfaces defined in:
- `CPP/7zip/Archive/IArchive.h` - Main archive interface
- `CPP/7zip/IStream.h` - Stream operations
- `CPP/7zip/ICoder.h` - Compression/decompression

## Compression Methods

Located in `CPP/7zip/Compress/`:

### Primary Compression Codecs

| Codec | Files | Description |
|-------|-------|-------------|
| **LZMA** | `LzmaDecoder.cpp`, `LzmaEncoder.cpp` | Main compression method |
| **LZMA2** | `Lzma2Decoder.cpp`, `Lzma2Encoder.cpp` | Multi-threaded LZMA |
| **PPMd** | `PpmdDecoder.cpp`, `PpmdEncoder.cpp` | Prediction by Partial Matching |
| **Deflate** | `DeflateDecoder.cpp`, `DeflateEncoder.cpp` | ZIP compression |
| **BZip2** | `BZip2Decoder.cpp`, `BZip2Encoder.cpp` | Burrows-Wheeler |
| **ZSTD** | `ZstdDecoder.cpp` | Zstandard (decode only) |
| **LZFSE** | `LzfseDecoder.cpp` | Apple's LZFSE (decode only) |

### Codec Architecture

Codecs implement the `ICompressCoder` interface:

```cpp
interface ICompressCoder {
  HRESULT Code(
    ISequentialInStream *inStream,
    ISequentialOutStream *outStream,
    const UInt64 *inSize,
    const UInt64 *outSize,
    ICompressProgressInfo *progress
  );
};
```

### Filter Codecs (BCJ)

Branch/Call/Jump filters for executables:

- **BCJ** - x86 filter
- **BCJ2** - Advanced x86 filter
- **ARMT** - ARM Thumb
- **ARM64** - ARM 64-bit
- **PPC** - PowerPC
- **IA64** - Itanium
- **SPARC** - SPARC

## Platform Abstraction

### File I/O

Platform-specific file operations are abstracted:

**Windows**: `CPP/Windows/FileIO.cpp`
**Unix/Linux**: Uses standard POSIX APIs

Interface: `IInStream`, `IOutStream`, `IStreamGetSize`

### Threading

Multi-threading support for compression:

**Windows**: `CPP/Windows/Synchronization.cpp`, `CPP/Windows/Thread.cpp`
**Unix/Linux**: `C/Threads.c` (uses pthreads)

### Memory Allocation

Custom allocators for performance:

- `C/Alloc.c` - General allocation
- `C/7zAlloc.c` - 7z-specific allocation
- Large page support on Windows for better performance

## Build System

### Windows Build

Uses **nmake** with Visual Studio:

- **Main makefile**: `CPP/7zip/makefile`
- **Component makefiles**: Each component has its own makefile
- **Build chain**: Top-level makefile includes component makefiles

### Unix/Linux Build

Uses **make** with GCC/Clang:

- **Generic makefile**: `makefile.gcc` in each component
- **Optimized makefiles**: `cmpl_gcc.mak`, `cmpl_clang.mak`, etc.
- **Variable files**: `var_gcc.mak` for compiler settings
- **Warning files**: `warn_gcc.mak` for warning flags

### Build Outputs

Different executables serve different purposes:

| Output | Purpose | Formats | Platform |
|--------|---------|---------|----------|
| **7zz** | Full standalone console | All | All platforms |
| **7za** | Limited standalone console | 7z, xz, zip, gzip, bzip2, tar | All platforms |
| **7zr** | Minimal console | 7z only | All platforms |
| **7z.exe** | Console with DLLs | All | Windows |
| **7zG.exe** | GUI | All | Windows |
| **7zFM.exe** | File Manager | All | Windows |

## Bundles

Located in `CPP/7zip/Bundles/`, bundles combine components:

### Standalone Executables

- **Alone2** (`7zz`) - All formats, no external dependencies
- **Alone** (`7za`) - Limited formats, no external dependencies  
- **Alone7z** (`7zr`) - 7z format only, minimal size

### DLLs (Windows)

- **Format7zF** (`7z.dll`) - All formats
- **Format7z** (`7za.dll`) - 7z format
- **Format7zR** (`7zr.dll`) - 7z format, reduced

### SFX Modules (Windows)

- **SFXCon** (`7zCon.sfx`) - Console self-extractor
- **SFXWin** (`7z.sfx`) - Windows self-extractor
- **SFXSetup** (`7zS.sfx`) - Setup self-extractor

## User Interfaces

Located in `CPP/7zip/UI/`:

### Console (`UI/Console/`)

Command-line interface for all platforms:
- Batch operations
- Scripting support
- Progress display
- Error handling

### GUI (`UI/GUI/` - Windows only)

Simple graphical interface:
- Extract wizard
- Compress dialog
- Test archives

### File Manager (`UI/FileManager/` - Windows only)

Full-featured file manager:
- Two-panel interface
- Archive browsing
- Drag and drop
- Context menus
- Settings dialog

## Data Flow Example: Creating a 7z Archive

1. **User Interface** receives command/request
2. **Update Manager** (`CPP/7zip/UI/Common/Update.cpp`) coordinates operation
3. **7z Handler** (`CPP/7zip/Archive/7z/7zOut.cpp`) creates archive structure
4. **Encoder** (`CPP/7zip/Compress/LzmaEncoder.cpp`) compresses data
5. **Filter** (e.g., BCJ) preprocesses if needed
6. **Stream** writes to output file

## Extension Points

To add new functionality:

1. **New Archive Format**: Implement `IInArchive`/`IOutArchive` in `Archive/`
2. **New Codec**: Implement `ICompressCoder` in `Compress/`
3. **New Filter**: Implement filter interface in `Compress/`
4. **New Hash**: Add to `Common/` and register

## Additional Resources

- **7z Format**: [DOC/7zFormat.txt](../DOC/7zFormat.txt)
- **Methods**: [DOC/Methods.txt](../DOC/Methods.txt)
- **Building**: [BUILDING.md](../BUILDING.md)
- **API Usage**: [API.md](API.md)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to the codebase.
