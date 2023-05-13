"""HTML parser and serializer."""

from __future__ import annotations

import html.parser
import xml.etree.ElementTree as ET  # noqa: N817


TAGS_WITHOUT_INDENT = {"pre"}


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
    """Parse an HTML document from a string.

    Ignores comments, doctype declaration and processing instructions.

    Args:
        data: The HTML data.

    Returns:
        The parsed HTML document.
    """
    parser = HTMLParser()
    parser.feed(data)
    return parser.close()


def indent_html(
    element: ET.Element,
    space: str = "  ",
    level: int = 0,
) -> ET.Element:
    """Indent an HTML document.

    Tnsert newlines and indentation space after elements.
    Create a new document instead of updating inplace.
    Do not indent elements inside <pre> tag.

    Args:
        element: The element to indent.
        space: The whitespace to insert for each indentation level.
        level: The initial indentation level. Should always be 0.

    Returns:
        The indented HTML document.
    """
    if element.tag in TAGS_WITHOUT_INDENT or not len(element):
        return element

    indented_element = ET.Element(element.tag, attrib=element.attrib)
    indented_element.text = element.text
    indented_element.tail = element.tail

    if not element.text or not element.text.strip():
        indented_element.text = "\n" + space * (level + 1)

    for child in element:
        indented_child = indent_html(child, space=space, level=level + 1)

        if not indented_child.tail or not indented_child.tail.strip():
            indented_child.tail = "\n" + space * (level + 1)

        indented_element.append(indented_child)

    if not indented_child.tail or not indented_child.tail.strip():  # pyright: ignore [reportUnboundVariable]  # noqa: E501
        indented_child.tail = "\n" + space * level  # pyright: ignore [reportUnboundVariable]  # noqa: E501

    return indented_element
