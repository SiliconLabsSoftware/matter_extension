# Matter Generator Firmware - SiWx917

The Generator Firmware (GFW) is flashed temporarily on a device by the Silicon
Labs provisioning tool. It generates the DAC key pair and CSR on the device and
writes the factory data used by the production application.

Sources live in `third_party/matter_sdk/examples/generator-firmware/silabs`,
and the Provision Core library and its headers come from
`third_party/matter_support/provision`.

## Build

From the root of the extension:

```bash
slc generate -p slc/apps/generator_firmware/si917/generator_firmware_si917.slcp \
    -d out/generator_firmware/si917 --with "brd4338a;wiseconnect3_sdk" \
    --sdk-package-path "$SISDK_ROOT,third_party/wifi_sdk/wiseconnect.slce"
make -j$(nproc) -C out/generator_firmware/si917 -f generator.Makefile
commander rps create --app out/generator_firmware/si917/build/debug/generator.s37 si917_core.rps
```

The provisioning tool expects `si917_core.rps` (BRD4338A) or `si917y_core.rps`
(BRD4343A).
