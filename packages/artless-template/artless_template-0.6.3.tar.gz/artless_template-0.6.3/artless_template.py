"""A lightweight and efficient template library for server-side rendering."""

__author__ = "Peter Bro"
__version__ = "0.6.3"
__license__ = "MIT"
__all__ = ["Component", "Tag", "Template", "aread_template", "read_template"]

from asyncio import to_thread
from pathlib import Path
from re import compile, escape
from typing import (
    ClassVar,
    Final,
    Mapping,
    Optional,
    Pattern,
    Protocol,
    runtime_checkable,
)

# Void tags (https://developer.mozilla.org/en-US/docs/Glossary/Void_element)
_VOID_TAGS: Final[frozenset[str]] = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "source",
        "track",
        "wbr",
    }
)


@runtime_checkable
class Component(Protocol):
    def view(self) -> "Tag": ...


def _read_file_raw(filename: str | Path, /) -> str:
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


class Tag:
    __slots__ = ("attrs", "children", "name", "parent", "text")

    def __init__(self, name: str, /, *args) -> None:
        self.name = name.lower()
        self.attrs, self.children, self.text = self._unpack_args(*args)
        self.parent: Optional["Tag"] = None

        for child in self.children:
            if isinstance(child, Tag):
                child.parent = self

    def __str__(self) -> str:
        parts = [f"<{self.name}"]

        if self.attrs:
            parts.extend(f' {k}="{v}"' for k, v in self.attrs.items())

        if self.name in _VOID_TAGS:
            parts.append(" />")
            return "".join(parts)

        parts.append(">")

        for child in self.children:
            parts.append(str(child))

        parts.append(f"{self.text}</{self.name}>")

        return "".join(parts)

    def __repr__(self) -> str:
        return f"<Tag: {self.name!r}>"

    @property
    def is_parent(self) -> bool:
        return bool(self.children)

    @property
    def is_leaf(self) -> bool:
        return not self.children

    def add_child(self, tag: "Tag", /) -> "Tag":
        if not isinstance(tag, Tag):
            raise TypeError(f"Child must be Tag instance, got {type(tag).__name__}")
        tag.parent = self
        self.children.append(tag)
        return self

    @staticmethod
    def _unpack_args(*args) -> tuple[dict[str, str], list["Tag"], str]:
        attrs: dict[str, str] = {}
        children: list[Tag] = []
        text: str = ""

        for arg in args:
            if isinstance(arg, Mapping):
                attrs.update(arg)
            elif isinstance(arg, (list, tuple)):
                children.extend(arg)
            elif isinstance(arg, str):
                text = arg
            elif arg:
                raise TypeError(f"Invalid argument type: {type(arg).__name__}")

        return attrs, children, text


class Template:
    __slots__ = ("content", "name", "_compiled_pattern")
    DELIMITER: ClassVar[str] = "@"

    def __init__(self, /, *, name: str | Path, content: str) -> None:
        self.name = name
        self.content = content
        self._compiled_pattern: tuple[Pattern[str], dict[str, str]] | None = None

    def __repr__(self) -> str:
        return f"<Template: {self.name!r}>"

    def render(self, **context) -> str:
        if not context:
            return self.content

        if self._compiled_pattern is None:
            replacements = {
                f"{self.DELIMITER}{key}": str(value.view() if isinstance(value, Component) else value)
                for key, value in context.items()
            }
            sorted_keys = sorted(replacements, key=len, reverse=True)
            self._compiled_pattern = (compile(r"|".join(map(escape, sorted_keys))), replacements)

        pattern, replacements = self._compiled_pattern
        return pattern.sub(lambda m: replacements[m.group(0)], self.content)


def read_template(filename: str | Path, /) -> Template:
    return Template(name=filename, content=_read_file_raw(filename))


async def aread_template(filename: str | Path, /) -> Template:
    return await to_thread(read_template, filename)
