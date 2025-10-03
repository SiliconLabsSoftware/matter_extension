# Package Generation and Helper Scripts

The contents of these folders are used for generation of packages. This document describes how to create packages and the helper scripts used to maintain package manager metadata.  

---

## Setup  

Follow the documentation on Confluence:  

- [Install SLT](https://confluence.silabs.com/spaces/MATTER/pages/725302792/How+to+work+with+Package+Manager#HowtoworkwithPackageManager-InstallSLT)  
- [Conan (via SLT)](https://confluence.silabs.com/spaces/MATTER/pages/725302792/How+to+work+with+Package+Manager#HowtoworkwithPackageManager-Conan(viaSLT))  

---

## How to Create Packages  

Starting from the **root** directory:  

### Create Matter Stack Package  
```bash
conan export-pkg packages/matter/conanfile.py --name matter --version <matter_extension_version>
```

### Create Matter Sample App Package  
```bash
conan export-pkg packages/matter_sample_app/conanfile.py
```

---

## Helper Scripts  

Helper scripts are stored under:  
```
root/slc/scripts/
```

### `slc/scripts/generate_pkg_slt.py`  
Generates `pkg.slt`, which is used by SLT to determine dependencies to download for development.  

- Centralized utility to generate consistent `pkg.slt` files across SLC projects and solutions.  
- Removes manual maintenance and prevents version drift in dependencies.  
- Supports switching between single- or multi-dependency models for sample apps (option 2 or 3 in [Matter Package Manager design doc](https://confluence.silabs.com/spaces/MATTER/pages/594744893/Matter+Package+Manager), decision still pending).  
- Generates `pkg.slt` for all directories containing a `.slcp` or `.slcw` file (Design option 3).  

---

### `slc/scripts/get_slce_extra_paths.py`  
- Regenerates managed path sections in `packages/matter/matter.slce.extra` deterministically.  
- Ensures only required files (e.g., ZAP templates) are packaged, minimizing package size.  
- Must be run for every `matter_sdk` submodule update.  

---

### `slc/scripts/matter_package_version`  
- Centralized version file used by `generate_pkg_slt`.  
- Designed for reuse across other helper scripts in the future.  

---

## Directory Layout  

```
root/
├── packages/
│   ├── matter/
│   │   ├── conanfile.py
│   │   └── matter.slce.extra
│   ├── matter_sample_app/
│   │   └── conanfile.py
│   ├── remotes/
│   └── README.md
└── slc/
    └── scripts/
```