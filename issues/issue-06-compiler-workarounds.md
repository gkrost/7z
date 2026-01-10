## Document and review compiler-specific workarounds

**Priority**: Medium (Technical Debt)  
**Category**: Compiler Workarounds  
**Affected Files**: `C/CpuArch.c`, `C/LzFindMt.c`, `C/LzFindOpt.c`, `C/Threads.c`

### Description

The codebase contains several workarounds for known compiler bugs and quirks. These should be documented, reviewed, and potentially updated or removed as compilers are updated.

## Workaround 1: MSVC x64 movsx Bug

### Location
- `C/LzFindMt.c:566-568`
- `C/LzFindOpt.c:214` (similar workaround)

### Code
```c
/*
  we use size_t for (pos) instead of UInt32
  to eliminate "movsx" BUG in old MSVC x64 compiler.
*/
UInt32 * Z7_FASTCALL GetMatchesSpecN_2(const Byte *lenLimit, size_t pos, ...)
```

### Issue
Old MSVC x64 compiler incorrectly generated `movsx` (sign-extend) instruction instead of `mov` or `movzx` when converting UInt32 to size_t, causing incorrect behavior.

### Questions
- Which MSVC versions are affected?
- Is this still needed for currently supported compilers?
- Can we add version check to only apply workaround for old compilers?

### Recommendation
```c
#if defined(_MSC_VER) && _MSC_VER < 1900  // Before VS2015
  // Use size_t for (pos) to workaround movsx bug in old MSVC x64
  typedef size_t pos_type;
#else
  typedef UInt32 pos_type;
#endif

UInt32 * Z7_FASTCALL GetMatchesSpecN_2(const Byte *lenLimit, pos_type pos, ...)
```

---

## Workaround 2: MSVC __cpuid ECX Bug

### Location
`C/CpuArch.c:247-275`

### Code
```c
/*
 __cpuid (func == (0 or 7)) requires subfunction number in ECX.
  MSDN: The __cpuid intrinsic clears the ECX register before calling the cpuid instruction.
   __cpuid() in new MSVC clears ECX.
   __cpuid() in old MSVC (14.00) x64 doesn't clear ECX
 We still can use __cpuid for low (func) values that don't require ECX,
 but __cpuid() in old MSVC will be incorrect for some func values: (func == 7).
 So here we use the hack for old MSVC to send (subFunction) in ECX register to cpuid instruction,
 where ECX value is first parameter for FASTCALL / NO_INLINE func.
 So the caller of MY_cpuidex_HACK() sets ECX as subFunction, and
 old MSVC for __cpuid() doesn't change ECX and cpuid instruction gets (subFunction) value.
 
DON'T remove Z7_NO_INLINE and Z7_FASTCALL for MY_cpuidex_HACK(): !!!
*/
static
Z7_NO_INLINE void Z7_FASTCALL MY_cpuidex_HACK(Int32 subFunction, Int32 func, Int32 *CPUInfo)
{
  UNUSED_VAR(subFunction)
  __cpuid(CPUInfo, func);
}
```

With pragma message:
```c
#pragma message("======== MY_cpuidex_HACK WAS USED ========")
```

### Issues
- Affects old MSVC 14.00 (Visual Studio 2005)
- Relies on FASTCALL calling convention to pass subFunction in ECX
- Compiler-dependent and fragile
- Triggers warning message during build

### Questions
- Is MSVC 14.00 (VS2005) still a supported compiler?
- Can we drop support for such old compilers?
- If not, can we improve the implementation?

### Recommendation

**Option 1: Version-gated workaround**
```c
#if defined(_MSC_VER) && _MSC_VER < 1600  // Before VS2010
  static Z7_NO_INLINE void Z7_FASTCALL MY_cpuidex_HACK(...)
  #pragma message("Using CPUID workaround for MSVC < 2010")
#else
  // Use standard __cpuidex
#endif
```

**Option 2: Document minimum compiler version**
```c
// Minimum MSVC version: Visual Studio 2010 (_MSC_VER >= 1600)
// for proper __cpuidex support
#if defined(_MSC_VER) && _MSC_VER < 1600
  #error "MSVC 2010 or newer required"
#endif
```

**Option 3: Keep but improve documentation**
Add comment explaining:
- Which MSVC versions need this
- When it can be safely removed
- Link to MSVC bug report if available

---

## Workaround 3: GCC/CLANG PIC Mode rbx/ebx Preservation

### Location
`C/CpuArch.c:28-80`

### Code
```c
/* there was some CLANG/GCC compilers that have issues with
   rbx(ebx) handling in asm blocks in -fPIC mode (__PIC__ is defined).
   compiler's <cpuid.h> contains the macro __cpuid() that is similar to our code.
   The history of __cpuid() changes in CLANG/GCC:
   GCC:
     2007: it preserved ebx for (__PIC__ && __i386__)
     2013: it preserved rbx and ebx for __PIC__
     2014: it doesn't preserves rbx and ebx anymore
     we suppose that (__GNUC__ >= 5) fixed that __PIC__ ebx/rbx problem.
   CLANG:
     2014+: it preserves rbx, but only for 64-bit code. No __PIC__ check.
   Why CLANG cares about 64-bit mode only, and doesn't care about ebx (in 32-bit)?
   Do we need __PIC__ test for CLANG or we must care about rbx even if
   __PIC__ is not defined?
*/

#if defined(MY_CPU_AMD64) && defined(__PIC__) \
    && ((defined (__GNUC__) && (__GNUC__ < 5)) || defined(__clang__))
  // rbx preservation code
#elif defined(MY_CPU_X86) && defined(__PIC__) \
    && ((defined (__GNUC__) && (__GNUC__ < 5)) || defined(__clang__))
  // ebx preservation code
#else
  // Standard cpuid without preservation
#endif
```

### Issues
- Complex platform-specific inline assembly
- Mentions issues with GCC < 5 (released 2015)
- CLANG behavior unclear and potentially unnecessary
- Code could be simplified if old compilers are dropped

### Questions
- Is GCC < 5 still supported?
- Is the CLANG workaround still necessary?
- Can we use compiler's `<cpuid.h>` instead?

### Recommendation

**Option 1: Use compiler builtins**
```c
#include <cpuid.h>

void Z7_FASTCALL z7_x86_cpuid(UInt32 p[4], UInt32 func)
{
    __cpuid(func, p[0], p[1], p[2], p[3]);
}

void Z7_FASTCALL z7_x86_cpuid_subFunc(UInt32 p[4], UInt32 func, UInt32 subFunc)
{
    __cpuid_count(func, subFunc, p[0], p[1], p[2], p[3]);
}
```

**Option 2: Minimum GCC version**
```c
#if defined(__GNUC__) && __GNUC__ < 5
  #error "GCC 5.0 or newer required"
#endif
```

**Option 3: Simplify with version check**
```c
#if defined(__GNUC__) && __GNUC__ >= 5
  // Use simple inline assembly without rbx preservation
#else
  // Use complex preservation code for old compilers
#endif
```

---

## General Recommendations

1. **Document minimum compiler versions** in README:
   - MSVC: Visual Studio 2015+ (or specify older if needed)
   - GCC: 5.0+ (or specify older if needed)
   - CLANG: 3.8+ (or specify older if needed)

2. **Add CI testing** for minimum supported compilers

3. **Version-gate workarounds** to apply only where needed

4. **Create tracking issues** for removing workarounds when old compilers are dropped

5. **Add comments with removal dates**:
   ```c
   // TODO: Remove this workaround after dropping VS2005 support (planned: v27.0)
   ```

6. **Test regularly** if workarounds are still needed

### Testing Matrix

| Compiler | Version | Platform | Test Status |
|----------|---------|----------|-------------|
| MSVC | 2015 (14.0) | x64 | ✓ Required |
| MSVC | 2017 (14.1) | x64 | ✓ Required |
| MSVC | 2019 (14.2) | x64 | ✓ Required |
| MSVC | 2022 (14.3) | x64 | ✓ Required |
| GCC | 5.x | x64 | ? Required? |
| GCC | 7.x | x64 | ✓ Required |
| GCC | 11.x | x64 | ✓ Required |
| CLANG | 10.x | x64 | ✓ Required |
| CLANG | 15.x | x64 | ✓ Required |
