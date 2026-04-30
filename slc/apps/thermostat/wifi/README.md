# Matter over Wi-Fi Thermostat Example

The Matter over Wi-Fi thermostat example is a baseline demonstration of a thermostat built with Simplicity SDK. It can be controlled by a Matter controller over a Wi-Fi network.

## Table of Contents

- [Matter over Wi-Fi Thermostat Example](#matter-over-wi-fi-thermostat-example)
  - [Table of Contents](#table-of-contents)
  - [Purpose/Scope](#purposescope)
  - [Prerequisites/Setup Requirements](#prerequisitessetup-requirements)
    - [HW Requirements](#hw-requirements)
    - [SW Requirements](#sw-requirements)
  - [Steps to Run Demo](#steps-to-run-demo)
    - [Configuration and Setup](#configuration-and-setup)
    - [Steps for Execution](#steps-for-execution)
  - [Troubleshooting](#troubleshooting)
  - [Resources](#resources)
  - [Report Bugs \& Get Support](#report-bugs--get-support)

## Purpose/Scope

For more general information on running matter applications and pre-requisites please look at online 
documentation for Matter available on docs.silabs.com. Follow Wi-Fi demo instructions depending on the example you are running.
[Demo instructions for Wi-Fi](https://docs.silabs.com/matter/2.9.0/matter-wifi)

The device is commissioned over Bluetooth Low Energy (BLE), during which the Matter
controller and device exchange security credentials in the Rendez-vous procedure.
Wi-Fi credentials (SSID and PSK) are then provided so the device joins your Wi-Fi network and can be controlled by any Matter-compliant controller.

In Wifi configurations, the region code can be set in this
[file](https://github.com/SiliconLabsSoftware/matter_sdk/blob/v2.9.0/src/platform/silabs/wifi/SiWx/WifiInterfaceImpl.cpp).
Search for `REGION_CODE` (build-time default) or `region_code` in the Wi-Fi configuration struct.

The available region codes are defined by the `sl_wifi_region_code_t` enum in
[sl_wifi_constants.h](https://github.com/SiliconLabs/wiseconnect/blob/v4.1.0-content-for-docs/components/protocol/wifi/inc/sl_wifi_constants.h).
Search for `sl_wifi_region_code_t` or the `SL_WIFI_REGION_` enumerator names.

## Prerequisites/Setup Requirements

### HW Requirements

For a full list of hardware requirements, see [Matter Hardware Requirements](https://docs.silabs.com/matter/2.8.1/matter-overview/#hardware-requirements) documentation.

### SW Requirements

For a full list of software requirements, see [Matter Software Requirements](https://docs.silabs.com/matter/2.8.1/matter-overview/#software-requirements) documentation.

## Steps to Run Demo

### Configuration and Setup

This sample app works out of the box with no additional configuration required. To customize the device, see the
[Custom Matter Device Development](https://docs.silabs.com/matter/2.8.1/matter-references/custom-matter-device#custom-matter-device-development) guide.

**Region code (SiWx917 Wi-Fi):** For Wi-Fi configurations, the region code can be set in this [file](https://github.com/SiliconLabsSoftware/matter_sdk/blob/v2.8.1/src/platform/silabs/wifi/SiWx/WifiInterfaceImpl.cpp). The available region codes can be found [here](https://github.com/SiliconLabs/wiseconnect/blob/v4.0.1-content-for-docs/components/protocol/wifi/inc/sl_wifi_constants.h#L739).

### Steps for Execution

1. Build and flash the application to your board.
2. On startup, **LED 0** flashes short-on (50 ms on / 950 ms off), indicating the
   device is waiting for commissioning.
3. Commission the device using one of the following methods:

   **chip-tool (standalone or pre-built):** The pre-built chip-tool instance ships
   with the Matter Hub image. More information on using the Matter Hub is in the
   [Silicon Labs Matter Hub Documentation](https://docs.silabs.com/matter/2.8.1/matter-thread/raspi-img).
   ```shell
   chip-tool pairing ble-wifi 1 <SSID> <PSK> 20202021 3840
   ```

   **Simplicity Connect mobile app:** Scan the QR code shown on the LCD or the URL
   printed to RTT logs on startup or by pressing BTN0. The URL can also be retrieved
   via the Matter shell:
   ```shell
   matterCli> onboardingcodes ble qrcodeurl
   ```
   Example RTT log output:
   ```
   [SVR] Copy/paste the below URL in a browser to see the QR Code:
   [SVR] https://project-chip.github.io/connectedhomeip/qrcode.html?data=MT%3A6FCJ142C00KA0648G00
   ```
   This QR code is only valid for an unprovisioned device, provisioning may change it.

   **Other:** The device can also be provisioned and controlled using the Python controller, Android, or iOS app.

4. Control the thermostat:
   ```shell
   chip-tool thermostat write occupied-cooling-setpoint 2500 1 1
   chip-tool thermostat read occupied-cooling-setpoint 1 1
   ```

**Button and LED reference:**

| Control | Action            | Result                                                          |
|---------|-------------------|-----------------------------------------------------------------|
| BTN0    | Press and release | Start/restart BLE advertisement, print QR code URL to RTT logs |
| BTN0    | Hold 6 s          | Initiate factory reset (release within 6 s to cancel)           |
| LED 0   | Short flash on    | Unprovisioned, waiting for commissioning                        |
| LED 0   | Rapid even flash  | BLE connected, commissioning in progress                        |
| LED 0   | Short flash off   | Provisioned, no full service connectivity                        |
| LED 0   | Solid on          | Fully provisioned with service connectivity                     |

## Troubleshooting

**Device does not advertise over BLE**
- Press BTN0 to restart BLE advertisement.

**Commissioning fails**
- Ensure the Wi-Fi SSID and PSK are correct and the network is reachable.
- Factory reset the device (hold BTN0 for 6 s) and retry.

**LCD or LEDs not working**
- **LCD:** If the board supports an LCD but it is not enabled, install the _Display_
  component under _Silicon Labs Matter > Matter > Platform > Display_. For the QR code
  on the LCD, install the _QR Code_ component under _Silicon Labs Matter > Matter >
  Platform > QR Code_ (Display is installed automatically).
- **LEDs:** If the board supports LEDs but they are not enabled, install `led0` and
  `led1` instances of _Simple LED_ under _Platform > Driver > LED > Simple LED_, then
  install _WSTK LED Support_ under _Silicon Labs Matter > Matter > Platform > WSTK LED Support_.

You can provision and control the Matter device using the python controller, chip-tool (standalone or pre-built), Android, iOS app or the mattertool utility from the Matter Hub package provided by Silicon Labs. The pre-built chip-tool instance ships with the Matter Hub image. More information on using the Matter Hub can be found in the online Matter documentation here: [Silicon Labs Matter Documentation](https://docs.silabs.com/matter/2.9.0/matter-thread/raspi-img)

## Resources

- [Silicon Labs Matter over Wi-Fi Documentation](https://docs.silabs.com/matter/2.8.1/matter-wifi)
- [Matter Hub Setup](https://docs.silabs.com/matter/2.8.1/matter-thread/raspi-img)
- [chip-tool README](https://github.com/project-chip/connectedhomeip/blob/master/examples/chip-tool/README.md)

## Report Bugs & Get Support

You are always encouraged and welcome to report any issues you found to us via [Silicon Labs Community](https://community.silabs.com).
