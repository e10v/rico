"""Core functions and classes."""

from __future__ import annotations

from abc import ABC, abstractmethod
import base64
import io
from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET  # noqa: N817

from rico import html


if TYPE_CHECKING:
    from typing import Any, Literal


try:
    import markdown
except ImportError:  # pragma: no cover
    markdown = None

try:
    import altair as alt
    import vl_convert as vlc  # type: ignore
    AltairChart = alt.TopLevelMixin  # type: ignore
except ImportError:  # pragma: no cover
    alt = None

    class AltairChart(ABC):  # noqa: D101
        @abstractmethod
        def to_json(self) -> str:  # noqa: D102
            ...

    class vlc(ABC):  # noqa: D101, N801
        @classmethod
        @abstractmethod
        def vegalite_to_svg(cls, *args: Any, **kwargs: Any) -> str:  # noqa: D102
            ...

        @classmethod
        @abstractmethod
        def vegalite_to_png(cls, *args: Any, **kwargs: Any) -> bytes:  # noqa: D102, E501
            ...

try:
    import matplotlib.pyplot as plt
    PyplotFigure = plt.Figure  # type: ignore
    PyplotAxes = plt.Axes  # type: ignore
except ImportError:  # pragma: no cover
    plt = None

    class PyplotFigure(ABC):  # noqa: D101
        @abstractmethod
        def savefig(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
            ...

    class PyplotAxes(ABC):  # noqa: D101
        @property
        @abstractmethod
        def figure(self) -> PyplotFigure:  # noqa: D102
            ...

try:
    import seaborn.objects as so
    SeabornPlot = so.Plot  # type: ignore
except ImportError:  # pragma: no cover
    so = None

    class SeabornPlot(ABC):  # noqa: D101
        @abstractmethod
        def save(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
            ...


class ContentBase:
    """A base content definition.

    Creates a container element on init.
    Defines serialization method and string representation.

    Attributes:
        container (Element): The container element.
    """
    container: ET.Element

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
    """A Tag content definition.

    Creates a content element using tag parameters and appends it to the container.
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
        """Initialize content using tag parameters.

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


class Text(ContentBase):
    """A Text content definition.

    Creates a content element from a text and appends it to the container.
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


class Code(ContentBase):
    """A Code content definition.

    Creates content elements from a code and appends it to the container.
    """
    def __init__(self, text: str, class_: str | None = None):
        """Initialize content from a code.

        Args:
            text: The code.
            class_: The container class attribute.
        """
        super().__init__(class_)
        pre = ET.Element("pre")
        code = ET.Element("code")
        code.text = text
        pre.append(code)
        self.container.append(pre)


class HTML(ContentBase):
    """An HTML content definition.

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


class Markdown(ContentBase):
    """A Markdown content definition.

    Creates content elements from a markdown text and appends it to the container.
    """
    def __init__(
        self,
        text: str,
        class_: str | None = None,
        **kwargs: Any,
    ):
        """Initialize content from a markdown text.

        Args:
            text: The markdown text.
            class_: The container class attribute.
            **kwargs: Keyword arguments passed to the `markdown.markdown` function.

        Raises:
            ImportError: The markdown package is not installed.
        """
        if markdown is None:
            raise ImportError("The markdown package is not installed.")  # pragma: no cover  # noqa: E501

        content = HTML(markdown.markdown(text, **kwargs), class_=class_)
        self.container = content.container


class Image(ContentBase):
    """An Image content definition.

    Creates content elements using an image data and appends it to the container.
    """
    def __init__(
        self,
        data: bytes | str,
        format: str,  # noqa: A002
        class_: str | None = None,
    ):
        """Initialize content using image data.

        Args:
            data: The image data.
            format: The image format.
            class_: The container class attribute.
        """
        super().__init__(class_)

        if format == "svg":
            if isinstance(data, bytes):
                data = data.decode()

            for element in html.parse_html(data):
                self.container.append(element)
        else:
            if isinstance(data, str):
                data = data.encode()
            encoded_image = base64.b64encode(data).decode()

            element = ET.Element(
                "img",
                attrib={"src": f"data:image/{format};base64,{encoded_image}"},
            )
            self.container.append(element)


class Chart(ContentBase):
    """An Chart content definition.

    Creates content elements from a chart object and appends it to the container.

    The supported chart types are the following:
    - Altair Chart,
    - Pyplot Axes and Figure,
    - Seaborn Plot (seaborn.objects interface).
    """
    def __init__(
        self,
        chart: AltairChart | PyplotAxes | PyplotFigure | SeabornPlot,
        format: Literal["svg", "png"] = "svg",  # noqa: A002
        class_: str | None = None,
        **kwargs: Any,
    ):
        """Initialize content from a chart object.

        Args:
            chart: The chart object.
            format: The image format.
            class_: The container class attribute.
            **kwargs: Keyword arguments passed to a function
                which converts object to an image.

        Raises:
            TypeError: Chart type is not supported
                or required extra package is not installed.
        """
        if plt is not None and isinstance(chart, PyplotAxes):
            chart = chart.figure

        if plt is not None and isinstance(chart, PyplotFigure):
            stream = io.StringIO() if format == "svg" else io.BytesIO()
            chart.savefig(stream, format=format, **kwargs)
            image = stream.getvalue()
        elif so is not None and isinstance(chart, SeabornPlot):
            stream = io.StringIO() if format == "svg" else io.BytesIO()
            chart.save(stream, format=format, **kwargs)
            image = stream.getvalue()
        elif alt is not None and isinstance(chart, AltairChart):
            convert = vlc.vegalite_to_svg if format == "svg" else vlc.vegalite_to_png
            image = convert(chart.to_json(), **kwargs)
        else:  # pragma: no cover
            error_msg = (
                f"Chart type {type(chart)} is not supported "
                "or required extra package is not installed."
            )
            raise TypeError(error_msg)

        content = Image(data=image, format=format, class_=class_)
        self.container = content.container
