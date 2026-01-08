"""Support for Roborock washing machine switches."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RoborockWashingMachineCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass
class WashingMachineSwitchDescription(SwitchEntityDescription):
    """Class describing washing machine switch entities."""

    is_on_fn: callable = None
    turn_on_cmd: str = None
    turn_off_cmd: str = None


WASHING_MACHINE_SWITCHES = [
    WashingMachineSwitchDescription(
        key="child_lock",
        name="Child Lock",
        translation_key="child_lock",
        icon="mdi:lock",
        entity_category=EntityCategory.CONFIG,
        is_on_fn=lambda data: data.get("child_lock", False),
        turn_on_cmd="set_child_lock",
        turn_off_cmd="set_child_lock",
    ),
    WashingMachineSwitchDescription(
        key="auto_detergent",
        name="Auto Detergent",
        translation_key="auto_detergent",
        icon="mdi:bottle-tonic-plus",
        entity_category=EntityCategory.CONFIG,
        is_on_fn=lambda data: data.get("auto_detergent", False),
        turn_on_cmd="set_auto_detergent",
        turn_off_cmd="set_auto_detergent",
    ),
    WashingMachineSwitchDescription(
        key="auto_softener",
        name="Auto Softener",
        translation_key="auto_softener",
        icon="mdi:bottle-tonic-plus-outline",
        entity_category=EntityCategory.CONFIG,
        is_on_fn=lambda data: data.get("auto_softener", False),
        turn_on_cmd="set_auto_softener",
        turn_off_cmd="set_auto_softener",
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Roborock washing machine switches."""
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
        for description in WASHING_MACHINE_SWITCHES:
            entities.append(
                RoborockWashingMachineSwitch(coordinator, description)
            )
    
    async_add_entities(entities)


class RoborockWashingMachineSwitch(
    CoordinatorEntity[RoborockWashingMachineCoordinator], SwitchEntity
):
    """Roborock washing machine switch."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RoborockWashingMachineCoordinator,
        description: WashingMachineSwitchDescription,
    ) -> None:
        """Initialize the switch."""
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
        if self.entity_description.is_on_fn and self.coordinator.data:
            self._attr_is_on = self.entity_description.is_on_fn(
                self.coordinator.data
            )
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        if self.entity_description.is_on_fn and self.coordinator.data:
            return self.entity_description.is_on_fn(self.coordinator.data)
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        if self.entity_description.turn_on_cmd:
            try:
                await self.coordinator.api.send_command(
                    self.entity_description.turn_on_cmd, [1]
                )
                await self.coordinator.async_request_refresh()
            except Exception as ex:
                _LOGGER.error("Failed to turn on %s: %s", self.name, ex)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        if self.entity_description.turn_off_cmd:
            try:
                await self.coordinator.api.send_command(
                    self.entity_description.turn_off_cmd, [0]
                )
                await self.coordinator.async_request_refresh()
            except Exception as ex:
                _LOGGER.error("Failed to turn off %s: %s", self.name, ex)
