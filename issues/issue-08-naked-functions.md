## Review and document naked function usage

**Priority**: Low (Working Legacy Code)  
**Category**: Legacy Assembly  
**Affected Files**: `C/CpuArch.c`, `C/Xxh64.c`

### Description

The codebase uses `__declspec(naked)` functions, which is a legacy MSVC feature that bypasses compiler-generated function prologue/epilogue code. While these currently work, naked functions are compiler-specific, hard to maintain, and not portable.

### Locations

1. **`C/CpuArch.c:161`** - `UInt32 __declspec(naked) Z7_FASTCALL z7_x86_cpuid_GetMaxFunc(void)`
2. **`C/CpuArch.c:195`** - `void __declspec(naked) Z7_FASTCALL z7_x86_cpuid(UInt32 p[4], UInt32 func)`
3. **`C/CpuArch.c:215`** - `void __declspec(naked) Z7_FASTCALL z7_x86_cpuid_subFunc(UInt32 p[4], UInt32 func, UInt32 subFunc)`
4. **`C/Xxh64.c:97`** - `__declspec(naked)` function (exact usage not shown in search)

### Example Code

```c
// C/CpuArch.c:195-212
void __declspec(naked) Z7_FASTCALL z7_x86_cpuid(UInt32 p[4], UInt32 func)
{
  UNUSED_VAR(p)
  UNUSED_VAR(func)
  __asm   push    ebx
  __asm   push    edi
  __asm   mov     edi, ecx    // p
  __asm   mov     eax, edx    // func
  __asm   xor     ecx, ecx    // subfunction (optional) for (func == 0)
  __asm   cpuid
  __asm   mov     [edi     ], eax
  __asm   mov     [edi +  4], ebx
  __asm   mov     [edi +  8], ecx
  __asm   mov     [edi + 12], edx
  __asm   pop     edi
  __asm   pop     ebx
  __asm   ret     0
}
```

### Context

These naked functions are **only used for x86 32-bit MSVC builds**:
```c
#if !defined(MY_CPU_AMD64)
  // Naked functions here
#endif
```

For other platforms, alternative implementations exist:
- **x64 MSVC**: Uses `__cpuid()` intrinsic (lines 235-295)
- **GCC/CLANG**: Uses inline assembly (lines 28-93)

### Why Naked Functions Were Used

1. **Full control**: Direct control over register usage for FASTCALL convention
2. **Performance**: No function overhead (prologue/epilogue)
3. **Specific needs**: Custom calling convention for CPUID wrapper

### Issues with Naked Functions

#### Portability
- MSVC-specific (`__declspec(naked)` not supported by GCC/CLANG)
- Not available in 64-bit MSVC in all scenarios
- Cannot be compiled in other environments

#### Maintenance
- No compiler optimization
- No compiler error checking
- No stack checking
- Easy to introduce bugs (incorrect register usage, stack corruption)
- Difficult to debug

#### Documentation
- Requires deep understanding of calling conventions
- Assembly syntax is MSVC-specific
- Hard for new contributors to understand

#### Future Compatibility
- May not work with future compiler versions
- Microsoft may deprecate or change behavior
- ARM64 doesn't support naked functions

### Current Status

✅ **Working**: The naked functions currently work correctly  
✅ **Platform-specific**: Only used on x86 32-bit MSVC  
✅ **Alternatives exist**: Other platforms use different implementations  
⚠️ **Legacy**: This is old-style code from 2000s era  

### Recommendations

#### Option 1: Keep with Better Documentation (RECOMMENDED)

Since these functions work and are isolated to one platform, keep them but improve documentation:

```c
/*
 * z7_x86_cpuid() - Execute CPUID instruction on x86
 * 
 * This function uses __declspec(naked) for x86 32-bit MSVC builds to:
 * 1. Properly preserve EBX register (required in PIC code)
 * 2. Implement FASTCALL convention manually
 * 3. Avoid compiler-generated prologue/epilogue
 * 
 * PLATFORM: x86 32-bit MSVC only
 * ALTERNATIVES: 
 *   - x64 MSVC: Uses __cpuid() intrinsic (see line 282)
 *   - GCC/CLANG: Uses inline asm (see line 84)
 * 
 * CAUTION: Changes to this function require careful testing
 * to avoid stack corruption or register clobbering.
 */
void __declspec(naked) Z7_FASTCALL z7_x86_cpuid(UInt32 p[4], UInt32 func)
{
  // Implementation...
}
```

#### Option 2: Replace with Inline Assembly

Convert to inline assembly (still MSVC-specific but more maintainable):

```c
void Z7_FASTCALL z7_x86_cpuid(UInt32 p[4], UInt32 func)
{
  __asm {
    push    ebx
    push    edi
    mov     edi, ecx    // p (FASTCALL first param in ECX)
    mov     eax, edx    // func (FASTCALL second param in EDX)
    xor     ecx, ecx
    cpuid
    mov     [edi     ], eax
    mov     [edi +  4], ebx
    mov     [edi +  8], ecx
    mov     [edi + 12], edx
    pop     edi
    pop     ebx
  }
}
```

Benefits:
- Compiler can manage stack frame
- Better error checking
- Less fragile
- Still explicit control over registers

#### Option 3: Use Compiler Intrinsics

If dropping very old MSVC support, use intrinsics everywhere:

```c
#if defined(_MSC_VER)
  #include <intrin.h>
  void Z7_FASTCALL z7_x86_cpuid(UInt32 p[4], UInt32 func)
  {
    __cpuid((int *)p, (int)func);
  }
#elif defined(__GNUC__) || defined(__clang__)
  #include <cpuid.h>
  void Z7_FASTCALL z7_x86_cpuid(UInt32 p[4], UInt32 func)
  {
    __get_cpuid(func, &p[0], &p[1], &p[2], &p[3]);
  }
#endif
```

Note: `__cpuid` has been available since much earlier MSVC versions (for example, VC6 on x86); this option instead assumes you can rely on the intrinsic on your target architectures (including x64) and are no longer constrained by very old MSVC versions or ECX-related CPUID bugs.

### Testing Requirements

If changes are made to naked functions:

1. **Test on x86 32-bit**:
   - Windows XP (if still supported)
   - Windows 7 32-bit
   - Windows 10 32-bit

2. **Test with different MSVC versions**:
   - MSVC 6.0 (if still supported)
   - MSVC 2005
   - MSVC 2010
   - MSVC 2015
   - MSVC 2019
   - MSVC 2022

3. **Verify CPUID results**:
   - Test on Intel CPUs
   - Test on AMD CPUs
   - Test with different CPUID function numbers
   - Test with sub-functions (ECX parameter)

4. **Memory safety**:
   - Run with application verifier
   - Check for stack corruption
   - Verify register preservation

### Action Items

1. ✅ **Document existing naked functions** with comments explaining:
   - Why they exist
   - What platforms they're for
   - What alternatives exist
   - What cautions apply

2. 📋 **Add to technical debt tracker**:
   - Consider replacing when dropping old MSVC support
   - Monitor for compiler deprecation warnings
   - Review when porting to new architectures

3. 📋 **Create test coverage**:
   - Ensure x86 32-bit builds are tested in CI
   - Add specific CPUID result verification tests

4. 📋 **Document minimum compiler versions**:
   - Clarify which MSVC versions require naked functions
   - Document migration path when support is dropped

### Related Issues

- Issue #6: Compiler Workarounds
- Consider together when determining minimum MSVC version

### References

- [MSVC __declspec(naked) documentation](https://docs.microsoft.com/en-us/cpp/cpp/naked-cpp)
- [Calling Conventions on x86](https://docs.microsoft.com/en-us/cpp/cpp/calling-conventions)
- [CPUID Instruction](https://en.wikipedia.org/wiki/CPUID)
