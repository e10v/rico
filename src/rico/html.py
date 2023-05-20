"""HTML parser and serializer."""

from __future__ import annotations

import html.parser
import xml.etree.ElementTree as ET  # noqa: N817


UNINDENTED_TAGS = {"pre"}

# Copy of xml.etree.ElementTree.HTML_EMPTY.
EMPTY_TAGS = {
    "area", "base", "basefont", "br", "col", "embed", "frame", "hr", "img",
    "input", "isindex", "link", "meta", "param", "path", "source", "track", "wbr",
}

UNESCAPED_TAGS = {"script", "style"}


class HTMLParser(html.parser.HTMLParser):
    """Simple HTML parser. Returns a list of instances of ET.Element on close().

    Assigns None values to boolean attributes.

    Ignores comments, doctype declaration and processing instructions.
    Converts attribute names to lower case, even for SVG.
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

    Assign None values to boolean attributes.

    Ignore comments, doctype declaration and processing instructions.
    Convert attribute names to lower case, even for SVG.

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
    if element.tag in UNINDENTED_TAGS or not len(element):
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


def _escape_cdata(text: str) -> str:
    """Copy of xml.etree.ElementTree._escape_cdata."""
    if "&" in text:
        text = text.replace("&", "&amp;")
    if "<" in text:
        text = text.replace("<", "&lt;")
    if ">" in text:
        text = text.replace(">", "&gt;")
    return text

def _escape_attrib_html(text: str) -> str:
    """Copy of xml.etree.ElementTree._escape_attrib_html."""
    if "&" in text:
        text = text.replace("&", "&amp;")
    if ">" in text:
        text = text.replace(">", "&gt;")
    if '"' in text:
        text = text.replace('"', "&quot;")
    return text

def serialize_html(element: ET.Element, indent_space: str | None = None) -> str:
    """Serialize an HTML document to a string.

    Indent the document if `indent_space` is not None.

    Serialize attributes with None values as boolean.

    Args:
        element: The HTML document.
        indent_space: The whitespace for indentation.

    Returns:
        The serialized HTML document.
    """
    if indent_space is not None:
        element = indent_html(element, space=indent_space)

    attrib = "".join(
        f' {k}="{_escape_attrib_html(v)}"'
        if v is not None  # pyright: ignore [reportUnnecessaryComparison]
        # Serialize attributes with None values as boolean.
        else f" {k}"
        for k, v in element.items()
    )

    opening_tag = f"<{element.tag}{attrib}>"
    ltag = element.tag.lower()

    if element.text is not None:
        text = element.text if ltag in UNESCAPED_TAGS else _escape_cdata(element.text)
    else:
        text = ""

    children = "".join(serialize_html(e) for e in element)
    closing_tag = f"</{element.tag}>" if ltag not in EMPTY_TAGS else ""
    tail = _escape_cdata(element.tail) if element.tail is not None else ""

    return opening_tag + text + children + closing_tag + tail
