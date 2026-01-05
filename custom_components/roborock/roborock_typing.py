"""Typing for Roborock integration."""

from dataclasses import dataclass
from typing import TypedDict

from roborock import DeviceData, DeviceProp


class DeviceNetwork(TypedDict):
    """Define any network information needed."""

    ip: str
    mac: str


class ConfigEntryData(TypedDict):
    """Define data stored by integration."""

    user_data: dict
    home_data: dict
    base_url: str
    username: str
    device_network: dict[str, DeviceNetwork]


@dataclass
class RoborockHassDeviceInfo(DeviceData):
    """Define a help class to carry device information."""

    props: DeviceProp | None = None
    is_map_valid: bool | None = False
    map_mapping: dict[int, str] | None = None
    room_mapping: dict[int, str] | None = None
    current_room: int | None = None
