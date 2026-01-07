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
