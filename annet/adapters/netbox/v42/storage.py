import ssl
from typing import Callable, Optional

from annetbox.v42.loader import NetboxLoaderV42
from requests import Session

from annet.adapters.netbox.common.storage_base import BaseNetboxStorage
from annet.adapters.netbox.common.storage_opts import NetboxStorageOpts
from annet.adapters.netbox.v41.models import FHRPGroupAssignmentV41, FHRPGroupV41
from annet.adapters.netbox.v42.models import InterfaceV42, IpAddressV42, NetboxDeviceV42, PrefixV42, Vlan, Vrf

# TODO: migration period only, kept so that old imports do not break.
#  Storage is not defined here, import it from annet.storage. Remove this after the next major release.
from annet.storage import Storage  # noqa: F401


class NetboxStorageV42(
    BaseNetboxStorage[
        NetboxDeviceV42,
        InterfaceV42,
        IpAddressV42,
        PrefixV42,
        FHRPGroupV41,
        FHRPGroupAssignmentV41,
    ]
):
    netbox: NetboxLoaderV42
    device_cls = NetboxDeviceV42

    def __init__(self, opts: Optional[NetboxStorageOpts] = None):
        super().__init__(opts)
        self._all_vlans: list[Vlan] | None = None
        self._all_vrfs: list[Vrf] | None = None

    def _init_adapter(
        self,
        url: str,
        token: str,
        ssl_context: ssl.SSLContext | None,
        threads: int,
        session_factory: Callable[[Session], Session] | None = None,
    ) -> NetboxLoaderV42:
        return NetboxLoaderV42(url, token, ssl_context, threads, session_factory)

    def resolve_all_vlans(self) -> list[Vlan]:
        if self._all_vlans is None:
            self._all_vlans = self.netbox.list_all_vlans()
        return self._all_vlans

    def resolve_all_vrfs(self) -> list[Vrf]:
        if self._all_vrfs is None:
            self._all_vrfs = self.netbox.list_all_vrfs()
        return self._all_vrfs
