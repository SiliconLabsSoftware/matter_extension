# SPI Flash Storage Bootloader (Single Image with Slot Size of 1024 KB)

SPI flash storage bootloader; single 1024 kB image slot. Requires external SPI flash of at least 1 MB. Default for Matter projects. See UG489 for configuration and storage layout.

## Table of Contents

- [Purpose and Scope](#purpose-and-scope)
- [Prerequisites](#prerequisites)
- [Steps to Run Demo](#steps-to-run-demo)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)
- [Report Bugs & Get Support](#report-bugs--get-support)

## Purpose and Scope

This application requires external SPI Flash of at least 1 MB. This sample configuration of the simplicity bootloader configures the bootloader to use an external SPI flash to store firmware update images. The storage configuration is set up to store a single firmware update image at a time, in a single storage slot. The storage slot is configured to start at address 0x0 of the SPI flash, and have a size of 1024 kB. This can be configured on the *"Bootloader Storage Slot Setup"*. This is the default bootloader configuration to use with Matter projects.

For information about multiple storage slot support, see the "SPI Flash Storage Bootloader (multiple images)" sample configuration.

## Prerequisites

- **Hardware:** See [Matter hardware requirements](https://docs.silabs.com/matter/2.8.0/matter-prerequisites/hardware-requirements). This bootloader requires a board with external SPI flash of at least 1 MB.
- **Software:** See [Matter software requirements](https://docs.silabs.com/matter/2.8.0/matter-prerequisites/software-requirements).

## Steps to Run Demo

1. Build the bootloader project for your target board, or use a pre-built binary.
2. Flash the bootloader to the device before flashing the application. Pre-built bootloader binaries for supported devices are available at [Matter Bootloader Binaries](https://docs.silabs.com/matter/2.8.0/matter-prerequisites/matter-artifacts#matter-bootloader-binaries).

## Troubleshooting

- For configuration, storage layout, and security options, see *UG489: Simplicity Bootloader User's Guide*.

## Resources

- [Gecko Bootloader User's Guide (UG489)](https://www.silabs.com/documents/public/user-guides/ug489-gecko-bootloader-user-guide-gsdk-4.pdf)
- [Matter Bootloader Binaries](https://docs.silabs.com/matter/2.8.0/matter-prerequisites/matter-artifacts#matter-bootloader-binaries)
- [Matter Prerequisites](https://docs.silabs.com/matter/2.8.0/matter-prerequisites)

## Report Bugs & Get Support

You are always encouraged and welcome to report any issues you found to us via [Silicon Labs Community](https://community.silabs.com).
