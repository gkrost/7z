## Remove or document 139 disabled code blocks (#if 0)

**Priority**: Medium (Code Maintenance)  
**Category**: Dead Code  
**Affected Files**: Multiple C files

### Description

The codebase contains 139 instances of `#if 0` preprocessor directives that disable code blocks. This dead code should either be removed if no longer needed or documented if kept for future reference.

### Sample Findings

#### Major disabled code blocks:
- `C/CpuArch.c:721` - Entire `CPU_IsSupported_AVX512F_AVX512VL()` function disabled
- `C/Threads.c:96` - Debug code disabled
- `C/Threads.c:170, 178` - Debug code disabled
- `C/Alloc.c:19, 361, 509, 562` - Multiple disabled allocation-related code blocks
- `C/Blake2.h:9, 56` - Disabled definitions
- `C/Blake2s.c:263, 293` - Disabled BLAKE2 implementation code
- `C/Sha512.c:91` - Size optimization code disabled: `#if 0 // 1 for size optimization`
- `C/Sha512.c:462` - Debug LONGJMP mode disabled: `#if 0 || !defined(_MSC_VER) // 1 || : for debug LONGJMP mode`
- `C/Md5.c:25` - Alignment-related code disabled

### Example of Disabled Code

```c
// C/CpuArch.c:721-735
#if 0
BoolInt CPU_IsSupported_AVX512F_AVX512VL(void)
{
  if (!CPU_IsSupported_AVX())
    return False;
  if (z7_x86_cpuid_GetMaxFunc() < 7)
    return False;
  {
    UInt32 d[4];
    BoolInt v;
    z7_x86_cpuid(d, 7);
    // printf("\ncpuid(7): ebx=%8x ecx=%8x\n", d[1], d[2]);
    v = 1
      & (BoolInt)(d[1] >> 16)  // avx512f
      & (BoolInt)(d[1] >> 31); // avx512vl
    return v;
  }
}
#endif
```

### Issues

1. **Code bloat**: Dead code increases repository size and makes codebase harder to navigate
2. **Confusion**: Developers may be unsure if disabled code should be re-enabled
3. **Maintenance burden**: Code may become outdated without being updated
4. **Merge conflicts**: More lines = more potential for conflicts
5. **Lost context**: Without comments, purpose of disabled code is unclear

### Recommended Actions

1. **Review each #if 0 block** to determine if it's still needed:
   - Is this debug code that might be useful? → Convert to `#ifdef DEBUG_MODE`
   - Is this performance test code? → Convert to `#ifdef ENABLE_PERF_TEST`
   - Is this obsolete code? → Remove entirely
   - Is this future feature? → Add comment explaining purpose and timeline

2. **Replace #if 0 with named macros** for intentionally disabled code:
   ```c
   // Instead of:
   #if 0
   // debug code
   #endif
   
   // Use:
   #ifdef ENABLE_DEBUG_LOGGING
   // debug code
   #endif
   ```

3. **Document retained disabled code**:
   ```c
   #if 0  // TODO: AVX512 support planned for v26.0 - see issue #XXX
   BoolInt CPU_IsSupported_AVX512F_AVX512VL(void)
   ```

4. **Remove clearly obsolete code** and rely on version control history

5. **Create tracking issues** for code that should be re-enabled in the future

### Proposed Approach

Phase 1: Quick wins (remove obviously obsolete code)
- Remove disabled code in files that haven't been modified in 2+ years
- Remove disabled code with comments like "old version"

Phase 2: Review and document
- Review remaining blocks with maintainers
- Add comments explaining why code is disabled
- Convert to named macros where appropriate

Phase 3: Clean up
- Remove any remaining #if 0 blocks without clear purpose
