[![Silicon Labs](./docs/images/silabs-logo.jpg)](https://www.silabs.com)

# Silicon Labs Matter

Welcome to the Silicon Labs Matter Extension repo. Matter is an application layer that provides a standardized interface between protocols and devices. With Matter, it is transparent to the underlying device whether the interaction is from a Thread application or a Wi-Fi application. For more information on Matter in general, see the main [Matter Overview](https://www.silabs.com/wireless/matter) page. Silicon Labs supports Matter on both 802.15.4 (Thread) and 802.11 (Wi-Fi) transport protocols.

Silicon Labs supports Matter on several different hardware platforms including the EFR32, RS9116, WF200, and the new SiWx917, which is a Wi-Fi System-on-Chip (SoC).

**This repo is intended to be used directly for bleeding edge development that closely tracks the CSA Matter codebase. If you are interested in a stable release, we recommend following our official documentation which can be found on [docs.silabs.com](https://docs.silabs.com/matter/2.6.0/matter-start/)**

_To see official release notes containing a list of features and known issues, go to [SiliconLabs/matter_extension/releases](https://github.com/SiliconLabs/matter_extension/releases) and find the corresponding notes for the release you are using._

---

## Setting up the Matter Extension repository

1. Fork the Silicon Labs Matter Extension GitHub repo by clicking "Fork" in the web UI at https://github.com/SiliconLabsSoftware/matter_extension.

1. Clone your fork of the Silicon Labs Matter Extension GitHub repo: `https://github.com/<user-name>/matter_extension`

1. Configure the upstream alias:

   ```
   git remote add upstream git@github.com:/SiliconLabsSoftware/matter_extension.git
   ```

Your local repo is now ready for development. Follow the rest of this document for instructions on how to create and build a project.

Additional setup required for contributing to this repo (not enabled yet): [Contributing](./docs/CONTRIBUTING.md)

Steps for directly cherry-picking CSA Matter repo commits into your environment: [Cherry-picking CSA Commits](docs/CHERRY_PICKING_CSA_COMMITS.md)

## Getting Started with Command Line Development

We provide a set of scripts to set up an environment and build Matter apps in a command line. Silicon Labs Matter leverages an internal tool called Silicon Labs Configurator Command-line Interface (SLC-CLI). SLC-CLI comes pre-integrated in the Simplicity Studio and is automatically installed by the scripts discussed below; it can be manually installed from here: [SLC-CLI download](https://www.silabs.com/developers/simplicity-studio/configurator-command-line-interface). This repo can also be used in the Silicon Labs proprietary IDE [Simplicity Studio](https://www.silabs.com/developers/simplicity-studio).

### Setting up the Environment

Install the following Python packages:

```
pip3 install dload
pip3 install python-dotenv  
```


The `sl_setup_env.py` script creates an `.env` file which contains all the relevant virtual environment paths to be used by `sl_create_new_app.py` and `sl_build.py` scripts. The file is not meant to be used directly and is mentioned here only for reference.

It will also create `environment_variables_vscode.txt`. This file can be referenced to add environment variables for VS Code-based builds.

For Mac and Linux:
```sh
python3 slc/sl_setup_env.py
```

For Windows:

```sh
python slc\sl_setup_env.py
```
The sl_setup_env.py script syncs and checks out the submodules and creates symbolic links for matter_extension. Windows users may need to enable long paths in the system and run the terminal with admin privileges to create the symbolic links.

Users may enable long paths for git by running:
```
git config --system core.longpaths true  
```

### Creating an Application Project

Run the `sl_create_new_app.py` script to create a BRD4187C project with name MyNewApp starting from the lighting-app-thread.slcp example or from the `lighting-app-thread-bootloader.slcw` [solution](https://docs.silabs.com/matter/2.6.0/matter-overview-guides/matter-solutions) application project file:

Sample-App Example: 
For Mac and Linux:

```sh
python3 slc/sl_create_new_app.py MyNewApp slc/sample-app/lighting-app/efr32/lighting-app-thread.slcp brd4187c
```

For Windows:

```sh
python slc\sl_create_new_app.py MyNewApp slc\sample-app\lighting-app\efr32\lighting-app-thread.slcp brd4187c
```

Solutions Examples:

For Mac and Linux:

```sh
python3 slc/sl_create_new_app.py MyNewApp slc/solutions/lighting-app/series-2/lighting-app-thread-bootloader.slcw brd4187c
```

For Windows:

```sh
python slc\sl_create_new_app.py MyNewApp slc\solutions\lighting-app\series-2\lighting-app-thread-bootloader.slcw brd4187c
```

### Building an Application Project

After a project is created, the `sl_build.py` script can be used to re-generate the MyNewApp project and build it:

Sample-App Example:
For Mac and Linux:

```sh
python3 slc/sl_build.py MyNewApp/lighting-app-thread.slcp brd4187c
```

For Windows:

```sh
python slc\sl_build.py MyNewApp\lighting-app-thread.slcp brd4187c
```

Solutions Examples:

For Mac and Linux:

```sh
python3 slc/sl_build.py MyNewApp/lighting-app-thread-bootloader.slcw brd4187c
```

For Windows:

```sh
python slc\sl_build.py MyNewApp\lighting-app-thread-bootloader.slcw brd4187c
```

Alternatively, one can use SLC-CLI commands directly to generate the project and then use `make` to build it.

Windows users will need to install `make` on their system. You can use your own or follow these steps to get `make`:

1. Install the MSYS terminal, which provides a Unix-like environment on Windows.
1. Open the MSYS terminal and install `make` using the command `pacman -S make`.
1. Run the command where make, copy the path, and add it to the PATH environment variable.
1. Restart your command line terminal and run `slc/sl_build.py` or run make directly. You might need to reboot.

**Note:** In rare cases, the build may fail due to missing files in the `zap-generated/` directory. The workaround is to delete the `.zap` folder in the home directory.

## Flash an Application to Device

The generated application binaries can be found at MyNewApp/artifact/lighting-app-thread.s37.

Simplicity Commander is used to flash binaries to the device. It is downloaded by the sl_setup.py script and can be found at slc/tools/SimplicityCommander-Mac/Commander.app/Contents/MacOS/commander.

```sh
slc/tools/SimplicityCommander-Mac/Commander.app/Contents/MacOS/commander flash MyNewApp/artifact/lighting-app-thread.s37
```

**Note:** If using SiWx917 SoC, `.rps` file will need be flashed, instead of the `.s37` file.

More info on Simplicity Commander can be found [here](https://www.silabs.com/documents/public/user-guides/ug162-simplicity-commander-reference-guide.pdf).

## Modifying an Application Project

The resulting user project can be modified like any other SLC project. Software components can be added or removed by modifying the project's .slcp file, configuration can be applied by modifying the files in the config directory, and the application logic can be managed through the files in the src directory. Various SLC-CLI commands can be used to examine, validate, or re-generate the project after a modification. See [Software Project Generation and Configuration with SLC-CLI](https://docs.silabs.com/simplicity-studio-5-users-guide/latest/ss-5-users-guide-tools-slc-cli/) for more information.

### Adding/Removing Components in an Application Project

Users can add/remove components from a project's .slcp file to enable/disable particular features. To add a component, users need to add the following lines in the .slcp under the **component:** section:

`- {from: matter, id: <component_id>}`

### Adding source/header files in an Application Project

Users can add source/header files from a project's .slcp file to enabling particular functionalities. To add a source/header files users need to add the relative path of the file in the slcp under `source:`
and `include:` tags.

```sh
source:
- {path: src/AppTask.cpp}
- {path: <path/to/source.cpp>}
```

```sh
include:
- path: include
  file_list:
  - {path: AppConfig.h}
- path: <path/to/include/folder>
  file_list:
  - {path: <include.h>}
```

### Adding/Removing Matter Clusters in an Application Project

To add a new Matter cluster, the cluster must be enabled in the ZAP tool and the respective cluster component must be added to the `.slcp` file. For modifying Matter endpoints and clusters, invoke the ZAP tool passing to it the application's ZAP file:

```C
python3 slc/sl_run_zaptool.py MyNewApp/config/common/lighting-thread-app.zap
```

Once the cluster is enabled in the ZAP tool and the file is saved, the corresponding component must be added to the project's .slcp file. The component IDs for the cluster components can be found in `src/app/zap-templates/cluster-to-component-dependencies.json`. A cluster component mapping is written in the following pattern:
```sh
  {
    "clusterCode": "Cluster Code",
    "value": [
      "%extension-matter%<component_id>"
    ]
  }
```
For example to enable the "level control-server cluster" the user should enable the cluster in the .zap file in the ZAP tool and then add the `matter_level_control` component to the project's .slcp file:

`- {from: matter, id: matter_level_control}`

The relevant entry from `src/app/zap-templates/cluster-to-component-dependencies.json`:

```sh
  {
    "clusterCode": "level control-server",
    "value": [
      "%extension-matter%matter_level_control"
    ]
  }
```
More details on how to develop using SLC CLI can be found at [Creating Matter Applications using SLC CLI](https://docs.silabs.com/matter/2.6.0/matter-overview-guides/matter-slc-cli)


## Project Upgrades

Users can upgrade a project to a newer Matter extension version by performing the following steps:

Checkout the target tag/branch to which you need to upgrade the project.
1. Run the slc/sl_setup_env.py script to check out dependencies of that target tag/branch.
1. Run the slc/sl_project_upgrade.py script to upgrade the project to the target Matter extension version.
1. For example, to upgrade a project to Matter extension v2.6.0:
   
`python3 slc/sl_project_upgrade.py MyNewApp/lighting-app-thread.slcp 2.6.0`


## Getting Started with Simplicity Studio Development 

Matter Extension official releases are available to install through Simplicity Studio out of the box. For bleeding-edge Matter codebase, this repo can be manually loaded as a custom Extension to the Simplicity SDK in Simplicity Studio.

To stage the Extension for loading it in Studio, invoke the following script passing to it the path to some temporary directory (the directory can be safely removed once the Extension is loaded in Studio).

```
python3 slc/stage_extension.py <any/location/on/disk>
```
The stage_extension.py script requires that submodules are initialized and checked out. The `sl_setup.py` script already checks out submodules, alternatively, users can manually checkout the submodules using the following commands.
```
git submodule sync 
git submodule update --init
```

To load a custom Matter Extension in Studio, navigate to Preferences -> Simplicity Studio -> SDKs -> Add Extension. Navigate to the directory where the extension was staged, and click Open -> OK -> Apply and Close.  
Note: In general, this repo supports the latest Simplicity SDK version. To confirm if you have the appropriate version, check the [matter.slce](./matter.slce) file.
Note: Matter requires an up-to-date version of the ZAP tool. To make sure that your Studio installation has the most recent ZAP, follow these steps to trigger the Studio update: In Studio -> Help, click on Update Software. In the Installation Manager screen, click Update All; the Studio will restart after the update is finished. After a ZAP update, the existing Matter projects must be re-generated by clicking "Force Generation" in the project window menu.

# License

Matter is released under the [Apache 2.0 license](./LICENSE).
