# GitHub Actions Workflow

## Build 7z Linux x64

This workflow builds the 7z command-line tool for Linux x64 architecture.

### What it does

1. **Builds the 7za binary** - Compiles the 7z source code using GCC without assembly optimizations
2. **Runs benchmark test** - Executes `7za b` to verify the binary works correctly
3. **Uploads artifacts** - Stores the compiled binary for download (retained for 30 days)

### Triggers

- Push to `main` or `master` branch
- Pull requests to `main` or `master` branch
- Manual trigger via `workflow_dispatch`

### Build Process

The workflow uses the standard build process for 7z on Linux:
```bash
cd CPP/7zip/Bundles/Alone
make -j -f ../../cmpl_gcc.mak
```

This produces the `7za` binary at `CPP/7zip/Bundles/Alone/b/g/7za`.

### Dependencies

- Ubuntu latest (via `ubuntu-latest` runner)
- build-essential
- g++
- make

### Artifacts

The compiled `7za` binary is uploaded as an artifact named `7za-linux-x64` and can be downloaded from the workflow run page.
