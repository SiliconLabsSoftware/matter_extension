## Cursor Cloud specific instructions

This is an embedded firmware SDK (Silicon Labs Matter Extension) for building IoT/smart home device applications that run on Silicon Labs microcontrollers. There are no web servers, databases, or traditional backend services. The "application" is cross-compiled ARM firmware.

### Key development workflows

All development commands are documented in the root `README.md`. The typical workflow is:

1. **Environment setup**: `python3 slc/sl_setup_env.py` — downloads ARM GCC toolchain (12.2), Java (Corretto 21), SLC-CLI, ZAP, Ninja, and Simplicity Commander. Also syncs git submodules and creates required symlinks.
2. **Create a project**: `python3 slc/sl_create_new_app.py <Name> <slcp-file> <board>` — generates a new project from a sample app template.
3. **Build a project**: `python3 slc/sl_build.py <slcp-or-slcw-file> <board>` — runs SLC generate + make to cross-compile firmware.

### Non-obvious caveats

- **Git LFS is required for submodules.** The `third_party/simplicity_sdk` submodule uses Git LFS for binary libraries (`.a` files). After `git submodule update --init`, you must run `cd third_party/simplicity_sdk && git lfs pull` or the linker will fail with "file format not recognized" on LFS pointer files.
- **ZAP SQLite lock errors.** If ZAP code generation fails with `SQLITE_BUSY: database is locked`, delete `~/.zap` and retry. This is noted in the README as well.
- **POST_BUILD_EXE must be set for `make`.** When running `make` directly (not through the Python scripts), you need: `POST_BUILD_EXE=/workspace/slc/tools/SimplicityCommander-Linux/commander/commander STUDIO_ADAPTER_PACK_PATH=/workspace/slc/tools/zap make all -C <project-dir> -f <project>.Makefile -j$(nproc)`.
- **`sl_build.py` expects the Makefile in the parent of the .slcp file**, but SLC generates it inside a subdirectory named after the project. To build directly, use `make` with the correct path to the Makefile inside the generated project subdirectory.
- **No linter or test suite.** This repo has no Python linter configuration (no flake8/pylint/mypy) and no automated test framework. CI builds are handled via Jenkins (see `jenkins_integration/`). The GitHub Actions workflows only handle CLA, version updates, and submodule sync.
- **Sample app .slcp files** are under `slc/apps/` (e.g., `slc/apps/lighting-app/thread/lighting-app.slcp`). Common board targets: `brd4187c` (EFR32 MG24).
- **Python 3.9+** is required for the build scripts. Dependencies are minimal: `python-dotenv` and `dload` (from `requirements.txt`), plus `pyyaml` (used by `sl_create_new_app.py`).
