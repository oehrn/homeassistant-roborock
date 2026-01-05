# Installation

This document describes how to install the **Roborock custom component** via HACS.

---

## Prerequisites

- Home Assistant running and reachable
- HACS installed and configured
- Network connectivity between Home Assistant and the Roborock vacuum

---

## Network requirements (local)

For local discovery/control, Home Assistant and the vacuum must be able to communicate on:

- **UDP 58866** — device broadcasts (vacuum → Home Assistant)
- **TCP 58867** — local control channel (Home Assistant ↔ vacuum)

Firewalls, Docker/VM networking, VLANs, or client isolation can block this.

Official documentation (Core integration):
https://www.home-assistant.io/integrations/roborock/

---

## Installation via HACS

1. Open **HACS**
2. Go to **Integrations**
3. Add this repository as a **custom repository**
4. Search for **Roborock**
5. Install the integration
6. Restart Home Assistant

---

## Post-installation

1. Go to **Settings → Devices & Services**
2. Click **Add integration**
3. Search for **Roborock**
4. Continue with [`configuration.md`](configuration.md)

---

## Notes

- This is a **custom component**
- Updates may be infrequent compared to Core
