# Compiler Requirements and Workarounds

This document describes the compiler versions supported by 7-Zip and documents the compiler-specific workarounds present in the codebase.

## Minimum Compiler Versions

### Recommended (Fully Tested)

| Compiler | Minimum Version | Platform | Notes |
|----------|----------------|----------|-------|
| **MSVC** | Visual Studio 2017 (14.1, _MSC_VER 1910) | Windows x86/x64/ARM64 | Recommended: VS2019 or VS2022 |
| **GCC** | GCC 13.4 | Linux/macOS x86/x64/ARM64 | Lowest version maintained by GCC team |
| **Clang** | Clang 10.0 | Linux/macOS x86/x64/ARM64 | Modern versions recommended |

**Note**: All workarounds for GCC versions below 13.4 have been removed. The codebase now requires GCC 13.4 or newer, which is the lowest version still maintained by the GCC development team.

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

**Status**: **REMOVED** (as of GCC 13.4 minimum requirement)

**File**: Previously in `C/CpuArch.c`

**Problem** (Historical):
Older GCC and Clang compilers had issues with `rbx`/`ebx` register handling in inline assembly blocks when Position Independent Code (PIC) mode is enabled. The `rbx` register is used as the PIC base pointer in x86-64 and must be preserved.

**Resolution**:
With the minimum GCC version requirement raised to 13.4, this workaround has been completely removed. GCC 13.4 and modern Clang versions handle cpuid correctly without special handling. The codebase now uses standard cpuid inline assembly without register preservation workarounds.

**Code Before** (removed):
```c
// Complex workaround with rbx/ebx preservation for old GCC < 5
#if defined(MY_CPU_AMD64) && defined(__PIC__) && (__GNUC__ < 5)
  __asm__ __volatile__ (
    "mov     %%rbx, %q1"  // Save rbx
    "cpuid"               
    "xchg    %%rbx, %q1"  // Restore rbx
    ...
  );
#endif
```

**Code Now**:
```c
// Standard cpuid - works with GCC 13.4+ and modern Clang
#define x86_cpuid_MACRO_2(p, func, subFunc) { \
  __asm__ __volatile__ ( \
    "cpuid" \
    : "=a" ((p)[0]), "=b" ((p)[1]), "=c" ((p)[2]), "=d" ((p)[3]) \
    : "0" (func), "2"(subFunc)); }
```

**Version Check Added**:
The codebase now enforces GCC 13.4+ at compile time:
```c
#if defined(__GNUC__) && !defined(__clang__)
  #if __GNUC__ < 13 || (__GNUC__ == 13 && __GNUC_MINOR__ < 4)
    #error "GCC 13.4 or newer is required. Please upgrade your compiler."
  #endif
#endif
```

---

## Testing Matrix

The following compilers are regularly tested:

| Compiler | Version | Platform | Status | CI |
|----------|---------|----------|--------|-----|
| MSVC | 2022 (14.3) | Windows x64 | ✅ Supported | Yes |
| MSVC | 2019 (14.2) | Windows x64 | ✅ Supported | Yes |
| MSVC | 2017 (14.1) | Windows x64 | ✅ Supported | No |
| GCC | 13.4+ | Linux x64 | ✅ Minimum Required | Yes |
| GCC | 14.x | Linux x64 | ✅ Supported | Yes |
| Clang | 15.x | Linux x64 | ✅ Supported | Yes |
| Clang | 10.x | macOS ARM64 | ⚠️ Minimum | No |
| AppleClang | Latest | macOS ARM64 | ✅ Supported | No |

**Legend**:
- ✅ Supported: Regularly tested and fully supported
- ⚠️ Minimum: Minimum version, should work but not regularly tested
- ❌ Not Supported: Known to not work or not tested

**Important**: GCC versions below 13.4 are **not supported** and will fail to compile with an error message.

---

## Recommendations for Maintainers

### Completed Actions

1. ✅ **Removed GCC < 13.4 workarounds**: All workarounds for old GCC versions removed
2. ✅ **Added compiler version checks**: GCC 13.4+ enforced at compile time
3. ✅ **Updated BUILDING.md**: Explicit minimum versions documented
4. ✅ **Updated testing matrix**: Reflects new GCC 13.4 minimum

### Short Term (Current Release Cycle)

1. **Monitor GCC 13.4 compatibility**: Ensure builds work correctly with minimum version
2. **Update CI pipelines**: Test with GCC 13.4 as the minimum version
3. **Document breaking change**: Clearly communicate GCC version requirement in release notes

### Medium Term (Next Major Release)

1. **Consider Clang minimum version bump**: Evaluate raising Clang minimum to 15.0+
2. **Review MSVC workarounds**: Evaluate if MSVC workarounds can be removed or simplified
3. **Consider using compiler intrinsics**: Evaluate using `<cpuid.h>` for further simplification

### Long Term (Future Releases)

1. **Regularly review compiler requirements** (every 1-2 years):
   - Track actively maintained compiler versions
   - Remove workarounds for obsolete compilers
   - Update testing matrix

2. **Track compiler market share**:
   - Monitor usage of compiler versions
   - Make data-driven decisions about minimum versions

---

## Related Documentation

- [BUILDING.md](BUILDING.md) - Build instructions and prerequisites
- [C/CpuArch.c](C/CpuArch.c) - CPU detection and cpuid implementation
- [C/LzFindMt.c](C/LzFindMt.c) - Match finder with movsx workaround
- [C/LzFindOpt.c](C/LzFindOpt.c) - Optimized match finder with movsx workaround

---

## Reporting Compiler Issues

If you encounter build issues with a specific compiler:

1. Check this document for minimum requirements
2. Verify your compiler version meets minimum requirements (GCC 13.4+, Clang 10.0+, MSVC 2017+)
3. Check [BUILDING.md](BUILDING.md) for build instructions
4. For GCC < 13.4: You will receive a compile-time error. Please upgrade to GCC 13.4 or newer.
5. Report issues on GitHub with:
   - Compiler name and exact version
   - Platform and architecture
   - Complete build log
   - Steps to reproduce

---

**Document Version**: 2.0  
**Last Updated**: 2026-01-12  
**Maintainer**: 7-Zip Development Team
