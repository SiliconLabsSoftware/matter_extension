# Matter Generator Firmware - EFR32

The Generator Firmware (GFW) is flashed temporarily on a device by the Silicon
Labs provisioning tool. It generates the DAC key pair and CSR on the device and
writes the factory data used by the production application.

This project supports EFR32 Series 2 (xG24, xG26) and Series 3 (SiXG301)
devices. Sources live in
`third_party/matter_sdk/examples/generator-firmware/silabs`, and the Provision
Core library and its headers come from `third_party/matter_support/provision`.
