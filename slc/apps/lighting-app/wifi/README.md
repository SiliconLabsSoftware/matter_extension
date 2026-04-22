# Matter SiWx917 SoC Lighting Example

The SiWx917 SoC lighting example provides a baseline demonstration of a Light control
device, built using Matter and the Silicon Labs simplicity SDK. It can be controlled
by a Matter controller over Wifi network.

The SiWx917 device can be commissioned over Bluetooth Low Energy where the device
and the Matter controller will exchange security information with the Rendez-vous
procedure.

If the LCD is enabled, the LCD on the Silabs WSTK shows a QR Code containing the
needed commissioning information for the BLE connection and starting the
Rendez-vous procedure.

The lighting example is intended to serve both as a means to explore the
workings of Matter as well as a template for creating real products based on the
Silicon Labs platform.

For more general information on running matter applications and pre-requisites please look at online 
documentation for Matter available on docs.silabs.com. Follow Wi-Fi instructions depending on the example you are running.
[Demo instructions for Wi-Fi](https://docs.silabs.com/matter/2.8.1/matter-wifi)

## Region code Setting (917 WiFi projects)

In Wifi configurations, the region code can be set in this
[file](https://github.com/SiliconLabsSoftware/matter_sdk/blob/v2.8.1/src/platform/silabs/wifi/SiWx/WifiInterfaceImpl.cpp).
Search for `REGION_CODE` (build-time default) or `region_code` in the Wi-Fi configuration struct.

The available region codes are defined by the `sl_wifi_region_code_t` enum in
[sl_wifi_constants.h](https://github.com/SiliconLabs/wiseconnect/blob/v4.0.1-content-for-docs/components/protocol/wifi/inc/sl_wifi_constants.h).
Search for `sl_wifi_region_code_t` or the `SL_WIFI_REGION_` enumerator names.

## Lighting Example User Interface

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

Shows the overall state of the device and its connectivity. The following states are possible:

-   _Short Flash On (50 ms on/950 ms off)_ ; The device is in the unprovisioned (unpaired) state and is waiting for a commissioning application to connect.

-   _Rapid Even Flashing_ ; (100 ms on/100 ms off)_ &mdash; The device is in the unprovisioned state and a commissioning application is connected through Bluetooth LE.

-   _Short Flash Off_ ; (950ms on/50ms off)_ &mdash; The device is fully
provisioned, but does not yet have full service
connectivity.

-   _Solid On_ ; The device is fully provisioned and has full service connectivity.

**LED 1** 

Simulates the Light The following states are possible:

-   _Solid On_ ; Light is on
-   _Off_ ; Light is off

    
**Push Button 0**

-   _Press and Release_ : Start, or restart, BLE advertisement in fast mode. It will advertise in this mode
for 30 seconds. The device will then switch to a slower interval advertisement.
After 15 minutes, the advertisement stops. In addition, this button should also print the QR Code URL to the RTT logs.

-   _Pressed and hold for 6 s_ : Initiates the factory reset of the device.
 Releasing the button within the 6-second window cancels the factory reset
 procedure. **LEDs** blink in unison when the factory reset procedure is
 initiated.

**Push Button 1** 

- Toggles the light state On/Off

## Extending Base App Implementation

### CustomerAppTask

To implement custom app behavior you can override any Silicon Labs implemented API in the CustomerAppTask file. This example provides `CustomerAppTask.h` and `CustomerAppTask.cpp` for that purpose. The base implementation and the full set of overridable `*Impl()` APIs are supplied by the build system in `AppTask.cpp` and `AppTaskImpl.h` under `autogen/`. Any `*Impl()` you do not override keeps the Silicon Labs default behavior.

### How to Override APIs

`CustomerAppTask` extends the base AppTask through the Curiously Recurring Template Pattern (CRTP). You override only the `*Impl()` methods you need, the base declares one `*Impl()` per overridable API. Steps:

1. Find the method to override in the base API (see [Override API reference](#override-api-reference) below).
2. Declare the same method signature in `CustomerAppTask` in your `CustomerAppTask.h` under `private:`
3. Implement the method in `CustomerAppTask.cpp`.
4. Build the project. Each overridable API is resolved as follows: **if you implemented that `*Impl()` in CustomerAppTask, your implementation is used, otherwise the Silicon Labs default implementation is used.** You only implement what you need, everything else falls back to the default automatically.

### DataModelCallbacks and CustomerAppTask

What used to live in `DataModelCallbacks.cpp` is now in the autogenerated
`AppTask.cpp` under `autogen/` (see [CustomerAppTask](#CustomerAppTask) above). That
file is regenerated; do not use it for custom application logic.

`MatterPostAttributeChangeCallback` is implemented in `examples/platform/silabs/BaseApplication.cpp`. The function logic is defined under `DMPostAttributeChangeCallback` under `AppTask.cpp`

Forwarding into `AppTask` still goes through CRTP as in [How to Override
APIs](#how-to-override-apis).

- **Methods that already exist in the autogenerated layer** — Customize them by
  overriding the matching `*Impl()` method in `CustomerAppTask`. Do not edit the
  autogenerated `AppTask.cpp` for app-specific behavior.

- **New custom data model methods** — Add them in `CustomerAppTask` directly. Do
  not add new application logic in autogenerated sources; those edits will not
  survive regeneration or project upgrades.

### Sample Implementation

The following shows a minimal example `CustomerAppTask` that overrides `AppInitImpl()` (required) and `ButtonEventHandlerImpl()`.

**CustomerAppTask.h**

```cpp
#pragma once
#include "AppTaskImpl.h"

/**
 * Minimal AppTaskImpl-derived class. Override only the *Impl() methods you need;
 * add AppInitImpl(), GetAppTask(), and sAppTask as required by the CRTP base.
 */
class CustomerAppTask : public AppTaskImpl<CustomerAppTask>
{
public:
    static CustomerAppTask & GetAppTask() { return sAppTask; }

private:
    friend class AppTaskImpl<CustomerAppTask>;
    CHIP_ERROR AppInitImpl();
    void ButtonEventHandlerImpl(uint8_t button, uint8_t btnAction);
    static CustomerAppTask sAppTask;
};
```

**CustomerAppTask.cpp**

```cpp
#include "CustomerAppTask.h"
#include "AppTask.h"
#include "AppConfig.h"
#include "AppEvent.h"
#include <platform/CHIPDeviceLayer.h>
#include <platform/silabs/platformAbstraction/SilabsPlatform.h>
#include <platform/silabs/tracing/SilabsTracingMacros.h>

using namespace ::chip::DeviceLayer::Silabs;

#define APP_FUNCTION_BUTTON 0
#define APP_LIGHT_SWITCH     1

CustomerAppTask CustomerAppTask::sAppTask;

AppTask & AppTask::GetAppTask()
{
    return CustomerAppTask::GetAppTask();
}

CHIP_ERROR CustomerAppTask::AppInitImpl()
{
    SILABS_LOG("CustomerAppTask: custom implementation (AppInitImpl)");
    CHIP_ERROR err = this->AppTask::AppInit();
    if (err == CHIP_NO_ERROR)
    {
        // Override the SDK default button handler registered in AppTask::AppInit().
        chip::DeviceLayer::Silabs::GetPlatform().SetButtonsCb(CustomerAppTask::ButtonEventHandler);
    }
    return err;
}

// override code goes here
void CustomerAppTask::ButtonEventHandlerImpl(uint8_t button, uint8_t btnAction)
{
    AppEvent button_event           = {};
    button_event.Type               = AppEvent::kEventType_Button;
    button_event.ButtonEvent.Action = btnAction;
    if (button == APP_LIGHT_SWITCH && btnAction == static_cast<uint8_t>(SilabsPlatform::ButtonAction::ButtonPressed))
    {
        button_event.Handler = LightActionEventHandler;
        AppTask::GetAppTask().PostEvent(&button_event);
    }
    else if (button == APP_FUNCTION_BUTTON)
    {
        button_event.Handler = BaseApplication::ButtonHandler;
        AppTask::GetAppTask().PostEvent(&button_event);
    }
}
```

### Override API Reference

The base API and implementation are generated into your project and live under `autogen/` directory. These files are regenerated on every project upgrade and match your installed SDK version. Use them as the reference for overridable methods and app configuration.

| File | Purpose |
|------|--------|
| `autogen/AppTaskImpl.h` | Declarations of every overridable `*Impl()` method. Copy the signatures you need from here into `CustomerAppTask.h`. |
| `autogen/AppTask.cpp` | Silicon Labs default implementation of AppTask. This is what runs for any `*Impl()` you do not override. Use as reference when customizing behavior. |

## Provision and Control

You can provision and control the Matter device using the python controller, chip-tool (standalone or pre-built), Android, iOS app or the mattertool utility from the Matter Hub package provided by Silicon Labs. The pre-built chip-tool instance ships with the Matter Hub image. More information on using the Matter Hub can be found in the online Matter documentation here: [Silicon Labs Matter Documentation](https://docs.silabs.com/matter/2.8.1/matter-thread/raspi-img)

    
More information on using the chip-tool directly can be found here: [CHIPTool](https://github.com/project-chip/connectedhomeip/blob/master/examples/chip-tool/README.md)


Here is an example with the CHIPTool:

```shell
chip-tool pairing ble-wifi <Node-ID> $SSID $PSK 20202021 3840

chip-tool onoff on <Node-ID> 1
```