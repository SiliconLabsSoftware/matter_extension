# Matter MG - SoC Generator Firmware FreeRTOS

Demonstrates on-device DAC key-pair and CSR generation and Matter factory data provisioning on MG SoC devices.

## Table of Contents

- [Matter MG - SoC Generator Firmware FreeRTOS](#matter-mg---soc-generator-firmware-freertos)
  - [Table of Contents](#table-of-contents)
  - [Purpose/Scope](#purposescope)
  - [Prerequisites/Setup Requirements](#prerequisitessetup-requirements)
    - [HW Requirements](#hw-requirements)
    - [SW Requirements](#sw-requirements)
  - [Steps to Run Demo](#steps-to-run-demo)
    - [Configuration and Setup](#configuration-and-setup)
      - [TrustZone](#trustzone)
    - [Steps for Execution](#steps-for-execution)
  - [Troubleshooting](#troubleshooting)
  - [Resources](#resources)
  - [Report Bugs \& Get Support](#report-bugs--get-support)

## Purpose/Scope

The Generator Firmware (GFW) is flashed temporarily by the Silicon Labs Matter
provisioning tool. It generates the Device Attestation Certificate (DAC) key
pair and Certificate Signing Request (CSR) on the device, and writes factory
data used by the production Matter application.

This project targets MG Series 2 (xG24, xG26) and Series 3 (SiXG301) SoC
devices. Application sources live in
`third_party/matter_sdk/examples/generator-firmware/silabs`. The Provision Core
library and headers come from `third_party/matter_support/provision`.

TrustZone-capable MG24 boards can use the TrustZone workspace in this folder,
which builds the secure side, non-secure side, and bootloader into a combined
artifact.

## Prerequisites/Setup Requirements

### HW Requirements

- Silicon Labs MG development board supported by this example (for example
  BRD4187C, BRD4116A, or BRD4407A)
- USB cable for power and debug

For a full list of hardware requirements, see
[Matter Hardware Requirements](https://docs.silabs.com/matter/2.10.0/matter-overview/#hardware-requirements).

### SW Requirements

- Simplicity Studio v5 with the Silicon Labs Matter extension
- Commander (included with Simplicity Studio)
- Silicon Labs Matter provisioning tool (host-side)

For a full list of software requirements, see
[Matter Software Requirements](https://docs.silabs.com/matter/2.10.0/matter-overview/#software-requirements).

## Steps to Run Demo

### Configuration and Setup

Generator Firmware is not a standalone demo. It runs together with the host-side
Matter provisioning script, which flashes the image and drives DAC/CSR
generation and factory-data injection. No project-file customization is
required for the default provisioning flow on supported MG boards. GFW does not
require a bootloader; the provisioning tool flashes it as a temporary image.

#### TrustZone

TrustZone requires a workspace that combines the secure, non-secure, and
bootloader builds. The workspace is defined by `matter_mg_soc_generator_firmware_trustzone_freertos.slcw`

Then flash the combined artifact produced under the board output directory.

### Steps for Execution

1. Build the Generator Firmware workspace for your board in Simplicity Studio,
   or with the SLC CLI:

   ```shell
   ./slc/build.sh slc/apps/generator_firmware/mg/matter_mg_soc_generator_firmware_freertos.slcw brd4187c
   ./slc/build.sh slc/apps/generator_firmware/mg/matter_mg_soc_generator_firmware_freertos.slcw brd4407a
   ```

2. Use the Silicon Labs Matter provisioning tool to flash the generated image
   and run factory provisioning (DAC/CSR generation and credential injection).
3. After provisioning completes, flash the production Matter application onto
   the device.

## Troubleshooting

**Provisioning tool cannot talk to the device**

- Confirm RTT/debug connection and that Generator Firmware is running.
- Retry with a full chip erase, then reflash Generator Firmware.

**TrustZone build or flash fails**

- Build and flash through the TrustZone workspace, not the secure or
  non-secure projects alone.
- Confirm the board supports TrustZone (MG24).

## Resources

- [Silicon Labs Matter Documentation](https://docs.silabs.com/matter/2.10.0/)
- [Matter Provisioning Overview](https://docs.silabs.com/matter/2.10.0/matter-provisioning/)
- [Simplicity Studio User Guide](https://docs.silabs.com/simplicity-studio-5-users-guide/latest/)

## Report Bugs & Get Support

You are always encouraged and welcome to report any issues you found to us via
[Silicon Labs Community](https://community.silabs.com).
