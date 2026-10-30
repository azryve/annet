import ssl
from typing import Callable

from annetbox.v41.loader import NetboxLoaderV41
from requests import Session

from annet.adapters.netbox.common.storage_base import BaseNetboxStorage
from annet.adapters.netbox.v41.models import (
    FHRPGroupAssignmentV41,
    FHRPGroupV41,
    InterfaceV41,
    IpAddressV41,
    NetboxDeviceV41,
    PrefixV41,
)


class NetboxStorageV41(
    BaseNetboxStorage[NetboxDeviceV41, InterfaceV41, IpAddressV41, PrefixV41, FHRPGroupV41, FHRPGroupAssignmentV41]
):
    netbox: NetboxLoaderV41
    device_cls = NetboxDeviceV41

    def _init_adapter(
        self,
        url: str,
        token: str,
        ssl_context: ssl.SSLContext | None,
        threads: int,
        session_factory: Callable[[Session], Session] | None = None,
    ) -> NetboxLoaderV41:
        return NetboxLoaderV41(url, token, ssl_context, threads, session_factory)
