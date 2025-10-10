# Matter SiWx917 SoC Lighting Example (Wi-Fi)

The SiWx917 SoC Lighting example provides a baseline demonstration of a lighting
device (On/Off, Level, Color), built using Matter and the Silicon Labs
Simplicity SDK. It can be controlled by a Matter controller over a Wi-Fi
network. Commissioning occurs over BLE after which the Wi-Fi credentials are
provisioned.

For general information and prerequisites see the online Silicon Labs Matter
documentation: https://docs.silabs.com/matter (Wi-Fi demo guide).

## Region Code (917 Wi-Fi Projects)

Set the region code in the Wi-Fi interface source (see SiWx917 platform
documentation). Acceptable region codes are defined in the SiWx917 SDK header
`sl_si91x_types.h`.

## User Interface

**LED 0** – Device / network state (see Thread README for patterns).

**LED 1** – Simulated light state (On / Off).

**Button 0** – Start / restart BLE advertising (fast 30 s -> slow, stops after 15 min) and prints QR URL.

**Button 1** – Toggle light state.

Factory reset: Hold Button 0 for 6 seconds (LEDs blink while pending).

## Provision & Control

Commissioning over BLE + Wi-Fi using `chip-tool`:

```shell
chip-tool pairing ble-wifi 1 <SSID> <PSK> 20202021 3840
```

Control examples:

```shell
chip-tool onoff on 1 1
chip-tool levelcontrol move-to-level 64 0 0 0 1 1
chip-tool colorcontrol move-to-hue-and-saturation 100 200 0 0 1 1
```

## Files

* `lighting-app-917-soc.slcw` – SiWx917 SoC solution
* `lighting-app-917-soc.slcp` – Application project (duplicate for merge)
* `pkg.slt` – Package version lock

## Notes

As with the Thread variant, the solution file still references the original
`sample-app` project path pending full migration.
