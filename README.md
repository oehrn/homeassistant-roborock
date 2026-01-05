# Roborock integration for Home Assistant

> ⚠️ **Important notice**  
> This repository contains the **custom component** version of the Roborock integration.  
> For most users, the **Home Assistant Core integration is recommended**.

---

## About this repository

This integration connects your Roborock account to Home Assistant and is intended to work alongside the official Roborock app.

---

## Installation (HACS)

### Network requirements (local)
Home Assistant must be able to:
- receive device broadcasts on **UDP 58866**
- connect to the vacuum on **TCP 58867**

In Docker/VM/VLAN setups, make sure Home Assistant and the vacuum can reach each other on these ports.

### Install steps
1. HACS → Integrations
2. Add this repository as a **custom repository**
3. Search for **Roborock** and install
4. Restart Home Assistant
5. Settings → Devices & Services → Add integration

---

## Setup

During setup you can choose one of these authentication methods:
- **Login with verification code (email)**
- **Login with password**

Then follow the on-screen flow to complete authentication.

---

## Supported features (overview)

- Vacuum entity (start/stop/pause/dock, fan speed)
- Services (zone/segment cleaning, go-to, remote control)
- Map as a Home Assistant **camera entity** (typically named "Map")
- Additional entities (sensors, binary sensors, numbers/selects/switches, time entities)

If your vacuum model has a built-in camera and you want live streaming, that is not provided by this integration itself.
Some users implement this separately via `go2rtc` (see go2rtc docs).

---

## Documentation

- [docs/index.md](docs/index.md)

---

## Credits

- @rovo89 – protocol research
- @PiotrMachowski – map extraction work
