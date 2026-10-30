from __future__ import annotations

import functools
import inspect
import sys
import traceback
from collections.abc import Callable, Iterator
from typing import Any, cast


class DumpResult(str):
    """
    a string whose repr equals its value
    """

    def __new__(cls, value: str) -> DumpResult:
        return super().__new__(cls, value)

    __repr__ = str.__str__


class _EnumAllAttrs:
    pass


# Data classes that do not know about dumping, they are dumped like DumpableView.
# The adapters that have such classes register them, see register_plain_type().
_PLAIN_TYPES: list[type] = []


@functools.singledispatch
def dump_list_key(obj: object) -> str | None:
    return cast("str | None", getattr(obj, "_dump__list_key", None))


def register_plain_type(cls: type, list_key: Callable[[Any], str]) -> None:
    """Dump the instances of cls attribute by attribute, list_key names them in a list."""
    _PLAIN_TYPES.append(cls)
    dump_list_key.register(cls, list_key)


class DumpableView:
    def _enum_attrs(self) -> Iterator[str]:
        for attr in dir(self):
            if not attr.startswith("_") and attr != "dump":
                yield attr

    def _getter_for_dump(self, attr: str) -> Callable[[], object] | None:
        dumper_name = "_dump_" + attr
        if hasattr(self, dumper_name) and callable(getattr(self, dumper_name)):
            return cast(Callable[[], object], getattr(self, dumper_name))
        return None

    @staticmethod
    def strip_dumper(
        attr: str,
        lines: int | None = None,
        chars: int | None = None,
        chars_in_line: int | None = None,
    ) -> Callable[[DumpableView], DumpResult]:
        def bound_method(self: DumpableView) -> DumpResult:
            lines_list = []
            value = getattr(self, attr)
            assert isinstance(value, str)
            total_lines = 0
            total_chars = 0
            add_tail = True
            for line in value.split("\n"):
                if lines and total_lines >= lines:
                    break

                if chars and total_chars + len(line) >= chars:
                    lines_list.append(line[chars - total_chars :])
                    break

                if chars_in_line and len(line) > chars_in_line:
                    assert chars is not None
                    lines_list.append(line[chars - total_chars :] + " ...")
                else:
                    lines_list.append(line)
                total_lines += 1
                total_chars += len(line) + 1
            else:
                add_tail = False

            ret = repr("\n".join(lines_list))
            if add_tail:
                ret += " ..."
            return DumpResult(ret)

        return bound_method

    def __dump_value(self, prefix: str, value: Any, seen: dict[int, str]) -> list[str]:
        ret: list[str] = []
        op = "="
        if isinstance(value, (DumpableView, *_PLAIN_TYPES)):
            # recursion guard - later occurrences are rendered as references rather than dumped again
            if id(value) in seen:
                value = DumpResult(seen[id(value)])
                op = "->"
            else:
                seen[id(value)] = prefix
                if not isinstance(value, DumpableView):
                    value = _PlainView(value)

        if isinstance(value, DumpableView):
            ret += value.dump(prefix, seen=seen)  # pylint: disable=no-member
        elif isinstance(value, dict):
            for k, v in value.items():
                ret.extend(self.__dump_value(f"{prefix}[{repr(k)}]", v, seen))
        elif isinstance(value, (list, tuple)):
            for i, v in enumerate(value):
                name = dump_list_key(v)
                name = repr(name) if name is not None else str(i)
                ret.extend(self.__dump_value(f"{prefix}[{name}]", v, seen))
        else:
            fmt = repr(value)
            vtype = type(value)
            if not isinstance(value, DumpResult) and (vtype.__module__ != "builtins") and vtype.__name__ not in fmt:
                fmt += "  # %s" % (vtype)
            ret += ["%s %s %s" % (prefix, op, fmt)]
        return ret

    def dump(self, prefix: str = "", value: Any = _EnumAllAttrs, seen: dict[int, str] | None = None) -> list[str]:
        """
        In your own DumpableView classes dump should be defined roughly like this:
        def dump(self, prefix, **kwargs):
            ret = super().dump(prefix, **kwargs) + [ your_own_lines ]
        """
        if seen is None:
            seen = {id(self): prefix}

        ret = []
        if value is not _EnumAllAttrs:
            ret.extend(self.__dump_value(prefix, value, seen))
        else:
            for attr in self._enum_attrs():
                getter = self._getter_for_dump(attr)
                try:
                    if getter:
                        value = getter()
                    else:
                        value = getattr(self, attr)
                        if inspect.isroutine(value):
                            continue
                except Exception as exc:
                    exc_tb = sys.exc_info()[2]
                    frame_index = -1
                    tb_list = traceback.extract_tb(exc_tb)
                    value = DumpResult("%r at %s:%s" % (exc, tb_list[frame_index][0], tb_list[frame_index][1]))

                ret.extend(self.__dump_value("%s.%s" % (prefix, attr), value, seen))
        return ret

    # Filter out cached lru_methods from state
    def __getstate__(self) -> dict[str, Any]:
        state = self.__dict__.copy()
        for key in list(state.keys()):  # For thread-safe: dictionary changed size during iteration
            if inspect.ismethod(state[key]):
                del state[key]
        return state


class _PlainView(DumpableView):
    """Makes an object that does not know about dumping dumpable."""

    def __init__(self, obj: object) -> None:
        self._obj = obj

    def __getattr__(self, name: str) -> Any:
        if name == "_obj":
            raise AttributeError(name)
        return getattr(self._obj, name)

    def _enum_attrs(self) -> Iterator[str]:
        for attr in dir(self._obj):
            if not attr.startswith("_") and attr != "dump":
                yield attr
