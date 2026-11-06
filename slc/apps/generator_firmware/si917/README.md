# Matter SiWx917 - SoC Generator Firmware FreeRTOS

Demonstrates on-device DAC key-pair and CSR generation and Matter factory provisioning on SiWx917 SoC devices.

## Table of Contents

- [Matter SiWx917 - SoC Generator Firmware FreeRTOS](#matter-siwx917---soc-generator-firmware-freertos)
  - [Table of Contents](#table-of-contents)
  - [Purpose/Scope](#purposescope)
  - [Prerequisites/Setup Requirements](#prerequisitessetup-requirements)
    - [HW Requirements](#hw-requirements)
    - [SW Requirements](#sw-requirements)
  - [Steps to Run Demo](#steps-to-run-demo)
    - [Program a Bootloader](#program-a-bootloader)
    - [Configuration and Setup](#configuration-and-setup)
    - [Steps for Execution](#steps-for-execution)
  - [Troubleshooting](#troubleshooting)
  - [Resources](#resources)
  - [Report Bugs \& Get Support](#report-bugs--get-support)

## Purpose/Scope

The Generator Firmware (GFW) is flashed temporarily by the Silicon Labs Matter
provisioning tool. It generates the Device Attestation Certificate (DAC) key
pair and Certificate Signing Request (CSR) on the device, and writes factory
data used by the production Matter application.

This project targets SiWx917 SoC devices. Application sources live in
`third_party/matter_sdk/examples/generator-firmware/silabs`. The Provision Core
library and headers come from `third_party/matter_support/provision`.

## Prerequisites/Setup Requirements

### HW Requirements

- Silicon Labs SiWx917 development board supported by this example (for
  example BRD4338A or BRD4343A)
- USB cable for power and debug

For a full list of hardware requirements, see
[Matter Hardware Requirements](https://docs.silabs.com/matter/2.10.0/matter-overview/#hardware-requirements).

### SW Requirements

- Simplicity Studio v5 with the Silicon Labs Matter extension and WiSeConnect
  SDK
- Commander (included with Simplicity Studio)
- Silicon Labs Matter provisioning tool (host-side)

For a full list of software requirements, see
[Matter Software Requirements](https://docs.silabs.com/matter/2.10.0/matter-overview/#software-requirements).

## Steps to Run Demo

### Program a Bootloader

Generator Firmware is normally flashed by the provisioning tool as a temporary
image. When building manually, create an RPS image with Commander after the
application build.

### Configuration and Setup

Generator Firmware is not a standalone demo. It runs together with the host-side
Matter provisioning script, which flashes the image and drives DAC/CSR
generation and factory-data injection. No project-file customization is
required for the default provisioning flow on supported SiWx917 boards.

### Steps for Execution

1. Build the Generator Firmware workspace for your board in Simplicity Studio,
   or with the SLC CLI:

   ```shell
   ./slc/build.sh slc/apps/generator_firmware/si917/matter_siwx917_soc_generator_firmware_freertos.slcw brd4338a
   ```

2. Use the Silicon Labs Matter provisioning tool to flash the image and run
   factory provisioning (DAC/CSR generation and credential injection).
3. After provisioning completes, flash the production Matter application onto
   the device.

## Troubleshooting

**Provisioning tool cannot talk to the device**

- Confirm RTT/debug connection and that Generator Firmware is running.
- Verify the RPS image name matches the board family expected by the
  provisioning tool.

**WiSeConnect SDK not found during generate**

- Ensure the WiSeConnect / wifi_sdk package path is available to SLC when
  generating the project.

## Resources

- [Silicon Labs Matter Documentation](https://docs.silabs.com/matter/2.10.0/)
- [Matter Provisioning Overview](https://docs.silabs.com/matter/2.10.0/matter-provisioning/)
- [Simplicity Studio User Guide](https://docs.silabs.com/simplicity-studio-5-users-guide/latest/)

## Report Bugs & Get Support

You are always encouraged and welcome to report any issues you found to us via
[Silicon Labs Community](https://community.silabs.com).
