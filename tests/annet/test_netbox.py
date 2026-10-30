import pytest
from annetbox.v37 import models as v37_api_models
from annetbox.v41 import models as v41_api_models
from annetbox.v42 import models as v42_api_models

from annet.adapters.netbox.common.query import NetboxQuery
from annet.adapters.netbox.common.storage_base import parse_glob
from annet.adapters.netbox.common.storage_opts import NetboxStorageOpts
from annet.adapters.netbox.v37 import storage as v37_storage
from annet.adapters.netbox.v41 import storage as v41_storage
from annet.adapters.netbox.v42 import storage as v42_storage


STORAGES = [
    pytest.param(v37_storage.NetboxStorageV37, "NetboxV37", id="v37"),
    pytest.param(v41_storage.NetboxStorageV41, "NetboxV41", id="v41"),
    pytest.param(v42_storage.NetboxStorageV42, "NetboxV42", id="v42"),
]


@pytest.mark.parametrize("storage_cls,client_name", STORAGES)
def test_storage_exposes_the_annetbox_client(storage_cls, client_name):
    storage = storage_cls(NetboxStorageOpts(url="http://localhost", token=""))

    assert type(storage.client).__name__ == client_name
    assert storage.client is storage.netbox.client


@pytest.mark.parametrize(
    "api_mod",
    [
        pytest.param(v37_api_models, id="v37"),
        pytest.param(v41_api_models, id="v41"),
        pytest.param(v42_api_models, id="v42"),
    ],
)
def test_netbox_device_site_remains_entity(api_mod):
    """Backward-compat: device.site stays an EntityWithSlug stub, not a full Site."""
    assert api_mod.Device.__annotations__["site"] is api_mod.EntityWithSlug


def test_parse_glob():
    assert parse_glob(True, NetboxQuery(["host"])) == {"name__ie": ["host"]}
    assert parse_glob(False, NetboxQuery(["host"])) == {"name__ic": ["host."]}
    assert parse_glob(True, NetboxQuery(["site:mysite"])) == {"site": ["mysite"]}
    assert parse_glob(True, NetboxQuery(["tag:mysite", "justhost"])) == {
        "name__ie": ["justhost"],
        "tag": ["mysite"],
    }
    with pytest.raises(Exception):
        parse_glob(True, NetboxQuery(["host:"]))
    with pytest.raises(Exception):
        parse_glob(True, NetboxQuery(["NONONO:param"]))
