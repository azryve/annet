import dataclasses
from typing import Any, TypeVar

from annet.annlib.netdev.views.hardware import HardwareView
from annet.storage import Storage

from .manufacturer import get_breed, get_hw
from .models import NetboxDevice


NetboxDeviceT = TypeVar("NetboxDeviceT", bound=NetboxDevice[Any, Any])


def get_device_breed(device: NetboxDeviceT) -> str:
    if device.device_type and device.device_type.manufacturer:
        return get_breed(
            device.device_type.manufacturer.name,
            device.device_type.model,
        )
    return ""


def get_device_hw(device: NetboxDeviceT) -> HardwareView:
    if device.device_type and device.device_type.manufacturer:
        return get_hw(
            device.device_type.manufacturer.name,
            device.device_type.model,
            device.platform.name if device.platform else "",
        )
    return HardwareView("", "")


def make_device(cls: type[NetboxDeviceT], device: Any, storage: Storage) -> NetboxDeviceT:
    """
    Make the device of annet from the device that annetbox converted,
    all its fields are taken as they are.
    """
    return cls(
        **{f.name: getattr(device, f.name) for f in dataclasses.fields(device)},
        fqdn=device.name,
        hostname=device.name,
        hw=get_device_hw(device),
        breed=get_device_breed(device),
        storage=storage,
    )
