# Troubleshooting

This document covers common issues and limitations of the **Roborock custom component** for Home Assistant.

For official documentation and the maintained integration, refer to the Home Assistant **Core** Roborock integration.

---

## Scope and expectations

This repository contains a **custom component**.
Maintainers have stated that most ongoing work happens in the Core integration and updates here may be limited.

If you rely on fast fixes, new device support, or official support, switching to Core is usually the right move.

---

## Integration does not load or setup fails

### Checks
- Restart Home Assistant after installation
- Check logs for `roborock` errors:
  - Settings → System → Logs

If it previously worked and broke after an update, switching to the Core integration may be the fastest way back to a stable state.

---

## Login issues (code/password)

### Symptoms
- verification email does not arrive
- verification code is rejected
- password login fails

### Notes
- email delivery delays can occur
- repeated rapid retries can make debugging harder

### Recommendations
- try the other auth method (code vs password) if available
- request a new verification code if using the code flow
- confirm you are using the same account as in the Roborock app

---

## Local communication issues (UDP 58866 / TCP 58867)

Local discovery/control requires:
- **UDP 58866** — device broadcasts (vacuum → Home Assistant)
- **TCP 58867** — local control channel (Home Assistant ↔ vacuum)

### Common causes
- firewall rules blocking traffic
- Home Assistant in Docker/VM without correct networking
- VLAN/client isolation between Home Assistant and the vacuum

### Recommendations
- ensure Home Assistant and the vacuum can reach each other on UDP 58866 and TCP 58867
- try placing both on the same network segment for testing
- if local networking is not possible, enable **Use cloud integration** in the integration options

---

## Map issues

- Maps may fail to update if the device is unreachable or map data is unavailable.
- Historical data completeness depends on what the device/account exposes.

---

## Getting help / filing issues

When opening an issue, include:
- Home Assistant version
- integration version
- vacuum model
- relevant logs (with debug logging enabled)
