import ssl
from typing import Callable

from annetbox.v37.loader import NetboxLoaderV37
from requests import Session

from annet.adapters.netbox.common.storage_base import BaseNetboxStorage
from annet.adapters.netbox.v37.models import (
    FHRPGroupAssignmentV37,
    FHRPGroupV37,
    InterfaceV37,
    IpAddressV37,
    NetboxDeviceV37,
    PrefixV37,
)


class NetboxStorageV37(
    BaseNetboxStorage[
        NetboxDeviceV37,
        InterfaceV37,
        IpAddressV37,
        PrefixV37,
        FHRPGroupV37,
        FHRPGroupAssignmentV37,
    ]
):
    netbox: NetboxLoaderV37
    device_cls = NetboxDeviceV37

    def _init_adapter(
        self,
        url: str,
        token: str,
        ssl_context: ssl.SSLContext | None,
        threads: int,
        session_factory: Callable[[Session], Session] | None = None,
    ) -> NetboxLoaderV37:
        return NetboxLoaderV37(url, token, ssl_context, threads, session_factory)
