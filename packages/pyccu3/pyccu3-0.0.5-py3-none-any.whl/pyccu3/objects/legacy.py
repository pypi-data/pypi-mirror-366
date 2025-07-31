import re
from dataclasses import dataclass
from typing import List

from pyccu3.enums import AESState, Direction, FirmwareUpdateState, RxMode
from pyccu3.objects.base import BaseSerializer


@dataclass
class HomeMaticRPCDevice(BaseSerializer):
    type: str
    subtype: str
    address: str
    rf_address: int
    children: List[str]
    parent: str
    parent_type: str
    index: int
    aes_active: AESState
    paramsets: List[str]
    firmware: str
    available_firmware: str
    updatable: bool
    firmware_update_state: FirmwareUpdateState
    version: int
    flags: int
    link_source_roles: str
    link_target_roles: str
    direction: Direction
    group: str
    team: str
    team_tag: str
    team_channels: List[str]
    interface: str
    roaming: int
    rx_mode: RxMode

    @property
    def default_device(self) -> bool:
        if re.match("^[0-9a-f]{14}:[0-9]+$", self.address, re.IGNORECASE):
            return True
        return False
