from dataclasses import dataclass

# TODO: migration period only, kept so that old imports do not break.
#  The classes below now live in annetbox. Remove the re-export after the next major release.
from annetbox.v37.views import (  # noqa: F401
    DeviceIpV37,
    FHRPGroupAssignmentV37,
    FHRPGroupV37,
    InterfaceV37,
    IpAddressV37,
    PrefixV37,
)
from annetbox.v37.views import NetboxDeviceV37 as BaseNetboxDeviceV37

from annet.adapters.netbox.common.models import NetboxDevice


__all__ = [
    "DeviceIpV37",
    "FHRPGroupAssignmentV37",
    "FHRPGroupV37",
    "InterfaceV37",
    "IpAddressV37",
    "NetboxDeviceV37",
    "PrefixV37",
]


@dataclass
class NetboxDeviceV37(NetboxDevice[InterfaceV37, DeviceIpV37], BaseNetboxDeviceV37):
    def __hash__(self) -> int:
        return hash((self.id, type(self)))
