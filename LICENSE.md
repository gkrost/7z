# 7-Zip License Information

7-Zip source code is licensed under multiple free software licenses depending on the specific files.

## Summary

- **Most files**: GNU LGPL v2.1+
- **RAR decompression code**: GNU LGPL v2.1+ with unRAR restriction
- **Some files**: BSD 3-clause License
- **Some files**: BSD 2-clause License
- **Some files**: Public Domain

---

## Copyright

**7-Zip Copyright (C) 1999-2025 Igor Pavlov.**

---

## File-Specific Licenses

### GNU LGPL Files (Most of the Code)

The following files are under the **GNU Lesser General Public License v2.1+**:
- All files without specific license information in their header
- General 7-Zip compression and archiving code

### GNU LGPL + unRAR Restriction

The following files are under **GNU LGPL v2.1+ with unRAR license restriction**:
- `CPP/7zip/Compress/Rar*` files (RAR decompression code)

### BSD 3-clause License

The following files are under the **BSD 3-clause License**:
- `CPP/7zip/Compress/LzfseDecoder.cpp` (LZFSE decompression, derived from Apple Inc. code)
- `C/ZstdDec.c` (ZSTD decompression, developed using Facebook Inc. reference code)

### BSD 2-clause License

The following files are under the **BSD 2-clause License**:
- `C/Xxh64.c` (XXH64 hashing, derived from Yann Collet's code)

### Public Domain

Some files are in the **public domain**, specifically stated in their source file headers.

---

## GNU Lesser General Public License v2.1+

This library is free software; you can redistribute it and/or modify it under the terms of the **GNU Lesser General Public License** as published by the Free Software Foundation; either version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful, but **WITHOUT ANY WARRANTY**; without even the implied warranty of **MERCHANTABILITY** or **FITNESS FOR A PARTICULAR PURPOSE**. See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with this library; if not, you can get a copy from:
- **Web**: http://www.gnu.org/licenses/lgpl-2.1.html
- **File**: [DOC/copying.txt](DOC/copying.txt) (full LGPL text included in this repository)

---

## unRAR License Restriction

### Overview

The decompression engine for RAR archives was developed using source code of the unRAR program. All copyrights to original unRAR code are owned by **Alexander Roshal**.

### Restriction

The unRAR sources cannot be used to **re-create the RAR compression algorithm**, which is proprietary.

Distribution of modified unRAR sources in separate form or as a part of other software is permitted, provided that it is clearly stated in the documentation and source comments that **the code may not be used to develop a RAR (WinRAR) compatible archiver**.

### What This Means

✅ **You CAN**:
- Compile and use compiled files under GNU LGPL rules
- Link compiled files to LGPL programs
- Fix bugs in source code and use the compiled fixed version
- Use the code to **decompress** RAR archives

❌ **You CANNOT**:
- Use unRAR sources to **create** RAR archives
- Develop a RAR-compatible archiver/compressor

### Excluding RAR Code

If you want to exclude RAR code from your build due to licensing concerns:

- **Remove all RAR support**: Build with `DISABLE_RAR=1`
- **Remove RAR decompression only**: Build with `DISABLE_RAR_COMPRESS=1` (keeps archive listing capability)

See [BUILDING.md](BUILDING.md) for details.

---

## BSD 3-clause License

### Applicable Files

1. **LZFSE decompression** (`CPP/7zip/Compress/LzfseDecoder.cpp`)
   - Derived from Apple Inc.'s LZFSE compression library
   
2. **ZSTD decompression** (`C/ZstdDec.c`)
   - Developed using Facebook Inc.'s original zstd decoder as reference

### Copyright Notices

- Copyright (c) 2015-2016, Apple Inc. All rights reserved.
- Copyright (c) Facebook, Inc. All rights reserved.
- Copyright (c) 2023-2025 Igor Pavlov.

### License Text

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

---

## BSD 2-clause License

### Applicable Files

**XXH64 hashing** (`C/Xxh64.c`)
- Derived from Yann Collet's original XXH64 code

### Copyright Notices

- Copyright (c) 2012-2021 Yann Collet.
- Copyright (c) 2023-2025 Igor Pavlov.

### License Text

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

---

## LZMA SDK

This package contains some files from **LZMA SDK**.

LZMA SDK is written and placed in the **public domain** by Igor Pavlov.

You can download LZMA SDK from: http://www.7-zip.org/sdk.html

---

## Using 7-Zip in Your Projects

### Compiled Binaries

Compiled files from this source code can be used under GNU LGPL rules:
- Link to LGPL-licensed programs
- Distribute under LGPL terms
- Commercial use is permitted under LGPL

### Source Code

When using 7-Zip source code:
- Follow the GNU LGPL v2.1+ requirements
- Respect the unRAR restriction (if using RAR code)
- Include appropriate license notices
- Make source code available if required by LGPL

### License Compatibility

7-Zip's GNU LGPL license is compatible with:
- GPL-licensed software
- Commercial proprietary software (when used as a library)
- Most open-source licenses

---

## Additional Resources

- **Full LGPL Text**: [DOC/copying.txt](DOC/copying.txt)
- **Original License File**: [DOC/License.txt](DOC/License.txt)
- **unRAR License**: [DOC/unRarLicense.txt](DOC/unRarLicense.txt)
- **GNU LGPL Official**: http://www.gnu.org/licenses/lgpl-2.1.html

---

## Questions?

For licensing questions:
- Visit the official website: http://www.7-zip.org
- Check the forums: http://sourceforge.net/projects/sevenzip/forums
- Review the full license texts in the [DOC/](DOC/) directory
