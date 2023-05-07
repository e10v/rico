"""Core functions and classes."""

from __future__ import annotations

from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET  # noqa: N817


if TYPE_CHECKING:
    from typing import Any


def create_element(
    tag: str,
    parent: ET.Element | None = None,
    text: str | None = None,
    tail: str | None = None,
    attrib: dict[str, Any] = {},
    **extra: Any,
) -> ET.Element:
    """Creates an element of a HTML document.

    Convenient wrapper for ET.Element and ET.SubElement.

    Args:
        tag: HTML tag, element type.
        parent: Parent element.
        text: Text between opening and closing tags.
        tail: Text after closing tag.
        attrib: A dictionary containing the element's attributes.
        extra: Extra attributes.

    Returns:
        An element of a HTML document.
    """
    if parent is not None:
        element = ET.SubElement(parent, tag, attrib={**attrib, **extra})
    else:
        element = ET.Element(tag, attrib={**attrib, **extra})

    element.text = text
    element.tail = tail
    return element
