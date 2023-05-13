"""Core functions and classes."""

from __future__ import annotations

import xml.etree.ElementTree as ET  # noqa: N817

from rico import html


class ContentBase:
    """Base class for an HTML content.

    Creates the container element on init.
    Defines serialization method.

    Attributes:
        container (Element): The container element.
    """

    def __init__(self, class_: str | None = None):
        """Initialize an instance of the ContentBase.

        Create the container element.

        Args:
            class_: The container class attribute.
        """
        attrib = {"class": class_} if class_ is not None else {}
        self.container = ET.Element("div", attrib=attrib)

    def serialize(self, indent_space: str | None = None) -> str:
        """Serialize the object to string in HTML format.

        Indent the object if `indent_space` is not None.

        Args:
            indent_space: The whitespace for indentation.

        Returns:
            The serialized object.
        """
        return html.serialize_html(self.container, indent_space=indent_space)

    def __str__(self) -> str:
        """Serialize the object to string in HTML format."""
        return self.serialize()
