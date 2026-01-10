# 7-Zip API Documentation

This guide explains how to use 7-Zip libraries in your own applications.

## Table of Contents

- [Overview](#overview)
- [Using 7-Zip DLLs](#using-7-zip-dlls)
- [Using 7-Zip as a Library](#using-7-zip-as-a-library)
- [LZMA SDK](#lzma-sdk)
- [7z ANSI-C Decoder](#7z-ansi-c-decoder)
- [C++ API](#c-api)
- [Examples](#examples)

## Overview

7-Zip provides several ways to integrate compression/decompression into your applications:

1. **DLL Files** - Use pre-built DLLs (Windows)
2. **Static Linking** - Compile 7-Zip code into your application
3. **LZMA SDK** - Standalone compression library
4. **7z ANSI-C Decoder** - C-based decompression

## Using 7-Zip DLLs

### Available DLLs (Windows)

| DLL | Formats | Description |
|-----|---------|-------------|
| **7z.dll** | All | Full format support |
| **7za.dll** | 7z | 7z format only |
| **7zr.dll** | 7z | 7z format (reduced) |
| **7zxa.dll** | 7z | 7z extraction only |

### DLL Interface

7-Zip uses COM-like interfaces but **not standard COM**. Objects are created via custom factory functions.

#### Key Interfaces

```cpp
// Archive handling
IInArchive    // Reading archives
IOutArchive   // Creating/updating archives

// Stream operations
IInStream     // Input stream
IOutStream    // Output stream
ISequentialInStream
ISequentialOutStream

// Compression
ICompressCoder     // Compression/decompression
ICompressProgressInfo  // Progress callbacks
```

### Example: Extracting with DLL

See `CPP/7zip/UI/Client7z/` for a complete example of using 7za.dll.

Basic steps:

1. Load the DLL
2. Get the `CreateObject` function
3. Create archive handler object
4. Open archive
5. Extract files
6. Release objects

```cpp
// Simplified example (see Client7z for full code)
typedef UINT32 (WINAPI *CreateObjectFunc)(
    const GUID *clsID,
    const GUID *interfaceID,
    void **outObject);

HMODULE library = LoadLibrary(TEXT("7z.dll"));
CreateObjectFunc createObject = (CreateObjectFunc)
    GetProcAddress(library, "CreateObject");

IInArchive *archive;
createObject(&CLSID_CFormat7z, &IID_IInArchive, (void **)&archive);

// Use archive...
archive->Release();
FreeLibrary(library);
```

## Using 7-Zip as a Library

### Standalone Bundles

Create standalone DLL versions by including all necessary code in your project.

Example bundles in source:
- `CPP/7zip/Bundles/Format7z` - Standalone 7z.dll
- `CPP/7zip/Bundles/Format7zExtract` - Extract-only version

### Building Standalone Library

1. Choose a bundle (e.g., `Format7z`)
2. Add all source files to your project
3. Define necessary macros
4. Compile as DLL or static library

Required definitions:
```cpp
#define EXTRACT_ONLY      // For extract-only builds
#define NO_READ_FROM_CODER // For minimal builds
```

## LZMA SDK

LZMA SDK is a **public domain** library for LZMA compression/decompression.

### Download

Get the latest LZMA SDK from: http://www.7-zip.org/sdk.html

### LZMA SDK Components

```
LZMA SDK/
├── C/           C implementation
│   ├── LzmaDec.c    LZMA decoder
│   ├── LzmaEnc.c    LZMA encoder
│   ├── Lzma2Dec.c   LZMA2 decoder
│   ├── Lzma2Enc.c   LZMA2 encoder
│   └── 7z*          7z format support
├── CPP/         C++ implementation
└── DOC/         Documentation
```

### Using LZMA Compression

#### Simple LZMA Compression (C)

```c
#include "LzmaEnc.h"

// Setup
CLzmaEncProps props;
LzmaEncProps_Init(&props);
props.level = 5;  // 0-9, 5 is default

// Allocate
CLzmaEncHandle enc = LzmaEnc_Create(&allocator);
LzmaEnc_SetProps(enc, &props);

// Encode
SizeT propsSize = LZMA_PROPS_SIZE;
SizeT destLen = /* calculate */;
UInt8 propsEncoded[LZMA_PROPS_SIZE];

SRes res = LzmaEnc_WriteProperties(enc, propsEncoded, &propsSize);

res = LzmaEnc_Encode(enc, 
    destBuffer, &destLen,
    srcBuffer, srcSize,
    progressCallback, &allocator, &allocator);

// Cleanup
LzmaEnc_Destroy(enc, &allocator, &allocator);
```

#### Simple LZMA Decompression (C)

```c
#include "LzmaDec.h"

// Setup
CLzmaDec dec;
LzmaDec_Construct(&dec);

SRes res = LzmaDec_Allocate(&dec, 
    propsEncoded, LZMA_PROPS_SIZE, &allocator);

// Decode
LzmaDec_Init(&dec);

SizeT destLen = /* output size */;
SizeT srcLen = /* input size */;
ELzmaStatus status;

res = LzmaDec_DecodeToBuf(&dec,
    destBuffer, &destLen,
    srcBuffer, &srcLen,
    LZMA_FINISH_END, &status);

// Cleanup
LzmaDec_Free(&dec, &allocator);
```

### LZMA Utility Functions

```c
// All-in-one compression
SRes LzmaCompress(
    unsigned char *dest, size_t *destLen,
    const unsigned char *src, size_t srcLen,
    unsigned char *outProps, size_t *outPropsSize,
    int level,  /* 0-9 */
    unsigned dictSize,  /* use 0 for default */
    int lc,  /* 0-8, default 3 */
    int lp,  /* 0-4, default 0 */
    int pb,  /* 0-4, default 2 */
    int fb,  /* 5-273, default 32 */
    int numThreads  /* 1 or 2, default 2 */
);

// All-in-one decompression
SRes LzmaUncompress(
    unsigned char *dest, size_t *destLen,
    const unsigned char *src, size_t *srcLen,
    const unsigned char *props, size_t propsSize
);
```

## 7z ANSI-C Decoder

Pure C implementation for 7z format decompression.

Location: `C/` directory (files starting with `7z`)

See [DOC/7zC.txt](../DOC/7zC.txt) for detailed documentation.

### Features

- Pure C code (C89 compatible)
- Supports LZMA, LZMA2, and copy methods
- Supports BCJ and BCJ2 filters
- Minimal dependencies
- Low memory usage

### Basic Usage

```c
#include "7z.h"
#include "7zAlloc.h"
#include "7zCrc.h"

// Initialize
CrcGenerateTable();

ISzAlloc allocImp = { SzAlloc, SzFree };
ISzAlloc allocTempImp = { SzAllocTemp, SzFreeTemp };

CLookToRead2 lookStream;
CSzArEx db;
SzArEx_Init(&db);

// Open archive
SRes res = SzArEx_Open(&db, &lookStream.vt, &allocImp, &allocTempImp);

// Extract file
UInt32 blockIndex = UINT32_MAX;
Byte *outBuffer = NULL;
size_t outBufferSize = 0;

for (UInt32 i = 0; i < db.NumFiles; i++) {
    size_t offset = 0;
    size_t outSizeProcessed = 0;
    
    res = SzArEx_Extract(&db, &lookStream.vt, i,
        &blockIndex, &outBuffer, &outBufferSize,
        &offset, &outSizeProcessed,
        &allocImp, &allocTempImp);
    
    // Use: outBuffer + offset, size: outSizeProcessed
}

// Cleanup
ISzAlloc_Free(&allocImp, outBuffer);
SzArEx_Free(&db, &allocImp);
```

### Memory Allocation

7z decoder uses two allocators:

1. **Main pool** - For database and decompressed blocks
2. **Temporary pool** - For headers and working buffers

Implement `ISzAlloc`:

```c
typedef struct {
    void *(*Alloc)(ISzAllocPtr p, size_t size);
    void (*Free)(ISzAllocPtr p, void *address);
} ISzAlloc;
```

## C++ API

### Stream Interfaces

```cpp
// Sequential input
STDMETHOD(Read)(void *data, UInt32 size, UInt32 *processedSize) = 0;

// Sequential output
STDMETHOD(Write)(const void *data, UInt32 size, UInt32 *processedSize) = 0;

// Seekable input
STDMETHOD(Seek)(Int64 offset, UInt32 seekOrigin, UInt64 *newPosition) = 0;
```

### Archive Interfaces

```cpp
// Opening archive
IInArchive::Open(IInStream *stream, 
                 const UInt64 *maxCheckStartPosition,
                 IArchiveOpenCallback *openCallback);

// Getting item count
IInArchive::GetNumberOfItems(UInt32 *numItems);

// Getting properties
IInArchive::GetProperty(UInt32 index, PROPID propID, PROPVARIANT *value);

// Extracting
IInArchive::Extract(const UInt32* indices,
                    UInt32 numItems,
                    Int32 testMode,
                    IArchiveExtractCallback *extractCallback);
```

### Compression Interfaces

```cpp
// Basic coder
ICompressCoder::Code(
    ISequentialInStream *inStream,
    ISequentialOutStream *outStream,
    const UInt64 *inSize,
    const UInt64 *outSize,
    ICompressProgressInfo *progress);

// Coder with properties
ICompressSetCoderProperties::SetCoderProperties(
    const PROPID *propIDs,
    const PROPVARIANT *properties,
    UInt32 numProperties);
```

## Examples

### Complete Examples in Source

| Example | Location | Description |
|---------|----------|-------------|
| **Client7z** | `CPP/7zip/UI/Client7z/` | Using 7za.dll |
| **7z decoder** | `C/Util/7z/` | ANSI-C 7z extraction |
| **LZMA utility** | `C/Util/Lzma/` | LZMA compression tool |
| **LzmaLib** | `C/Util/LzmaLib/` | LZMA library usage |

### Quick Start Examples

#### Compress with LZMA (Simple)

```c
#include "LzmaLib.h"

unsigned char *src = /* your data */;
size_t srcLen = /* data length */;
unsigned char *dest = malloc(srcLen + srcLen / 3 + 128);
size_t destLen = srcLen + srcLen / 3 + 128;

unsigned char outProps[LZMA_PROPS_SIZE];
size_t outPropsSize = LZMA_PROPS_SIZE;

int res = LzmaCompress(
    dest, &destLen,
    src, srcLen,
    outProps, &outPropsSize,
    5,  // level
    0,  // default dict size
    -1, -1, -1, -1, -1  // default params
);
```

#### Decompress with LZMA (Simple)

```c
#include "LzmaLib.h"

unsigned char *src = /* compressed data */;
size_t srcLen = /* compressed length */;
unsigned char *dest = malloc(originalSize);
size_t destLen = originalSize;

int res = LzmaUncompress(
    dest, &destLen,
    src, &srcLen,
    props, LZMA_PROPS_SIZE
);
```

## Threading

LZMA2 encoder supports multi-threading:

```c
CLzma2EncProps props;
Lzma2EncProps_Init(&props);
props.lzmaProps.level = 5;
props.numTotalThreads = 2;  // Number of threads

CLzma2EncHandle enc = Lzma2Enc_Create(&allocator, &allocator);
Lzma2Enc_SetProps(enc, &props);
```

## Error Handling

Most functions return `SRes` (result code):

```c
#define SZ_OK 0
#define SZ_ERROR_DATA 1
#define SZ_ERROR_MEM 2
#define SZ_ERROR_CRC 3
#define SZ_ERROR_UNSUPPORTED 4
#define SZ_ERROR_PARAM 5
#define SZ_ERROR_INPUT_EOF 6
#define SZ_ERROR_OUTPUT_EOF 7
#define SZ_ERROR_READ 8
#define SZ_ERROR_WRITE 9
#define SZ_ERROR_PROGRESS 10
#define SZ_ERROR_FAIL 11
#define SZ_ERROR_THREAD 12
#define SZ_ERROR_ARCHIVE 16
#define SZ_ERROR_NO_ARCHIVE 17
```

## Best Practices

1. **Always check return values** - Don't ignore `SRes` codes
2. **Free resources** - Use proper cleanup even on errors
3. **Progress callbacks** - Provide progress info for long operations
4. **Thread safety** - Most 7-Zip objects are not thread-safe
5. **Memory allocation** - Use custom allocators for large data
6. **Buffer sizes** - Allocate sufficient output buffers

## Additional Resources

- **7z Format**: [DOC/7zFormat.txt](../DOC/7zFormat.txt)
- **7z C Decoder**: [DOC/7zC.txt](../DOC/7zC.txt)
- **LZMA**: [DOC/lzma.txt](../DOC/lzma.txt)
- **Methods**: [DOC/Methods.txt](../DOC/Methods.txt)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)

## License

When using 7-Zip code:

- **LZMA SDK**: Public domain - no restrictions
- **7-Zip Library**: GNU LGPL - see [LICENSE.md](../LICENSE.md)
- **RAR code**: Additional restrictions - see [LICENSE.md](../LICENSE.md)

## Support

For API questions:
- Study the example code in `CPP/7zip/UI/Client7z/`
- Check the LZMA SDK documentation
- Visit the forums: http://sourceforge.net/projects/sevenzip/forums
