# Performance Optimization Guide

This document describes performance optimizations applied to address backend bottlenecks identified through profiling.

## Overview

Performance profiling revealed:
- **Backend bound**: 50.4% (memory + execution port contention)
- **Bad speculation**: 21.8% (branch mispredictions at 6.14% miss rate)
- **IPC**: 1.55 (showing room for improvement)

## Optimization Levels

### Build with -O3 Optimization

For maximum performance, build with `-O3` optimization level:

```bash
cd CPP/7zip/Bundles/Alone2
make -j -f makefile.gcc OPT_LEVEL=3
```

Default is `-O2`. Set `OPT_LEVEL=3` for more aggressive optimizations including:
- More aggressive inlining
- Better loop optimization
- Better instruction scheduling

### Build with Link-Time Optimization (LTO)

Enable LTO for cross-translation-unit optimizations:

```bash
cd CPP/7zip/Bundles/Alone2
make -j -f makefile.gcc USE_LTO=1
```

LTO benefits:
- Better inlining across compilation units
- More effective dead code elimination
- Improved interprocedural optimizations

### Combined Optimizations

For best performance, combine both:

```bash
cd CPP/7zip/Bundles/Alone2
make -j -f makefile.gcc OPT_LEVEL=3 USE_LTO=1
```

## Code-Level Optimizations

### Branch Prediction Hints

The hot paths in the match-finder algorithms (`LzFind.c`, `LzFindOpt.c`) now use branch prediction hints:

- `Z7_LIKELY()` - marks likely branches (common case)
- `Z7_UNLIKELY()` - marks unlikely branches (error paths, early exits)

These hints help the compiler and CPU branch predictor:
- Improve instruction cache utilization
- Reduce branch misprediction penalties
- Better code layout for hot paths

Key optimized functions:
- `GetMatchesSpecN_2()` - Main match-finding loop
- `GetMatchesSpec1()` - Binary tree match search
- `SkipMatchesSpec()` - Match skipping

### Memory Access Patterns

Optimizations preserve existing SIMD and prefetch strategies:
- Maintained `USE_SON_PREFETCH` for data prefetching
- Preserved SIMD saturating subtraction (SSE4.1/AVX2/NEON)
- Individual 32-bit copies for better portability

## Performance Testing

### Quick Performance Test

Build and test compression speed:

```bash
# Build with optimizations
cd CPP/7zip/Bundles/Alone2
make -j -f makefile.gcc OPT_LEVEL=3 USE_LTO=1

# Run benchmark
./b/g/7zz b
```

### Comparing Optimization Levels

```bash
# Baseline (-O2, no LTO)
make clean
make -j -f makefile.gcc
./b/g/7zz b > results-o2.txt

# With -O3
make clean
make -j -f makefile.gcc OPT_LEVEL=3
./b/g/7zz b > results-o3.txt

# With -O3 and LTO
make clean
make -j -f makefile.gcc OPT_LEVEL=3 USE_LTO=1
./b/g/7zz b > results-o3-lto.txt
```

## Expected Performance Improvements

Based on profiling data and applied optimizations:

1. **Branch Prediction**: 
   - Target: Reduce 6.14% branch miss rate by 10-20%
   - Impact: Lower bad speculation from 21.8%

2. **Backend Stalls**:
   - Better instruction scheduling with -O3
   - Reduced port contention through better code layout
   - Target: Reduce backend bound from 50.4%

3. **IPC Improvements**:
   - Target: Increase from 1.55 to 1.7-1.9
   - Better instruction-level parallelism

## Platform-Specific Notes

### x86-64
- Full benefit from branch hints with GCC 5+ and Clang 8+
- SIMD optimizations use SSE4.1 and AVX2 where available
- LTO particularly effective on x86-64

### ARM64
- Branch hints supported on GCC 6+ and Clang 3.8+
- NEON optimizations for vector operations
- Good performance gains expected

### Compiler Compatibility

Branch prediction hints (`Z7_LIKELY`/`Z7_UNLIKELY`) are defined in `C/Compiler.h`:
- Clang 8+ and GCC 10+: Full `__builtin_expect()` support
- Older compilers: Macros expand to no-ops (no performance penalty)

## Troubleshooting

### Build Errors with LTO

If LTO causes build errors:
```bash
# Try without LTO
make clean
make -j -f makefile.gcc OPT_LEVEL=3
```

### Performance Regression

If optimizations cause regression:
```bash
# Fall back to default
make clean
make -j -f makefile.gcc
```

### Verification

Always verify correctness after optimization:
```bash
# Create test archive
./b/g/7zz a test.7z /path/to/testdata

# Extract and verify
./b/g/7zz t test.7z
```

## Future Optimizations

Additional optimizations that could be explored:
- Profile-Guided Optimization (PGO)
- Memory alignment tuning for specific architectures
- Further loop unrolling in hot paths
- Additional prefetch tuning

## References

- Original performance analysis: See issue #[number]
- Compiler.h: Branch prediction macro definitions
- LzFind.c, LzFindOpt.c: Optimized match-finder code
