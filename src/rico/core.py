"""Core functions and classes."""

from __future__ import annotations

from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET  # noqa: N817

from rico import html


if TYPE_CHECKING:
    from typing import Any


class ContentBase:
    """Base content definition.

    Creates a container element on init.
    Defines serialization method and string representation.

    Attributes:
        container (Element): The container element.
    """

    def __init__(self, class_: str | None = None):
        """Initialize base content.

        Args:
            class_: The container element's class attribute.
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


class Tag(ContentBase):
    """Content definition based on tag parameters.

    Creates a content element based on tag parameters and appends it to the container.
    """

    def __init__(
        self,
        tag: str,
        text: str | None = None,
        tail: str | None = None,
        attrib: dict[str, Any] = {},
        class_: str | None = None,
        **extra: Any,
    ):
        """Initialize base content based on tag parameters.

        Args:
            tag: The content element's tag.
            text: Text before first subelement.
            tail: Text after the end tag.
            attrib: The tag's attributes.
            extra: Extra attributes.
            class_: The container class attribute.
        """
        super().__init__(class_)
        element = ET.Element(tag, attrib={**attrib, **extra})
        element.text = text
        element.tail = tail
        self.container.append(element)
