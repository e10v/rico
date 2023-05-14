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
    """Content definition with tag parameters.

    Creates a content element from tag parameters and appends it to the container.
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
        """Initialize content from tag parameters.

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


class HTML(ContentBase):
    """Content definition with an HTML text.

    Creates content elements from an HTML text and appends it to the container.
    """
    def __init__(
        self,
        data: str,
        strip_dataframe_borders: bool = False,
        class_: str | None = None,
    ):
        """Initialize content from an HTML text.

        Args:
            data: The HTML text.
            strip_dataframe_borders: Delete borders attributes from dataframes.
            class_: The container class attribute.
        """
        super().__init__(class_)
        for element in html.parse_html(data):
            if strip_dataframe_borders:
                if (
                    element.tag == "table" and
                    "dataframe" in element.get("class", "") and
                    "border" in element.attrib
                ):
                    del element.attrib["border"]

                for table in element.iterfind('table[@class="dataframe"][@border]'):
                    del table.attrib["border"]

            self.container.append(element)


class Text(ContentBase):
    """Content definition with a text.

    Creates content elements from a text and appends it to the container.
    """
    def __init__(
        self,
        text: Any,
        mono: bool = False,
        wrap: bool = False,
        class_: str | None = None,
    ):
        """Initialize content from a text.

        The default tag is <p> unless the text contains a line break.
        Then the <pre> tag is used.

        The `mono` and `wrap` parameters rely on Bootstrap CSS.

        Args:
            text: The text. If it's not an instance of str, then it's converted to str.
            mono: If True then "font-monospace" class is assigned to the text element.
            wrap: If True then "text-wrap" class is assigned to the text element.
            class_: The container class attribute.
        """
        super().__init__(class_)

        if not isinstance(text, str):
            text = str(text)

        text_class = " ".join([
            cl
            for cond, cl in [(mono, "font-monospace"), (wrap, "text-wrap")]
            if cond
        ])

        tag = "pre" if "\n" in text else "p"
        attrib = {"class": text_class} if text_class else {}
        element = ET.Element(tag, attrib=attrib)
        element.text = text
        self.container.append(element)
