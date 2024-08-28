[![Silicon Labs](./docs/images/silabs-logo.jpg)](https://www.silabs.com)

# Silicon Labs Matter

Welcome to the Silicon Labs Matter Extension repo. Matter is an application layer
that provides a standardized interface between protocols and devices. With
Matter, it is transparent to the underlying device whether the interaction is
from a Thread application or a Wi-Fi application. For more information on Matter
in general see the main
[Matter Overview](https://www.silabs.com/wireless/matter) page. Silicon Labs
supports Matter on both 802.15.4 (Thread) and 802.11 (Wi-Fi) transport
protocols.

Silicon Labs supports Matter on several different hardware platforms including the EFR32, RS9116, WF200 and the new SiWx917 which is a Wi-Fi System-on-Chip (SoC).

**This repo is intended to be used directly for bleeding edge development that closely tracks the CSA Matter codebase. If you are interested in a stable release, we recommend following our official documentation which can be found on [docs.silabs.com](https://docs.silabs.com/matter/2.3.1/matter-start/)**

_To see official release notes containing list of features and knowns issues go to
[SiliconLabs/matter_extension/releases](https://github.com/SiliconLabs/matter_extension/releases)
and find the corresponding notes for the release you are using._

---

## Setting up the Matter Extension repository

1. Fork the Silicon Labs Matter Extension GitHub repo by clicking "Fork" in the web UI https://github.com/SiliconLabsSoftware/matter_extension .

1. Clone your fork of the  Silicon Labs Matter Extension GitHub:

   ```
   git clone https://github.com/<user-name>/matter_extension.git 
   ```

1. Configure the upstream alias:

   ```
   git remote add upstream git@github.com:/SiliconLabsSoftware/matter_extension.git
   ```

Your local repo is now ready for development. Follow the rest of this document for instructions on how to create and build a project. 

Additional setup required for contributing to this repo (not enabled yet): [Contributing](./docs/CONTRIBUTING.md)

Steps for directly cherry-picking CSA Matter repo commits into your environment: [Cherry-picking CSA Commits](docs/CHERRY_PICKING_CSA_COMMITS.md)

## Getting Started with Command Line Development

We provide a set of scripts to set up an environment and build Matter apps in a command line. Silicon Labs Matter leverages an internal tool called Silicon Labs Configurator Command-line Interface (SLC-CLI). SLC-CLI comes pre-integrated in the Simplicity Studio, and is automatically installed by the scripts discussed below; it can be manually installed from here:  [SLC-CLI download](https://www.silabs.com/developers/simplicity-studio/configurator-command-line-interface). This repo can also be used in the Silicon Labs proprietary IDE [Simplicity Studio](https://www.silabs.com/developers/simplicity-studio).


### Setting up the Environment

The `sl_setup_env`.py script creates an .env file to be used to set the environment variables needed for the installed tools, ARM toolchain, SLC-CLI, Java ZAP, Simplicity Commander, Ninja, and Java.

```
python3 slc/sl_setup_env.py
```

### Creating an Application Project

Run the `sl_create_new_app.py` script to create a BRD4187C project with name MyNewApp starting from the lighting-app-thread.slcp example

```
python3 slc/sl_create_new_app.py MyNewApp slc/sample-app/lighting-app/efr32/lighting-app-thread.slcp brd4187c
```

### Building an Application Project

After a project is created the `sl_build.py` script can be used to re-generate the MyNewApp project and build it:

```
python3 slc/sl_build.py MyNewApp/lighting-app-thread.slcp brd4187c
```

## Getting Started with Simplicity Studio Development 

Matter Extension official releases are available to install through Simplicity Studio out of the box. For bleeding edge Matter codebase, this repo can be manually loaded as a custom Extension to the Simplicity SDK in Simplicity Studio.

To stage the Extension for loading it in Studio invoke the following script passing to it the path to some temporary directory (the directory can be safely removed once the Extension is loaded in Studio).

```
python3 slc/stage_extension.py <any/location/on/disk>
```

To load a custom Matter Extension in Studio, navigate to Preferences -> Simplicity Studio -> SDKs -> Add Extension. Navigate to the directory where the extension was staged, and click Open -> Ok -> Apply and Close.  
Note: In general, this repo supports the latest Simplicity SDK version. To confirm if you have the appropriate version, check the [matter.slce](./matter.slce) file.

# License

Matter is released under the [Apache 2.0 license](./LICENSE).
