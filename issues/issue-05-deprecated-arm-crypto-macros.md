## Update deprecated ARM crypto feature detection macros

**Priority**: Medium (Future Compatibility)  
**Category**: Deprecated Macros  
**Affected Files**: `C/Sha1Opt.c`, `C/AesOpt.c`

### Description

The code uses deprecated `__ARM_FEATURE_CRYPTO` macro for ARM cryptography feature detection. This macro has been deprecated in favor of more fine-grained feature macros.

### Locations

1. **`C/Sha1Opt.c:210`**:
   ```c
   // __ARM_FEATURE_CRYPTO macro is deprecated in favor of the finer grained 
   // feature macro __ARM_FEATURE_SHA2
   ```

2. **`C/AesOpt.c:664`**:
   ```c
   // __ARM_FEATURE_CRYPTO macro is deprecated in favor of the finer grained 
   // feature macro __ARM_FEATURE_AES
   ```

### Background

The `__ARM_FEATURE_CRYPTO` macro was originally used to detect ARM Cryptography Extension support. However, this extension includes multiple features:
- AES encryption/decryption
- SHA-1 hashing
- SHA-256 hashing
- Polynomial multiply (for GHASH/GCM)

Not all ARM processors support all crypto features, so ARM deprecated the generic macro in favor of specific ones:
- `__ARM_FEATURE_AES` - AES instructions
- `__ARM_FEATURE_SHA2` - SHA-1 and SHA-256 instructions
- `__ARM_FEATURE_SHA3` - SHA-3 and SHA-512 instructions (ARMv8.2+)
- `__ARM_FEATURE_SHA512` - SHA-512 instructions (ARMv8.2+)
- `__ARM_FEATURE_CRYPTO` - All crypto features (deprecated)

### Current Impact

While the deprecated macro still works, it may:
- Cause compiler warnings on newer ARM compilers
- Be removed in future compiler versions
- Fail to detect partial crypto support correctly

### Recommended Solution

#### For SHA-1 code (`C/Sha1Opt.c`):

```c
// Before:
#if defined(__ARM_FEATURE_CRYPTO)
  // SHA-1 hardware acceleration code
#endif

// After:
#if defined(__ARM_FEATURE_SHA2) || defined(__ARM_FEATURE_CRYPTO)
  // SHA-1 hardware acceleration code
  // Note: SHA-1 is part of SHA2 crypto extension
#endif
```

#### For AES code (`C/AesOpt.c`):

```c
// Before:
#if defined(__ARM_FEATURE_CRYPTO)
  // AES hardware acceleration code
#endif

// After:
#if defined(__ARM_FEATURE_AES) || defined(__ARM_FEATURE_CRYPTO)
  // AES hardware acceleration code
#endif
```

### Backward Compatibility

Keep the old macro as fallback to support older compilers:
```c
#if defined(__ARM_FEATURE_SHA2) || \
    (defined(__ARM_FEATURE_CRYPTO) && !defined(__ARM_FEATURE_SHA2))
```

This ensures:
- New compilers: Use the specific feature macro
- Old compilers: Fall back to the deprecated generic macro
- Smooth transition period

### Additional Considerations

1. **Check for SHA-512 support separately** (ARMv8.2+):
   ```c
   #if defined(__ARM_FEATURE_SHA512) || defined(__ARM_FEATURE_SHA3)
     // Can use SHA-512 hardware acceleration
   #endif
   ```

2. **Runtime detection**: Consider adding runtime CPU feature detection as fallback:
   ```c
   #include <sys/auxv.h>
   #include <asm/hwcap.h>
   
   unsigned long hwcaps = getauxval(AT_HWCAP);
   if (hwcaps & HWCAP_AES) {
       // AES is supported
   }
   if (hwcaps & HWCAP_SHA2) {
       // SHA-256 is supported
   }
   ```

3. **Update build flags**: Ensure compiler flags match:
   - `-march=armv8-a+crypto` (old, enables all crypto)
   - `-march=armv8-a+aes+sha2` (new, specific features)

### Testing

Test on ARM platforms with varying crypto support:
- ARMv8.0 with full crypto extension
- ARMv8.0 without crypto extension
- ARMv8.2+ with SHA-512 support
- Compile with both old and new compilers

### References

- [ARM C Language Extensions (ACLE)](https://github.com/ARM-software/acle/blob/main/main/acle.md)
- ARM Compiler Documentation on Crypto Extensions
- GCC ARM Options: `-march` flags
