# Matter SiWx917 SoC Light Switch Example

The SiWx917 SoC light switch example provides a baseline demonstration of a on-off
light switch device, built using Matter and the Silicon Labs simplicity SDK. It can
be controlled by a Matter controller over Wifi network.

The SiWx917 SoC device can be commissioned over Bluetooth Low Energy where the device
and the Matter controller will exchange security information with the Rendez-vous
procedure.

If the LCD is enabled, the LCD on the Silabs WSTK shows a QR Code containing the
needed commissioning information for the BLE connection and starting the
Rendez-vous procedure.

The light switch example is intended to serve both as a means to explore the
workings of Matter as well as a template for creating real products based on the
Silicon Labs platform. **This example is defaulted to use full ICD functionality
out-of-the-box and therefore has the matter_icd_management component enabled.**

For more general information on running matter applications and pre-requisites please look at online 
documentation for Matter available on docs.silabs.com. Follow Wi-Fi instructions depending on the example you are running.
[Demo instructions for Wi-Fi](https://docs.silabs.com/matter/2.6.0/matter-wifi)

## Region code Setting (917 WiFi projects)

In Wifi configurations, the region code can be set in this
[file](https://github.com/SiliconLabsSoftware/matter_sdk/blob/085bd03532990e5b1f99ff4b08ebce4f4ca5edf6/src/platform/silabs/wifi/SiWx/WifiInterface.cpp#L125).
The available region codes can be found
[here](https://github.com/SiliconLabs/wiseconnect/blob/f675628eefa1ac4990e94146abb75dd08b522571/components/device/silabs/si91x/wireless/inc/sl_si91x_types.h#L71)

## Light Switch Specific Interface

**LCD** 

The LCD on Silabs WSTK shows a QR Code. This QR Code is be scanned by the CHIP Tool app For the Rendez-vous procedure over BLE.

![QR Code](qr_code_img.png)

A URL can be found in the **RTT logs upon startup OR by pressing BTN0**

**The URL can also be printed by issuing the following matter shell command:**

```shell
matterCli> onboardingcodes ble qrcodeurl
```

Log output example:

```shell
[SVR] Copy/paste the below URL in a browser to see the QR Code:
[SVR] https://project-chip.github.io/connectedhomeip/qrcode.html?data=MT%3A6FCJ142C00KA0648G00
```

Note: This QR Code is only valid for an unprovisioned device. Provisioning may change the QR Code.

**LED 0** 

Led 0 shows the overall state of the device and its connectivity. The
following states are possible:

-   Short Flash On (50 ms on/950 ms off): The device is in the
unprovisioned (unpaired) state and is waiting for a commissioning
application to connect.

-   Rapid Even Flashing (100 ms on/100 ms off): The device is in the
    unprovisioned state and a commissioning application is connected through Bluetooth LE.

-   Short Flash Off (950ms on/50ms off): The device is fully provisioned, but does not yet have full service connectivity.

-   Solid On: The device is fully provisioned and has full service connectivity.

**Push Button 0**

-   _Press and Release_ : Start, or restart, BLE advertisement in fast mode. It will advertise in this mode
for 30 seconds. The device will then switch to a slower interval advertisement.
After 15 minutes, the advertisement stops. In addition, this button should also print the QR Code URL to the RTT logs.

-   _Pressed and hold for 6 s_ : Initiates the factory reset of the device. Releasing the button within the 6-second window cancels the factory reset procedure. **LEDs** blink in unison when the factory reset procedure is initiated.

**Push Button 1**

-   Sends a Toggle command to bound light app

**Matter shell**

**_OnOff Cluster_**

-  'switch onoff on'            : Sends unicast On command to bound device
-  'switch onoff off'           : Sends unicast Off command to bound device
-  'switch onoff toggle'        : Sends unicast Toggle command to bound device

-  'switch groups onoff on'     : Sends On group command to bound group
-  'switch groups onoff off'    : Sends On group command to bound group
-  'switch groups onoff toggle' : Sends On group command to bound group

**_Binding Cluster_**

- 'switch binding unicast  [*fabric index*] [*node id*] [*endpoint*]' : Creates a unicast binding
- 'switch binding group [*fabric index*] [*group id*]'              : Creates a group binding
