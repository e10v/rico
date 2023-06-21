"""HTML parser and serializer."""

from __future__ import annotations

import html.parser
import xml.etree.ElementTree as ET

import rico._config


TAGS_EMPTY = {
    "area", "base", "basefont", "br", "col", "embed", "frame", "hr", "img",
    "input", "isindex", "link", "meta", "param", "path", "source", "track", "wbr",
}

TAGS_INLINE = {
    "a", "abbr", "b", "bdi", "bdo", "br", "cite", "code", "data", "dfn", "em",
    "i", "kbd", "mark", "q", "rp", "rt", "ruby", "s", "samp", "small", "span",
    "strong", "sub", "sup", "time", "u", "var", "wbr",
}

TAGS_NOT_ESCAPED = {"script", "style"}
TAGS_PREFORMATTED = {"pre"}


class HTMLParser(html.parser.HTMLParser):
    """Simple HTML parser. Returns a list of instances of ET.Element on close().

    Assigns None values to boolean attributes.

    Ignores comments, doctype declaration and processing instructions.
    Converts attribute names to lower case, even for SVG.
    """

    def __init__(self):
        super().__init__()
        self._root = "root"
        self._builder = ET.TreeBuilder()
        self._builder.start(self._root, {})

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        self._builder.start(tag, dict(attrs))

    def handle_endtag(self, tag: str) -> None:
        self._builder.end(tag)

    def handle_data(self, data: str) -> None:
        self._builder.data(data)

    def close(self) -> tuple[ET.Element]:  # type: ignore
        super().close()
        self._builder.end(self._root)
        return tuple(self._builder.close())


def parse_html(data: str) -> tuple[ET.Element]:
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
    """Indent an HTML element.

    Tnsert newlines and indentation space after elements.
    Create a new element instead of updating inplace.
    Do not indent elements inside <pre> tag.

    Args:
        element: The element to indent.
        space: The whitespace to insert for each indentation level.
        level: The initial indentation level. Should always be 0.

    Returns:
        The indented HTML element.
    """
    if element.tag.lower() in TAGS_PREFORMATTED or not len(element):
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

    if not indented_child.tail or not indented_child.tail.strip():  # type: ignore
        indented_child.tail = "\n" + space * level  # type: ignore

    return indented_element


def strip_html(element: ET.Element) -> ET.Element:
    """Strip an HTML element.

    Remove unnecessary whitespaces from the element by strippping elements'
    text and tail.
    Do not strip elements inside <pre> tag or inside inline tags.

    Args:
        element: The element to strip.

    Returns:
        The stripped HTML element.
    """
    stripped_element = ET.Element(element.tag, attrib=element.attrib)
    stripped_element.text = element.text
    stripped_element.tail = element.tail

    if element.tag.lower() in TAGS_INLINE | TAGS_PREFORMATTED:
        for child in element:
            stripped_element.append(child)
    else:
        for child in element:
            stripped_element.append(strip_html(child))

        if stripped_element.text:
            if len(stripped_element) == 0 and (
                not stripped_element.tail or
                not stripped_element.tail.strip()
            ):
                stripped_element.text = stripped_element.text.strip()
            else:
                stripped_element.text = stripped_element.text.lstrip()

    if stripped_element.tail:
        if len(stripped_element) == 0 and not stripped_element.text:
            stripped_element.tail = stripped_element.tail.strip()
        else:
            stripped_element.tail = stripped_element.tail.rstrip()

    return stripped_element


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

def serialize_html(
    element: ET.Element,
    indent: bool | None = None,
    space: str | None = None,
    strip: bool | None = None,
) -> str:
    """Serialize an HTML element to a string.

    Serialize attributes with None values as boolean.

    Args:
        element: The HTML element.
        indent: If True, indent the element.
        space: The whitespace for indentation.
        strip: If True, strip unnecessary whitespace.

    Returns:
        The serialized HTML element.
    """
    global_config = rico._config.get_config()
    if indent is None:
        indent = global_config["indent_html"]
    if space is None:
        space = global_config["indent_space"]
    if strip is None:
        strip = global_config["strip_html"]

    if strip:
        element = strip_html(element)
    if indent:
        element = indent_html(element, space=space)  # type: ignore

    attrib = "".join(
        f' {k}="{_escape_attrib_html(v)}"'
        if v is not None and not isinstance(v, bool)  # type: ignore
        # Serialize attributes with None values as boolean.
        else f" {k}"
        for k, v in element.items()
        if not isinstance(v, bool) or v
    )

    opening_tag = f"<{element.tag}{attrib}>"
    ltag = element.tag.lower()

    if element.text is not None:
        text = element.text if ltag in TAGS_NOT_ESCAPED else _escape_cdata(element.text)
    else:
        text = ""

    children = "".join(serialize_html(e) for e in element)
    closing_tag = f"</{element.tag}>" if ltag not in TAGS_EMPTY else ""
    tail = _escape_cdata(element.tail) if element.tail is not None else ""

    return opening_tag + text + children + closing_tag + tail
