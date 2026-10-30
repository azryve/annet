from dataclasses import dataclass

import annetbox.v42.models

# TODO: migration period only, kept so that old imports do not break.
#  The classes below now live in annetbox. Remove the re-export after the next major release.
from annetbox.v41.views import (  # noqa: F401
    DeviceIpV41,
    FHRPGroupAssignmentV41,
    FHRPGroupV41,
)
from annetbox.v42.views import (  # noqa: F401
    InterfaceV42,
    IpAddressV42,
    PrefixV42,
)
from annetbox.v42.views import NetboxDeviceV42 as BaseNetboxDeviceV42

from annet.adapters.netbox.common.models import NetboxDevice


__all__ = [
    "DeviceIpV41",
    "FHRPGroupAssignmentV41",
    "FHRPGroupV41",
    "InterfaceV42",
    "IpAddressV42",
    "NetboxDeviceV42",
    "PrefixV42",
    "Vlan",
    "Vrf",
]


@dataclass
class NetboxDeviceV42(NetboxDevice[InterfaceV42, DeviceIpV41], BaseNetboxDeviceV42):
    def __hash__(self) -> int:
        return hash((self.id, type(self)))


# should be unified in case of netbox update
Vrf = annetbox.v42.models.Vrf
Vlan = annetbox.v42.models.Vlan
