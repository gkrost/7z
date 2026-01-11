## Clean up commented-out debug code and defines

**Priority**: Low (Code Cleanliness)  
**Category**: Dead Code / Debug Code  
**Affected Files**: Multiple C files

### Description

The codebase contains extensive commented-out `#define` statements for debug code, alternative implementations, and testing. This clutters the source files and makes them harder to read.

### Categories of Commented Code

#### 1. Debug Defines (Currently Commented Out)

**SHA-2/SHA-512 Debug**:
- `C/Sha512.c:442` - `// #define Z7_SHA512_PROBE_DEBUG // for debug`
- `C/Sha512.c:495` - `// #define Z7_SHA512_USE_SIMPLIFIED_PROBE // for debug`
- `C/Sha512.c:97` - `// #define Z7_SHA512_UNROLL`
- `C/Sha256Opt.c:8` - `// #define Z7_USE_HW_SHA_STUB // for debug`
- `C/Sha256Opt.c:31` - `// #define Z7_USE_HW_SHA_STUB // for debug`
- `C/Sha256Opt.c:150` - `// #define msg tmp`
- `C/Sha512Opt.c:8, 26, 31` - `// #define Z7_USE_HW_SHA_STUB // for debug`
- `C/Sha512Opt.c:150` - `// #define msg tmp`

**CRC64 Debug**:
- `C/XzCrc64Opt.c:12` - `// #define Z7_CRC64_DEBUG_BE`

**LZMA Debug**:
- `C/LzFindMt.c:13` - `// #define LOG_ITERS`
- `C/LzFindMt.c:15` - `// #define LOG_THREAD`
- `C/LzFindMt.c:99` - `// #define DEBUG_BUFFER_LOCK   // define it to debug lock state`

**PPMd Debug**:
- `C/Ppmd8Enc.c:49-50` - Commented macro alternatives:
  ```c
  // #define RC_PRE(total) p->Range /= total;
  // #define RC_PRE(total)
  ```

#### 2. Alternative Implementation Macros (Commented Out)

- `C/LzFindMt.c:56-57` - Commented convenience macros:
  ```c
  // #define MF(mt) (&(mt)->MatchFinder)
  // #define MF_CRC (p->MatchFinder.crc)
  ```
- `C/LzFindMt.c:223` - `// #define RINOK_THREAD(x) { if ((x) != 0) return SZ_ERROR_THREAD; }`
- `C/LzFindMt.c:295-296`:
  ```c
  // #define kMtMaxValForNormalize ((1 << 21)) // for debug
  // #define kNormalizeAlign (1 << 7) // alignment for speculated accesses
  ```

#### 3. Unused Code (Commented Out)

**CPU Vendor Detection** (`C/CpuArch.c:315-358`):
```c
/*
static const UInt32 kVendors[][1] =
{
  { 0x756E6547 }, // , 0x49656E69, 0x6C65746E },
  { 0x68747541 }, // , 0x69746E65, 0x444D4163 },
  { 0x746E6543 }  // , 0x48727561, 0x736C7561 }
};
*/

/*
typedef struct
{
  UInt32 maxFunc;
  UInt32 vendor[3];
  UInt32 ver;
  UInt32 b;
  UInt32 c;
  UInt32 d;
} Cx86cpuid;
...
int x86cpuid_GetFirm(const Cx86cpuid *p)
{
  ...
}
*/
```

#### 4. Disabled Debug Logging

- `C/CpuArch.c:6` - `// #include <stdio.h>`
- Multiple `// printf(...)` statements throughout files

### Issues

1. **Code Clutter**: Makes files harder to read and navigate
2. **Confusion**: Unclear if code should be enabled or is obsolete
3. **Maintenance**: Commented code may become outdated
4. **Merge Conflicts**: More lines = more potential conflicts
5. **Lost Context**: Purpose of commented code often unclear

### Recommended Actions

#### Phase 1: Quick Cleanup

**Remove clearly obsolete commented code:**
- Old vendor detection structs and functions that are no longer used
- Commented-out alternative macro definitions that were experiments
- Old printf debug statements

**Example:**
```c
// REMOVE:
// #include <stdio.h>

// REMOVE entire block:
/*
static const UInt32 kVendors[][1] = { ... };
int x86cpuid_GetFirm(const Cx86cpuid *p) { ... }
*/
```

#### Phase 2: Convert Useful Debug Code

**For actually useful debug defines, create a debug header:**

Create `C/Debug.h`:
```c
#ifndef DEBUG_H
#define DEBUG_H

/* Debug options - enable as needed for debugging */

/* Uncomment to enable SHA-512 probe debugging */
/* #define Z7_SHA512_PROBE_DEBUG */

/* Uncomment to enable LZMA buffer lock debugging */
/* #define DEBUG_BUFFER_LOCK */

/* Uncomment to enable LZMA iteration logging */
/* #define LOG_ITERS */

/* Uncomment to enable thread logging */
/* #define LOG_THREAD */

/* Uncomment to enable CRC64 big-endian testing */
/* #define Z7_CRC64_DEBUG_BE */

#endif /* DEBUG_H */
```

Then in source files:
```c
#include "Precomp.h"
#include "Debug.h"  // Centralized debug options

#ifdef Z7_SHA512_PROBE_DEBUG
  // debug code here
#endif
```

#### Phase 3: Document Remaining Comments

For any commented code that must be kept, add explanation:
```c
// The following code is preserved for reference but not currently used.
// It may be needed for future CPU vendor-specific optimizations.
// See issue #XXX for discussion.
/*
static const UInt32 kVendors[][1] = { ... };
*/
```

### Benefits of Cleanup

1. **Reduced file size**: Less scrolling, easier navigation
2. **Clear intent**: Debug options clearly documented
3. **Easier maintenance**: Debug features in one place
4. **Better version control**: Less noise in diffs
5. **Centralized control**: Enable/disable debug features globally

### Implementation Strategy

```bash
# 1. Create centralized debug header
cat > C/Debug.h << 'EOF'
#ifndef DEBUG_H
#define DEBUG_H
// Debug options - see Debug.h for available flags
#endif
EOF

# 2. Remove clearly dead code
# Review each file and remove obsolete comments

# 3. Convert useful debug defines
# Move to Debug.h and reference from source files

# 4. Document any remaining commented code
```

### Files to Review

High priority (lots of commented debug code):
1. `C/Sha512.c`
2. `C/Sha256Opt.c`
3. `C/Sha512Opt.c`
4. `C/LzFindMt.c`
5. `C/CpuArch.c`
6. `C/XzCrc64Opt.c`
7. `C/Ppmd8Enc.c`

### Testing

After cleanup:
1. Verify code compiles without changes to behavior
2. Test with debug defines enabled (using new Debug.h)
3. Run full test suite
4. Check that file sizes are reduced
5. Verify git diffs are cleaner

### Related Issues

- See also: Issue #2 (Dead Code: #if 0 blocks)
- Consider combining cleanup efforts
