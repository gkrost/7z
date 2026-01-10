# 7-Zip Source Code

[![License: LGPL v2.1+](https://img.shields.io/badge/License-LGPL%20v2.1+-blue.svg)](LICENSE.md)
[![Version](https://img.shields.io/badge/version-25.01-green.svg)](DOC/src-history.txt)

7-Zip is a file archiver with a high compression ratio.

## Features

- **High compression ratio** in 7z format with LZMA and LZMA2 compression
- **Supported formats:**
  - Packing / unpacking: 7z, XZ, BZIP2, GZIP, TAR, ZIP and WIM
  - Unpacking only: APFS, AR, ARJ, CAB, CHM, CPIO, CramFS, DMG, EXT, FAT, GPT, HFS, IHEX, ISO, LZH, LZMA, MBR, MSI, NSIS, NTFS, QCOW2, RAR, RPM, SquashFS, UDF, UEFI, VDI, VHD, VHDX, VMDK, XAR and Z
- **Strong AES-256 encryption** in 7z and ZIP formats
- **Self-extracting capability** for 7z format
- **Integration with Windows Shell**
- **Powerful File Manager**
- **Powerful command line version**
- **Localizations** for 87 languages

## Quick Links

- 🏠 [Official Website](http://www.7-zip.org)
- 📖 [Building Instructions](BUILDING.md)
- 🤝 [Contributing Guidelines](CONTRIBUTING.md)
- 📄 [License Information](LICENSE.md)
- 🏗️ [Architecture Documentation](docs/ARCHITECTURE.md)
- 🔌 [API Documentation](docs/API.md)

## For End Users

If you're looking to download and use 7-Zip, please visit the [official 7-Zip website](http://www.7-zip.org) for pre-built binaries and installers.

This repository contains the **source code** for developers who want to build 7-Zip themselves or contribute to the project.

## For Developers

### Quick Start

**Windows:**
```cmd
cd CPP\7zip\Bundles\Alone2
nmake
```

**Linux/macOS:**
```bash
cd CPP/7zip/Bundles/Alone2
make -j -f makefile.gcc
```

See [BUILDING.md](BUILDING.md) for detailed build instructions.

### Project Structure

```
7z/
├── Asm/          # Assembly optimized code (CRC, SHA, AES, LZMA)
├── C/            # C implementation of core algorithms
├── CPP/          # C++ implementation
│   ├── 7zip/     # Main 7-Zip code
│   ├── Common/   # Common utilities
│   └── Windows/  # Windows-specific code
└── DOC/          # Documentation files
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture information.

## Licensing

7-Zip is free software distributed under the **GNU LGPL** license (except for unRAR code).

- Most files: **GNU LGPL v2.1+**
- RAR decompression: **GNU LGPL + unRAR restriction**
- Some files: **BSD 3-clause** or **BSD 2-clause** licenses
- Some files: **Public Domain**

See [LICENSE.md](LICENSE.md) for complete licensing information.

**Important**: The unRAR code has restrictions - it cannot be used to develop a RAR-compatible archiver.

## Security

7-Zip takes security seriously. If you discover a security vulnerability, please report it responsibly.

Recent security fixes are documented in [DOC/src-history.txt](DOC/src-history.txt).

## Support

- **Website**: http://www.7-zip.org
- **Forum**: http://sourceforge.net/projects/sevenzip/forums
- **Bug Reports**: Use the SourceForge forum or submit issues on GitHub

## Credits

7-Zip is developed by **Igor Pavlov**.

Copyright (C) 1999-2025 Igor Pavlov.

## Additional Information

- **7z Format Specification**: [DOC/7zFormat.txt](DOC/7zFormat.txt)
- **Compression Methods**: [DOC/Methods.txt](DOC/Methods.txt)
- **LZMA SDK**: [DOC/lzma.txt](DOC/lzma.txt)
- **Source History**: [DOC/src-history.txt](DOC/src-history.txt)
