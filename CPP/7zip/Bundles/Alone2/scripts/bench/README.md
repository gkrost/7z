# 7zz Evolutionary Benchmark Harness

This harness rebuilds `7zz` with GCC flag variants and runs `7zz b` to score throughput. It uses a small genetic algorithm (GA) to explore optimization flags and keeps a cache of results.

## Prereqs

- GCC + g++ + make in PATH
- Python 3.9+

## Quick start

From the repo root (`CPP/7zip/Bundles/Alone2`):

```
python3 scripts/bench/evo_flags.py --generations 6 --population 6 --verbose
```

## What it does

- Builds to `b/ga/7zz` with per-candidate flags
- Runs `b/ga/7zz b` and parses the 22-25 dict results
- Scores by default on **best compress KiB/s** (max dict)
- Logs results to `scripts/bench/results/evo_results.jsonl`
- Logs raw benchmark output to `scripts/bench/results/logs/`
- Deletes the build directory before every candidate build

## Common runs

Compress throughput (best dict):

```
python3 scripts/bench/evo_flags.py --target compress --score-mode best --generations 8 --population 8
```

Decompress throughput:

```
python3 scripts/bench/evo_flags.py --target decompress --generations 8 --population 8
```

Balanced (avg of compress + decompress):

```
python3 scripts/bench/evo_flags.py --target balanced --score-mode average --generations 8 --population 8
```

Force a clean failure blacklist and re-run:

```
python3 scripts/bench/evo_flags.py --blacklist-reset --generations 8 --population 8
```

Add extra base flags:

```
python3 scripts/bench/evo_flags.py --base-flags "-pipe" --generations 6 --population 6
```

## Notes

- The GA explores pools defined near the top of `scripts/bench/evo_flags.py`.
- Unsupported flags are logged with `status` and skipped in later generations.
