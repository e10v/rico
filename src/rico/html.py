"""HTML parser and serializer."""

from __future__ import annotations

import html.parser
from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET  # noqa: N817


if TYPE_CHECKING:
    from typing import Any


class HTMLParser(html.parser.HTMLParser):
    """Simple HTML parser. Returns an instance of ET.Element on close().

    Ignores comments, doctype declaration and processing instructions.
    """

    def __init__(self, root: str = "div"):
        """Initalizes parser.

        Args:
            root: A root tag.
        """
        super().__init__()
        self._root = root
        self._builder = ET.TreeBuilder()
        self._builder.start(self._root, {})

    def handle_starttag(  # noqa: ANN201, D102
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ):
        self._builder.start(tag, dict(attrs))

    def handle_endtag(self, tag: str):  # noqa: ANN201, D102
        self._builder.end(tag)

    def handle_data(self, data: Any):  # noqa: ANN201, D102
        self._builder.data(data)

    def close(self) -> ET.Element:  # noqa: D102
        super().close()
        self._builder.end(self._root)
        return self._builder.close()


def parse_html(data: str, root: str = "div") -> ET.Element:
    """Parse HTML from a string.

    Ignores comments, doctype declaration and processing instructions.

    Args:
        data: HTML data.
        root: A root tag.

    Returns:
        Parsed HTML data.
    """
    parser = HTMLParser(root=root)
    parser.feed(data)
    return parser.close()
