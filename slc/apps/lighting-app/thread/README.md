# Matter EFR32 Lighting Example (Thread)

The EFR32 Lighting example provides a baseline demonstration of a lighting
device (On/Off, Level, Color), built using Matter and the Silicon Labs
Simplicity SDK. It can be commissioned by a Matter controller over a
Thread network (commissioning over BLE + Thread provisioning).

If an LCD is enabled, the WSTK LCD shows a QR Code containing the
commissioning information. Scan it with a Matter controller application
(`chip-tool`, Android, iOS, Matter Hub, etc.) to start commissioning.

For general information and prerequisites see the online Silicon Labs
Matter documentation: https://docs.silabs.com/matter (Thread demo guide).

## User Interface

**LED 0** – Shows overall device / network state:

* Short Flash On (50 ms on / 950 ms off): Unprovisioned, waiting for commissioning
* Rapid Even Flash (100 ms on / 100 ms off): Unprovisioned, BLE connection active
* Short Flash Off (950 ms on / 50 ms off): Provisioned, not fully connected
* Solid On: Fully provisioned and Thread + service connectivity established

**LED 1** – Simulated light state (On = solid, Off = off) when configured.

**Push Button 0**
* Press & Release: Start / restart BLE advertising (fast for 30 s then slow; stops after 15 min). Prints QR Code URL to RTT.
* Hold 6 s: Factory reset (LEDs blink together while pending; release before timeout to cancel).

**Push Button 1** (if present) – Toggles the light (On/Off) and updates clusters.

## Enabling LCD / LEDs

If not already present in the project:
* Install **QR Code** component (installs LCD dependency automatically)
* Install **Simple LED** (instances led0 / led1) and **WSTK LED Support** components

## Provision & Control

Example `chip-tool` commissioning over Thread (replace `<operationalDataset>`):

```shell
chip-tool pairing ble-thread 1 hex:<operationalDataset> 20202021 3840
```

Sample cluster commands:

```shell
chip-tool onoff on 1 1
chip-tool levelcontrol move-to-level 128 0 0 0 1 1
chip-tool colorcontrol move-to-hue-and-saturation 120 180 0 0 1 1
```

## Files

This folder contains unified Thread solution / project artifacts:

* `lighting-app-series-2.slcw` – Series 2 bootloader + app solution
* `lighting-app-series-2-internal.slcw` – Series 2 internal flash bootloader + app
* `lighting-app-series-3.slcw` – Series 3 bootloader + app solution
* `lighting-app.slcp` – Application project (copied from `sample-app` pending full merge)
* `pkg.slt` – Package version lock

## Notes

The `.slcw` solution files still reference the original `sample-app` project
path. The duplicated `lighting-app.slcp` is added here to support the
ongoing merge of `sample-app` and `solutions`. Future cleanup will retarget
the solution entries to the local `.slcp` and remove legacy locations.
