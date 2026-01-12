# Compiler Requirements and Workarounds

This document describes the compiler versions supported by 7-Zip and documents the compiler-specific workarounds present in the codebase.

## Minimum Compiler Versions

### Recommended (Fully Tested)

| Compiler | Minimum Version | Platform | Notes |
|----------|----------------|----------|-------|
| **MSVC** | Visual Studio 2017 (14.1, _MSC_VER 1910) | Windows x86/x64/ARM64 | Recommended: VS2019 or VS2022 |
| **GCC** | GCC 7.0 | Linux/macOS x86/x64/ARM64 | GCC 5+ should work with workarounds |
| **Clang** | Clang 5.0 | Linux/macOS x86/x64/ARM64 | Clang 3.8+ may work with workarounds |

### Absolute Minimum (With Workarounds)

The codebase contains workarounds that allow building with older compilers, though this is not recommended for production use:

| Compiler | Minimum Version | Limitations |
|----------|----------------|-------------|
| **MSVC** | Visual Studio 2010 (_MSC_VER 1600) | x64 only; __cpuidex available |
| **MSVC** | Visual Studio 2005 (_MSC_VER 1400) | x86/x64; requires cpuid workarounds |
| **GCC** | GCC 4.x | Requires PIC mode rbx/ebx workarounds |
| **Clang** | Clang 3.x | May require PIC mode workarounds |

**Warning**: Compilers older than the recommended versions are not regularly tested and may have bugs or limitations. Use at your own risk.

## Compiler-Specific Workarounds

The following sections document the workarounds present in the codebase for known compiler bugs and quirks.

### Workaround 1: MSVC x64 movsx Bug

**Files**: 
- `C/LzFindMt.c:565-591`
- `C/LzFindOpt.c:215-241`

**Problem**:
Old MSVC x64 compilers incorrectly generated a `movsx` (sign-extend move) instruction when converting `UInt32` to `size_t`, instead of using `mov` or `movzx` (zero-extend). This caused incorrect behavior when the high bit of the UInt32 value was set.

**Workaround**:
Use `size_t` directly for function parameters (e.g., `pos`, `_cyclicBufferPos`) instead of `UInt32` to avoid the type conversion that triggers the bug.

```c
// Instead of: UInt32 pos
// We use:     size_t pos
UInt32 * Z7_FASTCALL GetMatchesSpecN_2(const Byte *lenLimit, size_t pos, ...)
```

**Affected Versions**:
- MSVC versions before Visual Studio 2015 (_MSC_VER < 1900)
- Exact version range not documented, but known to affect VS2005-VS2013

**Current Status**:
- **Active**: Workaround is unconditionally applied
- **Impact**: Minimal; using `size_t` is safe and doesn't harm newer compilers
- **Testing**: Not regularly tested with affected old compilers

**Removal Plan**:
This workaround could be made conditional or removed entirely if:
1. Minimum MSVC version is bumped to VS2015+ (_MSC_VER >= 1900), OR
2. The workaround is determined to have no negative effects (current assessment)

**Recommendation**: Keep as-is unless minimum compiler version policy changes.

---

### Workaround 2: MSVC __cpuid ECX Register Bug

**File**: `C/CpuArch.c:247-277`

**Problem**:
The `cpuid` instruction supports a subfunction parameter in ECX for certain function values (e.g., `func=7` for extended features). MSDN documentation states that `__cpuid()` should clear ECX before calling the cpuid instruction.

- **New MSVC (2010+)**: Provides `__cpuidex()` which properly handles subfunctions
- **Old MSVC (VS2005, _MSC_VER 1400)**: The `__cpuid()` intrinsic doesn't clear ECX in x64 builds

This causes `__cpuid()` to fail for function values that require specific ECX values (subfunctions).

**Workaround**:
Use a hack that exploits the `Z7_FASTCALL` calling convention (which passes the first parameter in ECX) combined with `Z7_NO_INLINE` to ensure the subfunction value reaches the cpuid instruction through ECX without being cleared.

```c
static Z7_NO_INLINE void Z7_FASTCALL MY_cpuidex_HACK(Int32 subFunction, Int32 func, Int32 *CPUInfo)
{
  UNUSED_VAR(subFunction)  // subFunction is in ECX due to FASTCALL
  __cpuid(CPUInfo, func);   // Old MSVC doesn't clear ECX, so cpuid gets subFunction
}
```

**Affected Versions**:
- Visual Studio 2005 (MSVC 8.0, _MSC_VER 1400)
- Visual Studio 2008 (MSVC 9.0, _MSC_VER 1500)
- **Fixed in**: Visual Studio 2010 (MSVC 10.0, _MSC_VER 1600) with `__cpuidex()`

**Current Status**:
- **Active**: Only for _MSC_VER < 1600 (VS2010)
- **Impact**: This code path should never execute in supported builds (minimum is VS2017)
- **Build Warning**: Pragma messages warn when this workaround is active
- **Testing**: Not tested with affected compilers

**Removal Plan**:
Consider one of the following approaches:

1. **Option A**: Add `#error` directive for unsupported compilers
   ```c
   #if defined(_MSC_VER) && _MSC_VER < 1600
     #error "Visual Studio 2010 or newer required for proper __cpuidex support"
   #endif
   ```

2. **Option B**: Keep workaround but improve documentation (current approach)

3. **Option C**: Remove workaround when minimum MSVC version policy is formalized

**Recommendation**: Keep workaround with improved documentation until minimum compiler policy is formalized.

---

### Workaround 3: GCC/Clang PIC Mode rbx/ebx Preservation

**File**: `C/CpuArch.c:28-80`

**Problem**:
Some older GCC and Clang compilers had issues with `rbx`/`ebx` register handling in inline assembly blocks when Position Independent Code (PIC) mode is enabled (`-fPIC`, `__PIC__` defined). The `rbx` register is used as the PIC base pointer in x86-64 and must be preserved.

**Timeline**:
- **GCC**:
  - 2007: Preserved `ebx` for `(__PIC__ && __i386__)`
  - 2013: Preserved `rbx` and `ebx` for `__PIC__`
  - 2014: Stopped preserving rbx/ebx
  - **GCC 5.0+ (2015)**: Assumed to have fixed the PIC ebx/rbx issue

- **Clang**:
  - 2014+: Preserves `rbx` for 64-bit code only, no `__PIC__` check
  - Unclear why Clang only handles 64-bit and not 32-bit `ebx`

**Workaround**:
Use `mov/xchg` to save and restore `rbx`/`ebx` around the cpuid instruction in inline assembly:

```c
// For x86-64 with GCC < 5 or Clang in PIC mode:
__asm__ __volatile__ (
  "mov     %%rbx, %q1"  // Save rbx
  "cpuid"               
  "xchg    %%rbx, %q1"  // Restore rbx
  : "=a" (p[0]), "=&r" (p[1]), "=c" (p[2]), "=d" (p[3])
  : "0" (func), "2"(subFunc)
);
```

**Affected Versions**:
- **GCC < 5.0**: Definitely affected
- **GCC 5.0+**: Should be safe without workaround
- **Clang**: Unclear; workaround applied conservatively for all versions

**Current Status**:
- **Active**: For `(GCC < 5 || Clang) && __PIC__`
- **Impact**: Extra instructions in PIC builds on affected compilers
- **Testing**: Tested on modern GCC/Clang with workaround active

**Removal Plan**:
This workaround can likely be removed or simplified:

1. **Option A**: Use compiler's `<cpuid.h>` instead of inline assembly
   ```c
   #include <cpuid.h>
   // Use __cpuid() and __cpuid_count() from the compiler
   ```

2. **Option B**: Bump minimum GCC to 7.0+ and minimum Clang to 10.0+
   - Remove workaround entirely for supported versions
   - Add version check to fail on unsupported compilers

3. **Option C**: Keep for GCC < 5, remove for Clang (testing needed)

**Recommendation**: Consider Option A (use `<cpuid.h>`) for code simplification, or Option B if minimum compiler policy is formalized.

---

## Testing Matrix

The following compilers are regularly tested:

| Compiler | Version | Platform | Status | CI |
|----------|---------|----------|--------|-----|
| MSVC | 2022 (14.3) | Windows x64 | ✅ Supported | Yes |
| MSVC | 2019 (14.2) | Windows x64 | ✅ Supported | Yes |
| MSVC | 2017 (14.1) | Windows x64 | ✅ Supported | No |
| GCC | 11.x | Linux x64 | ✅ Supported | Yes |
| GCC | 9.x | Linux x64 | ✅ Supported | No |
| GCC | 7.x | Linux x64 | ⚠️ Minimum | No |
| Clang | 15.x | Linux x64 | ✅ Supported | Yes |
| Clang | 10.x | macOS ARM64 | ✅ Supported | No |
| AppleClang | Latest | macOS ARM64 | ✅ Supported | No |

**Legend**:
- ✅ Supported: Regularly tested and fully supported
- ⚠️ Minimum: Minimum version, should work but not regularly tested
- ❌ Not Supported: Known to not work or not tested

### Untested (Workarounds Present)

The following compilers have workarounds but are **not regularly tested**:

| Compiler | Version | Status | Notes |
|----------|---------|--------|-------|
| MSVC | 2005-2008 | ❌ Not Tested | __cpuid workaround present but untested |
| MSVC | 2010-2015 | ⚠️ Should Work | May have movsx issues |
| GCC | 4.x | ❌ Not Tested | PIC workaround present but untested |
| GCC | 5.x-6.x | ⚠️ Should Work | PIC workaround may be unnecessary |
| Clang | < 5.0 | ❌ Not Tested | Not recommended |

---

## Recommendations for Maintainers

### Short Term (Current Release Cycle)

1. **Keep all workarounds** with improved documentation (this document)
2. **Add pragma warnings** to alert users building with old compilers
3. **Update BUILDING.md** with explicit minimum versions (Done)
4. **Document testing matrix** (this document)

### Medium Term (Next Major Release)

1. **Formalize minimum compiler policy**:
   - Windows: MSVC 2017+ (_MSC_VER >= 1910)
   - Linux: GCC 7.0+ or Clang 5.0+

2. **Optionally remove workarounds** for compilers below minimum:
   - Consider `#error` directives for unsupported versions
   - Or keep workarounds for legacy builds (low cost)

3. **Consider using compiler intrinsics**:
   - Use `<cpuid.h>` from GCC/Clang instead of inline assembly
   - Simplifies code and improves portability

### Long Term (Future Releases)

1. **Regularly review workarounds** (every 1-2 years):
   - Check if affected compiler versions are still relevant
   - Remove workarounds for obsolete compilers
   - Update testing matrix

2. **Add CI testing** for minimum supported compilers:
   - Ensure workarounds still function correctly
   - Detect when workarounds can be safely removed

3. **Track compiler market share**:
   - Monitor usage of old compiler versions
   - Make data-driven decisions about minimum versions

---

## Related Documentation

- [BUILDING.md](BUILDING.md) - Build instructions and prerequisites
- [C/CpuArch.c](C/CpuArch.c) - CPU detection and cpuid workarounds
- [C/LzFindMt.c](C/LzFindMt.c) - Match finder with movsx workaround
- [C/LzFindOpt.c](C/LzFindOpt.c) - Optimized match finder with movsx workaround

---

## Reporting Compiler Issues

If you encounter build issues with a specific compiler:

1. Check this document for known workarounds
2. Verify your compiler version meets minimum requirements
3. Check [BUILDING.md](BUILDING.md) for build instructions
4. Report issues on GitHub with:
   - Compiler name and exact version
   - Platform and architecture
   - Complete build log
   - Steps to reproduce

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-12  
**Maintainer**: 7-Zip Development Team
