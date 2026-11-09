# BMW Weather for iDrive 7 MGU

Unofficial weather app for BMW iDrive 7 (MGU), intended to be installed as a source repository through Robert Nisipeanu's MGU Store.

## Target

- BMW G30/G31, model years 2019–2020, B48 petrol (initial target)
- iDrive 7 / MGU
- Romanian interface
- Metric units: °C, km/h, hPa
- Full-screen weather view and home-screen widget
- Open-Meteo forecast API
- Cached forecast for temporary network loss

## MGU Store

This repository uses the MGU Store repo-tree format. The root `mgu-repo.json` discovers apps under `apps/*`. The head unit builds the app from source using the pinned upstream iDrive 7 app kit and its own BMW SDK donor. The BMW SDK is deliberately not included here.

## Build notes

The MGU Store build runs on the head unit. `tools/build_unit.py` downloads a pinned revision of the public `idrive7-apps` build kit, overlays this app's source, and invokes the kit's standard builder. The build requires the MGU Store build sandbox's network permission and the SDK donor it supplies.

## Location

GPS access on this MGU firmware has not yet been verified. The app therefore includes a manual-coordinate fallback and does not pretend that GPS is available. A GPS provider can be enabled after the relevant MGU interface is confirmed.

## Disclaimer

Unofficial community software; not affiliated with or endorsed by BMW AG. Use and install at your own risk. Configure and test the app while parked.
