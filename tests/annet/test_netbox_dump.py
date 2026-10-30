from dataclasses import dataclass, field
from datetime import datetime, timezone

from annetbox.common.models import EntityWithSlug, IpAddress, IpFamily, Label, Prefix, Vrf

from annet.adapters.netbox.common import models as _models  # noqa: F401  (registers the classes in the dumper)
from annet.annlib.netdev.views.dump import DumpableView, dump_list_key


NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


@dataclass
class Holder(DumpableView):
    items: list = field(default_factory=list)
    prefix: Prefix | None = None


def _prefix(**kwargs) -> Prefix:
    fields = dict(
        id=1,
        prefix="10.0.0.0/24",
        vrf=Vrf(id=3, name="mgmt", rd=None),
        tenant=None,
        vlan=None,
        role=None,
        status=Label(value="active", label="Active"),
        is_pool=False,
        custom_fields={},
        created=NOW,
        last_updated=NOW,
        tags=[EntityWithSlug(id=7, name="Tag", slug="tag")],
    )
    fields.update(kwargs)
    return Prefix(**fields)


def _ip_address() -> IpAddress:
    return IpAddress(
        id=1,
        assigned_object_id=None,
        display="x",
        family=IpFamily(value=4, label="IPv4"),
        address="10.0.0.1/24",
        status=Label(value="active", label="Active"),
        created=NOW,
        last_updated=NOW,
    )


def test_plain_data_class_is_dumped_without_implementing_anything():
    assert not hasattr(Prefix, "dump")
    lines = Holder(prefix=_prefix()).dump("h")
    assert "h.prefix.tags['Tag'].slug = 'tag'" in lines
    assert "h.prefix.vrf.name = 'mgmt'" in lines
    # not a plain type, shown as a repr
    assert "h.prefix.status = Label(value='active', label='Active')" in lines


def test_list_keys():
    assert dump_list_key(_ip_address()) == "10.0.0.1/24"
    assert dump_list_key(_prefix()) == "10.0.0.0/24"
    assert dump_list_key(EntityWithSlug(id=1, name="n", slug="s")) == "n"
    assert dump_list_key("something else") is None
    assert "h.items['10.0.0.1/24'].id = 1" in Holder(items=[_ip_address()]).dump("h")


def test_repeated_object_is_a_reference():
    tag = EntityWithSlug(id=7, name="Tag", slug="tag")
    lines = Holder(prefix=_prefix(tags=[tag, tag])).dump("h")
    assert "h.prefix.tags['Tag'].slug = 'tag'" in lines
    assert "h.prefix.tags['Tag'] -> h.prefix.tags['Tag']" in lines


def test_dumpable_view_override_is_used_when_nested():
    @dataclass
    class Hw(DumpableView):
        def dump(self, prefix="", **kwargs):
            return [f"{prefix} = custom"]

    @dataclass
    class Device(DumpableView):
        hw: Hw

    assert Device(Hw()).dump("d") == ["d.hw = custom"]
