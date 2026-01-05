# Features

This page describes the main features exposed by this **custom component**.

> The exact set of entities can vary by device model/firmware and what the underlying library reports as supported.

---

## Platforms / entity types

The integration can expose multiple entity platforms, including:
- **Vacuum**
- **Camera** (map image)
- **Sensor** / **Binary sensor**
- **Number**, **Select**, **Switch**
- **Time** (e.g., timers like DnD start/end when supported)
- **Button**

---

## Vacuum control

The vacuum entity supports standard Home Assistant vacuum actions such as:
- start / stop / pause
- return to dock
- locate
- fan speed control (when supported by the device status)

---

## Services

The integration registers additional services (see `custom_components/roborock/services.yaml`), including:

- `vacuum_remote_control_start`
- `vacuum_remote_control_stop`
- `vacuum_remote_control_move`
- `vacuum_remote_control_move_step`
- `vacuum_clean_zone`
- `vacuum_clean_segment`
- `vacuum_goto`
- `vacuum_load_multi_map`

---

## Map (camera entity)

A map is exposed as a Home Assistant **camera entity** (typically named **"Map"**).
It provides a rendered image plus map-related attributes when available (e.g., zones, paths, rooms).

This is **not** live video streaming from a built-in camera; it is a map image.

---

## Sensors and status

Commonly exposed sensor/binary-sensor categories include:
- battery and cleaning statistics
- consumables/maintenance counters (brushes, filter, etc.)
- attachments/status flags (e.g., mop/water box) when supported

---

## Built-in vacuum camera streaming (separate)

If your vacuum model has a built-in camera and you want streaming, this integration does not implement that directly.
Some users implement streaming separately via tools like `go2rtc` (see go2rtc documentation).
