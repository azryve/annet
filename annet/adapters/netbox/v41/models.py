from dataclasses import dataclass

# TODO: migration period only, kept so that old imports do not break.
#  The classes below now live in annetbox. Remove the re-export after the next major release.
from annetbox.v41.views import (  # noqa: F401
    DeviceIpV41,
    FHRPGroupAssignmentV41,
    FHRPGroupV41,
    InterfaceV41,
    IpAddressV41,
    PrefixV41,
)
from annetbox.v41.views import NetboxDeviceV41 as BaseNetboxDeviceV41

from annet.adapters.netbox.common.models import NetboxDevice


__all__ = [
    "DeviceIpV41",
    "FHRPGroupAssignmentV41",
    "FHRPGroupV41",
    "InterfaceV41",
    "IpAddressV41",
    "NetboxDeviceV41",
    "PrefixV41",
]


@dataclass
class NetboxDeviceV41(NetboxDevice[InterfaceV41, DeviceIpV41], BaseNetboxDeviceV41):
    def __hash__(self) -> int:
        return hash((self.id, type(self)))
