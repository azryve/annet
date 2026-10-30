from dataclasses import dataclass, field

from annet.annlib.netdev.views.dump import DumpableView, dump_list_key, register_plain_type


@dataclass
class Tag:
    id: int
    name: str


@dataclass
class Item:
    id: int
    name: str
    tags: list[Tag] = field(default_factory=list)
    kind: Tag | None = None


@dataclass
class NotRegistered:
    value: int


register_plain_type(Tag, lambda obj: obj.name)
register_plain_type(Item, lambda obj: f"item-{obj.id}")


@dataclass
class Holder(DumpableView):
    items: list = field(default_factory=list)
    item: Item | None = None
    other: NotRegistered | None = None


def test_registered_data_class_is_dumped_without_implementing_anything():
    assert not hasattr(Item, "dump")
    lines = Holder(item=Item(1, "a", tags=[Tag(7, "t")])).dump("h")
    assert "h.item.name = 'a'" in lines
    assert "h.item.tags['t'].id = 7" in lines


def test_not_registered_data_class_is_shown_as_repr():
    assert "h.other = NotRegistered(value=5)" in Holder(other=NotRegistered(5)).dump("h")


def test_list_keys():
    assert dump_list_key(Item(3, "a")) == "item-3"
    assert dump_list_key(Tag(1, "t")) == "t"
    assert dump_list_key("something else") is None
    assert "h.items['item-3'].id = 3" in Holder(items=[Item(3, "a")]).dump("h")


def test_repeated_object_is_a_reference():
    tag = Tag(7, "t")
    lines = Holder(item=Item(1, "a", tags=[tag, tag])).dump("h")
    assert "h.item.tags['t'].id = 7" in lines
    assert "h.item.tags['t'] -> h.item.tags['t']" in lines


def test_dumpable_view_override_is_used_when_nested():
    @dataclass
    class Hw(DumpableView):
        def dump(self, prefix="", **kwargs):
            return [f"{prefix} = custom"]

    @dataclass
    class Device(DumpableView):
        hw: Hw

    assert Device(Hw()).dump("d") == ["d.hw = custom"]
