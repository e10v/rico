"""HTML parser and serializer."""

from __future__ import annotations

import html.parser
import xml.etree.ElementTree as ET  # noqa: N817


class HTMLParser(html.parser.HTMLParser):
    """Simple HTML parser. Returns a list of instances of ET.Element on close().

    Ignores comments, doctype declaration and processing instructions.
    """

    def __init__(self):  # noqa: D107
        super().__init__()
        self._root = "root"
        self._builder = ET.TreeBuilder()
        self._builder.start(self._root, {})

    def handle_starttag(  # noqa: D102
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        self._builder.start(tag, dict(attrs))

    def handle_endtag(self, tag: str) -> None:  # noqa: D102
        self._builder.end(tag)

    def handle_data(self, data: str) -> None:  # noqa: D102
        self._builder.data(data)

    def close(self) -> list[ET.Element]:  # noqa: D102
        super().close()
        self._builder.end(self._root)
        return list(self._builder.close())


def parse_html(data: str) -> list[ET.Element]:
    """Parse HTML from a string.

    Ignores comments, doctype declaration and processing instructions.

    Args:
        data: HTML data.

    Returns:
        Parsed HTML data.
    """
    parser = HTMLParser()
    parser.feed(data)
    return parser.close()
