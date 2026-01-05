# Configuration

This document describes configuration of the Roborock **custom component** after installation.

---

## Account authentication

During setup, you authenticate with the same account you use in the official Roborock app.

The config flow offers two authentication methods:
- **Login with verification code (email)**
- **Login with password**

### Verification code (email) flow
1. Add the Roborock integration in Home Assistant
2. Choose **Login with verification code**
3. Enter your Roborock account username (email)
4. A verification code is sent via email
5. Enter the code to complete setup

### Password flow
1. Add the Roborock integration in Home Assistant
2. Choose **Login with password**
3. Enter your Roborock account username (email)
4. Enter your password to complete setup

---

## Device discovery

After successful authentication, devices associated with the account are discovered and added.

In many networks, no manual device configuration is required.

If local discovery/reachability fails, the integration may guide you through additional steps (depending on your setup and what the integration detects).

---

## Local vs cloud communication

By default the integration prefers **local polling** where possible.
If local reachability fails, behavior may fall back to cloud/MQTT depending on the operation and settings.

Local communication depends on proper network access (see `installation.md`).

---

## Notes

- The set of available entities/options can vary by device model and firmware
- Feature parity with the Core integration is not guaranteed
