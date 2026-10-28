# Matter Generator Firmware - TrustZone (EFR32 Series 2)

TrustZone variant of the Matter Generator Firmware. The secure side
(`generator_firmware_trustzone_s.slcp`) exposes the NVM3 access used by the
non-secure side (`generator_firmware_trustzone_ns.slcp`), which runs the
provisioning protocol.

Sources live in `third_party/matter_sdk/examples/generator-firmware/silabs`.

## Documentation

[AN1374: Series 2 TrustZone](https://www.silabs.com/documents/public/application-notes/an1374-trustzone.pdf)

## Build

From the root of the extension:

```bash
slc generate -w slc/apps/generator_firmware/trustzone/generator_firmware_trustzone.slcw \
    -d out/generator_firmware/trustzone --with brd4187c --sdk "$SISDK_ROOT"
make -j$(nproc) -C out/generator_firmware/trustzone -f generator-workspace.solution.Makefile
```

## Flash

```bash
python3 provision.py --gen_fw out/generator_firmware/trustzone/artifact/generator-workspace-full.s37
```
