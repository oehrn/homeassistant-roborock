"""Support for Roborock washing machine sensors."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RoborockWashingMachineCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class WashingMachineSensorDescription(SensorEntityDescription):
    """Class describing washing machine sensor entities."""

    value_fn: callable = None


WASHING_MACHINE_SENSORS = [
    WashingMachineSensorDescription(
        key="online",
        name="Online Status",
        translation_key="online_status",
        device_class=SensorDeviceClass.ENUM,
        options=["online", "offline"],
        value_fn=lambda data: "online" if data.get("online") else "offline",
    ),
    WashingMachineSensorDescription(
        key="name",
        name="Device Name",
        translation_key="device_name",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("name"),
    ),
    WashingMachineSensorDescription(
        key="status",
        name="Status",
        translation_key="washing_status",
        device_class=SensorDeviceClass.ENUM,
        options=["idle", "running", "paused", "error"],
        value_fn=lambda data: data.get("status", "unknown"),
    ),
    WashingMachineSensorDescription(
        key="washing_left",
        name="Time Remaining",
        translation_key="washing_left",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        value_fn=lambda data: data.get("washing_left"),
    ),
    WashingMachineSensorDescription(
        key="countdown",
        name="Countdown",
        translation_key="countdown",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("countdown"),
    ),
    WashingMachineSensorDescription(
        key="error",
        name="Error Code",
        translation_key="error_code",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("error", 0),
    ),
    WashingMachineSensorDescription(
        key="mode",
        name="Mode",
        translation_key="mode",
        value_fn=lambda data: data.get("mode"),
    ),
    WashingMachineSensorDescription(
        key="program",
        name="Program",
        translation_key="program",
        value_fn=lambda data: data.get("program"),
    ),
    WashingMachineSensorDescription(
        key="temperature",
        name="Temperature",
        translation_key="temperature",
        icon="mdi:thermometer",
        value_fn=lambda data: data.get("temperature"),
    ),
    WashingMachineSensorDescription(
        key="rinse_times",
        name="Rinse Times",
        translation_key="rinse_times",
        icon="mdi:water-sync",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("rinse_times"),
    ),
    WashingMachineSensorDescription(
        key="spin_level",
        name="Spin Level",
        translation_key="spin_level",
        icon="mdi:sync",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("spin_level"),
    ),
    WashingMachineSensorDescription(
        key="drying_mode",
        name="Drying Mode",
        translation_key="drying_mode",
        icon="mdi:tumble-dryer",
        value_fn=lambda data: data.get("drying_mode"),
    ),
    WashingMachineSensorDescription(
        key="door_lock",
        name="Door Lock",
        translation_key="door_lock",
        device_class=SensorDeviceClass.ENUM,
        options=["locked", "unlocked"],
        icon="mdi:lock",
        value_fn=lambda data: "locked" if data.get("door_lock") else "unlocked",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Roborock washing machine sensors."""
    from .domain import EntryData

    entry_data: EntryData = hass.data[DOMAIN][entry.entry_id]
    coordinators = []
    
    for device_id, device_entry_data in entry_data["devices"].items():
        coordinator = device_entry_data["coordinator"]
        if isinstance(coordinator, RoborockWashingMachineCoordinator):
            coordinators.append(coordinator)
    
    if not coordinators:
        return
    
    entities = []
    for coordinator in coordinators:
        for description in WASHING_MACHINE_SENSORS:
            entities.append(
                RoborockWashingMachineSensor(coordinator, description)
            )
    
    async_add_entities(entities)


class RoborockWashingMachineSensor(
    CoordinatorEntity[RoborockWashingMachineCoordinator], SensorEntity
):
    """Roborock washing machine sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RoborockWashingMachineCoordinator,
        description: WashingMachineSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = (
            f"{coordinator.device_info.device.duid}_{description.key}"
        )
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_info.device.duid)},
            "name": coordinator.device_info.device.name,
            "manufacturer": "Roborock",
            "model": coordinator.device_info.model,
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.entity_description.value_fn and self.coordinator.data:
            self._attr_native_value = self.entity_description.value_fn(
                self.coordinator.data
            )
        self.async_write_ha_state()

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.entity_description.value_fn and self.coordinator.data:
            return self.entity_description.value_fn(self.coordinator.data)
        return None
