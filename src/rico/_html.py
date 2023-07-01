"""HTML parser and serializer."""

from __future__ import annotations

import html.parser
import textwrap
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


class _HTMLParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self._root = "root"
        self._builder = ET.TreeBuilder()
        self._builder.start(self._root, {})
        self._empty_tag = None

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if self._empty_tag:
            self._builder.end(self._empty_tag)
        self._empty_tag = tag if tag.lower() in TAGS_EMPTY else None
        self._builder.start(tag, dict(attrs))

    def handle_endtag(self, tag: str) -> None:
        if self._empty_tag:
            if self._empty_tag.lower() != tag.lower():
                self._builder.end(self._empty_tag)
            self._empty_tag = None
        self._builder.end(tag)

    def handle_data(self, data: str) -> None:
        if self._empty_tag:
            self._builder.end(self._empty_tag)
            self._empty_tag = None
        self._builder.data(data)

    def close(self) -> tuple[ET.Element]:  # type: ignore
        super().close()
        self._builder.end(self._root)
        return tuple(self._builder.close())


def parse_html(data: str) -> tuple[ET.Element]:
    """Parse HTML from a string.

    Assigns None values to boolean attributes.

    Ignores comments, doctype declaration and processing instructions.
    Converts attribute names to lower case, even for SVG.

    Args:
        data: The string containing HTML data.

    Returns:
        HTML elements parsed from the string.
    """
    parser = _HTMLParser()
    parser.feed(data)
    return parser.close()


def indent_html(
    element: ET.Element,
    space: str = "  ",
    level: int = 0,
) -> ET.Element:
    """Indent an HTML element and its chidren.

    Tnserts newlines and indentation space after elements.
    Creates a new element instead of updating in place.
    Doesn't indent elements inside the <pre> tag or inside inline tags.

    Args:
        element: The element to indent.
        space: Whitespace to insert for each indentation level.
        level: The initial indentation level. Should always be 0.

    Returns:
        Indented HTML element.
    """
    indented_element = ET.Element(element.tag, attrib=element.attrib)
    indented_element.text = element.text
    indented_element.tail = element.tail

    if element.tag.lower() in TAGS_PREFORMATTED | TAGS_INLINE:
        for child in element:
            indented_element.append(child)
    else:
        has_children = len(element) > 0
        left_stripped_text = (
            indented_element.text.lstrip()
            if indented_element.text else
            indented_element.text
        )
        if (
            not has_children and
            indented_element.text is not None and
            left_stripped_text
        ):
            if "\n" in left_stripped_text:
                indented_element.text = "\n" + textwrap.indent(
                    textwrap.dedent(indented_element.text).strip(),
                    space * (level + 1),
                ) + "\n" + space * level
            else:
                indented_element.text = left_stripped_text
        elif not left_stripped_text:
            indented_element.text = "\n" + space * (level + 1) if has_children else None

        for child in element:
            indented_child = indent_html(child, space=space, level=level + 1)
            indented_element.append(indented_child)
            if not indented_child.tail or not indented_child.tail.strip():
                indented_child.tail = "\n" + space * (level + 1)

        if has_children:
            last_child = indented_element[-1]
            if not last_child.tail or not last_child.tail.strip():
                last_child.tail = "\n" + space * level

    return indented_element


def strip_html(element: ET.Element) -> ET.Element:
    """Remove unnecessary whitespace from an HTML element and its children.

    Removes leading whitespace from elements' text.
    Doesn't strip elements inside the <pre> tag or inside inline tags.

    Args:
        element: The element to strip.

    Returns:
        An HTML element with stripped leading and trailing whitespace.
    """
    stripped_element = ET.Element(element.tag, attrib=element.attrib)
    stripped_element.text = element.text
    stripped_element.tail = element.tail

    if element.tag.lower() in TAGS_INLINE | TAGS_PREFORMATTED:
        for child in element:
            stripped_element.append(child)
    else:
        stripped_element.text = (
            stripped_element.text.lstrip()
            if stripped_element.text else
            stripped_element.text
        )

        has_children = len(element) > 0
        if stripped_element.text and not has_children:
            stripped_element.text = stripped_element.text.rstrip()

        for child in element:
            stripped_element.append(strip_html(child))

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
    """Serialize an HTML element and its children to a string.

    Serializes attributes with None values as boolean.

    Args:
        element: The HTML element.
        indent: If True, indent the element.
        space: Whitespace for indentation.
        strip: If True, strip unnecessary whitespace.

    Returns:
        A string with serialized HTML.
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

    ltag = element.tag.lower()
    closing_slash = "/" if ltag in TAGS_EMPTY else ""
    opening_tag = f"<{element.tag}{attrib}{closing_slash}>"

    if element.text is not None:
        text = element.text if ltag in TAGS_NOT_ESCAPED else _escape_cdata(element.text)
    else:
        text = ""

    children = "".join(serialize_html(e) for e in element)
    closing_tag = f"</{element.tag}>" if ltag not in TAGS_EMPTY else ""
    tail = _escape_cdata(element.tail) if element.tail is not None else ""

    return opening_tag + text + children + closing_tag + tail
