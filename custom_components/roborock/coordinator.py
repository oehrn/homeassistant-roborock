"""Coordinatory for Roborock devices."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from roborock.version_1_apis import RoborockClientV1 as RoborockClient
from roborock.version_1_apis import RoborockMqttClientV1 as RoborockMqttClient
from roborock.version_1_apis import RoborockLocalClientV1 as RoborockLocalClient
from roborock.containers import HomeDataRoom, MultiMapsList, RoborockBase
from roborock.exceptions import RoborockException

from .const import DOMAIN
from .roborock_typing import RoborockHassDeviceInfo

SCAN_INTERVAL = timedelta(seconds=30)
WASHING_MACHINE_SCAN_INTERVAL = timedelta(seconds=60)

_LOGGER = logging.getLogger(__name__)


class RoborockDataUpdateCoordinator(DataUpdateCoordinator[RoborockHassDeviceInfo]):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: RoborockClient,
        map_client: RoborockMqttClient,
        device_info: RoborockHassDeviceInfo,
        rooms: list[HomeDataRoom],
    ) -> None:
        """Initialize."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.api = client
        self.map_api = map_client
        self.devices_maps: dict[str, MultiMapsList] = {}
        self.device_info = device_info
        self.rooms = rooms
        self.scheduled_refresh: asyncio.TimerHandle | None = None

    def schedule_refresh(self) -> None:
        """Schedule coordinator refresh after 1 second."""
        if self.scheduled_refresh:
            self.scheduled_refresh.cancel()
        self.scheduled_refresh = self.hass.loop.call_later(
            1, lambda: asyncio.create_task(self.async_refresh())
        )

    async def async_release(self) -> None:
        """Disconnect from API."""
        if self.scheduled_refresh:
            self.scheduled_refresh.cancel()
        await self.api.async_disconnect()
        if self.api != self.map_api:
            try:
                await self.map_api.async_disconnect()
            except RoborockException:
                _LOGGER.warning("Failed to disconnect from map api")

    async def fill_device_prop(self, device_info: RoborockHassDeviceInfo) -> None:
        """Get device properties."""
        device_prop = await self.api.get_prop()
        if device_prop:
            if device_info.props:
                device_info.props.update(device_prop)
            else:
                device_info.props = device_prop

    def update_device(self, device_id: str, attribute: str, data: RoborockBase):
        """Update device based on prop attribute."""
        if device_id == self.device_info.device.duid:
            setattr(self.device_info.props, attribute, data)
            self.hass.loop.call_soon_threadsafe(
                self.async_set_updated_data, self.device_info
            )

    async def fill_room_mapping(self, device_info: RoborockHassDeviceInfo) -> None:
        """Build the room mapping - only works for local api."""
        if not isinstance(self.api, RoborockLocalClient):
            return
        if device_info.room_mapping is None:
            room_mapping = await self.api.get_room_mapping()
            if room_mapping:
                room_iot_name = {str(room.id): room.name for room in self.rooms}
                device_info.room_mapping = {
                    rm.segment_id: room_iot_name.get(str(rm.iot_id))
                    for rm in room_mapping
                }

    async def fill_device_multi_maps_list(
        self, device_info: RoborockHassDeviceInfo
    ) -> None:
        """Get multi maps list."""
        if not isinstance(self.api, RoborockLocalClient):
            return
        if device_info.map_mapping is None:
            multi_maps_list = await self.api.get_multi_maps_list()
            if multi_maps_list:
                map_mapping = {
                    map_info.mapFlag: map_info.name
                    for map_info in multi_maps_list.map_info
                }
                device_info.map_mapping = map_mapping

    async def fill_device_info(self, device_info: RoborockHassDeviceInfo):
        """Merge device information."""
        await asyncio.gather(
            *(
                [
                    self.fill_device_prop(device_info),
                    asyncio.gather(
                        *(
                            [
                                self.fill_device_multi_maps_list(device_info),
                                self.fill_room_mapping(device_info),
                            ]
                        ),
                        return_exceptions=True,
                    ),
                ]
            )
        )

    async def _async_update_data(self) -> RoborockHassDeviceInfo:
        """Update data via library."""
        try:
            await self.fill_device_info(self.device_info)
        except RoborockException as ex:
            raise UpdateFailed(ex) from ex
        return self.device_info


class RoborockWashingMachineCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for Roborock washing machines (Zeo devices)."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: RoborockMqttClient,
        device_info: RoborockHassDeviceInfo,
    ) -> None:
        """Initialize washing machine coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_washing_machine",
            update_interval=WASHING_MACHINE_SCAN_INTERVAL,
        )
        self.api = client
        self.device_info = device_info
        self.scheduled_refresh: asyncio.TimerHandle | None = None

    def schedule_refresh(self) -> None:
        """Schedule coordinator refresh after 1 second."""
        if self.scheduled_refresh:
            self.scheduled_refresh.cancel()
        self.scheduled_refresh = self.hass.loop.call_later(
            1, lambda: asyncio.create_task(self.async_refresh())
        )

    async def async_release(self) -> None:
        """Disconnect from API."""
        if self.scheduled_refresh:
            self.scheduled_refresh.cancel()
        try:
            await self.api.async_disconnect()
        except RoborockException:
            _LOGGER.warning("Failed to disconnect from washing machine api")

    async def _async_update_data(self) -> dict[str, Any]:
        """Update washing machine data."""
        data = {
            "device": self.device_info.device,
            "online": self.device_info.device.online,
            "name": self.device_info.device.name,
        }
        
        # Try to get status data from washing machine
        try:
            # Get all properties from washing machine
            # This should return a list of values corresponding to the schema
            prop_result = await self.api.send_command("get_prop", [])
            
            if prop_result:
                _LOGGER.debug("Zeo One data: %s", prop_result)
                
                # Map the result to our data dictionary
                # Based on Zeo One schema order
                if isinstance(prop_result, list) and len(prop_result) > 0:
                    # Try to parse the response
                    # Schema IDs: 203=status, 204=mode, 205=program, 207=temp, 
                    # 208=rinse_times, 209=spin_level, 210=drying_mode,
                    # 217=countdown, 218=washing_left, 219=door_lock, 220=error
                    
                    # Since we don't know exact order, try to get specific props
                    try:
                        status_result = await self.api.send_command("get_prop", ["status"])
                        if status_result:
                            data["status"] = status_result[0] if isinstance(status_result, list) else status_result
                    except Exception:
                        pass
                    
                    try:
                        washing_left = await self.api.send_command("get_prop", ["washing_left"])
                        if washing_left:
                            data["washing_left"] = washing_left[0] if isinstance(washing_left, list) else washing_left
                    except Exception:
                        pass
                    
                    try:
                        countdown = await self.api.send_command("get_prop", ["countdown"])
                        if countdown:
                            data["countdown"] = countdown[0] if isinstance(countdown, list) else countdown
                    except Exception:
                        pass
                    
                    try:
                        error = await self.api.send_command("get_prop", ["error"])
                        if error:
                            data["error"] = error[0] if isinstance(error, list) else error
                    except Exception:
                        pass
                    
                    # Get other properties
                    for prop_name in ["mode", "program", "temp", "rinse_times", 
                                     "spin_level", "drying_mode", "doorlock_state"]:
                        try:
                            result = await self.api.send_command("get_prop", [prop_name])
                            if result:
                                key = "door_lock" if prop_name == "doorlock_state" else prop_name
                                if prop_name == "temp":
                                    key = "temperature"
                                data[key] = result[0] if isinstance(result, list) else result
                        except Exception:
                            pass
                    
                    # Get switch states
                    for switch_name in ["child_lock", "detergent_set", "softener_set"]:
                        try:
                            result = await self.api.send_command("get_prop", [switch_name])
                            if result:
                                key = switch_name
                                if switch_name == "detergent_set":
                                    key = "auto_detergent"
                                elif switch_name == "softener_set":
                                    key = "auto_softener"
                                data[key] = result[0] if isinstance(result, list) else result
                        except Exception:
                            pass
                            
        except RoborockException as ex:
            _LOGGER.debug("Failed to get washing machine status: %s", ex)
        
        return data
