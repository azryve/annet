import dataclasses
from dataclasses import dataclass
from typing import Any, Generic, Sequence, TypeVar

# TODO: migration period only, kept so that old imports do not break.
#  These definitions now live in annetbox. Remove the re-export after the next major release.
from annetbox.common.models import (  # noqa: F401
    DeviceIp,
    DeviceType,
    Entity,
    EntityWithSlug,
    FHRPGroup,
    FHRPGroupAssignment,
    Interface,
    InterfaceConnectedEndpoint,
    InterfaceMode,
    InterfaceType,
    InterfaceVlan,
    IpAddress,
    IpFamily,
    Label,
    Prefix,
    Vrf,
    vrf_object,
)
from annetbox.common.models import NetboxDevice as BaseNetboxDevice

from annet.annlib.netdev.views.dump import DumpableView, register_plain_type
from annet.annlib.netdev.views.hardware import HardwareView, lag_name
from annet.storage import Storage
from annet.vendors import registry_connector


__all__ = [
    "DeviceIp",
    "DeviceType",
    "Entity",
    "EntityWithSlug",
    "FHRPGroup",
    "FHRPGroupAssignment",
    "Interface",
    "InterfaceConnectedEndpoint",
    "InterfaceMode",
    "InterfaceType",
    "InterfaceVlan",
    "IpAddress",
    "IpFamily",
    "Label",
    "NetboxDevice",
    "Prefix",
    "Vrf",
    "vrf_object",
]


# annetbox classes do not know about dumping, tell the dumper about them
register_plain_type(DeviceIp, lambda obj: obj.address)
register_plain_type(Entity, lambda obj: obj.name)
register_plain_type(Prefix, lambda obj: obj.prefix)
register_plain_type(IpAddress, lambda obj: obj.address)

_InterfaceT = TypeVar("_InterfaceT", bound=Interface[Any, Any])
_DeviceIPT = TypeVar("_DeviceIPT", bound=DeviceIp)


@dataclass
class NetboxDevice(BaseNetboxDevice[_InterfaceT, _DeviceIPT], DumpableView, Generic[_InterfaceT, _DeviceIPT]):
    """
    The device of annetbox with what annet adds to it.
    """

    fqdn: str = dataclasses.field(kw_only=True)
    hostname: str = dataclasses.field(kw_only=True)
    hw: HardwareView = dataclasses.field(kw_only=True)
    breed: str = dataclasses.field(kw_only=True)
    storage: Storage = dataclasses.field(kw_only=True)

    def is_pc(self) -> bool:
        custom_breed_pc = ("Mellanox", "NVIDIA", "Moxa", "Nebius")
        return self.device_type.manufacturer.name in custom_breed_pc or self.breed == "pc"

    def _lag_name(self, lag: int) -> str:
        return lag_name(self.hw, lag)

    def make_lag(self, lag: int, ports: Sequence[str], lag_min_links: int | None) -> _InterfaceT:
        new_name = self._lag_name(lag)
        for target_interface in self.interfaces:
            if target_interface.name == new_name:
                return target_interface
        lag_interface = self._make_interface(
            name=new_name,
            type=InterfaceType(value="lag", label="Link Aggregation Group (LAG)"),
        )
        lag_interface.lag_min_links = lag_min_links
        for interface in self.interfaces:
            if interface.name in ports:
                interface.lag = lag_interface
        self.interfaces.append(lag_interface)
        return lag_interface

    def _svi_name(self, svi: int) -> str:
        return registry_connector.get().match(self.hw).svi_name(svi)

    def add_svi(self, svi: int) -> _InterfaceT:
        name = self._svi_name(svi)
        for interface in self.interfaces:
            if interface.name == name:
                return interface
        interface = self._make_interface(name=name, type=InterfaceType("virtual", "Virtual"))
        self.interfaces.append(interface)
        return interface

    def _subif_name(self, interface: str, subif: int) -> str:
        return f"{interface}.{subif}"

    def add_subif(self, interface: str, subif: int) -> _InterfaceT:
        name = self._subif_name(interface, subif)
        for target_port in self.interfaces:
            if target_port.name == name:
                return target_port
        target_port = self._make_interface(name=name, type=InterfaceType("virtual", "Virtual"))
        self.interfaces.append(target_port)
        return target_port
