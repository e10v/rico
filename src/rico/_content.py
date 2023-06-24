# pyright: reportUnknownMemberType=false
"""Rich content classes."""

from __future__ import annotations

import base64
import io
from typing import TYPE_CHECKING
import urllib.request
import xml.etree.ElementTree as ET

import rico._config
import rico._html


if TYPE_CHECKING:
    from typing import Any, Literal


try:
    import altair as alt
    import vl_convert as vlc
except ImportError:
    alt = None

try:
    import markdown
except ImportError:
    markdown = None

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

try:
    import seaborn.objects as so
except ImportError:
    so = None


class ContentBase:
    """A base content definition.

    Creates a container element on init.
    Defines serialization method and string representation.

    Attributes:
        container (Element): The container element.
    """
    container: ET.Element

    def __init__(self, class_: str | None = None):
        """Create base content.

        Args:
            class_: The container element's class attribute.
        """
        attrib = {"class": class_} if class_ is not None else {}
        self.container = ET.Element("div", attrib=attrib)

    def serialize(
        self,
        indent: bool | None = None,
        space: str | None = None,
        strip: bool | None = None,
    ) -> str:
        """Serialize the object to string in HTML format.

        Indent the object if `indent_space` is not None.

        Args:
            indent: If True, indent the element.
            space: The whitespace for indentation.
            strip: If True, strip unnecessary whitespace.

        Returns:
            The serialized object.
        """
        return rico._html.serialize_html(
            self.container, indent=indent, space=space, strip=strip)

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
        """Create content using tag parameters.

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
        obj: Any,
        mono: bool | None = None,
        wrap: bool | None = None,
        class_: str | None = None,
    ):
        """Create content from a text.

        The default tag is <p> unless the text contains a line break.
        Then the <pre> tag is used.

        The `mono` and `wrap` parameters rely on Bootstrap CSS.

        Args:
            obj: The text. If it's not an instance of str, then it's converted to str.
            mono: If True then "font-monospace" class is assigned to the text element.
            wrap: If True then "text-wrap" class is assigned to the text element.
            class_: The container class attribute.
        """
        super().__init__(class_)

        global_config = rico._config.get_config()
        if mono is None:
            mono = global_config["text_mono"]
        if wrap is None:
            wrap = global_config["text_wrap"]

        if not isinstance(obj, str):
            obj = str(obj)

        text_class = " ".join([
            cl
            for cond, cl in [(mono, "font-monospace"), (wrap, "text-wrap")]
            if cond
        ])

        tag = "pre" if "\n" in obj else "p"
        attrib = {"class": text_class} if text_class else {}
        element = ET.Element(tag, attrib=attrib)
        element.text = obj
        self.container.append(element)


class Code(ContentBase):
    """A Code content definition.

    Creates content elements from a code and appends them to the container.
    """
    def __init__(self, text: str, class_: str | None = None):
        """Create content from a code.

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

    Creates content elements from an HTML text and appends them to the container.
    """
    def __init__(
        self,
        text: str,
        strip_dataframe_borders: bool = False,
        class_: str | None = None,
    ):
        """Create content from an HTML text.

        Args:
            text: The HTML text.
            strip_dataframe_borders: Delete borders attributes from dataframes.
            class_: The container class attribute.
        """
        super().__init__(class_)

        for element in rico._html.parse_html(text):
            self.container.append(element)

        if strip_dataframe_borders:
            for table in self.container.iterfind(
                './/table[@class="dataframe"][@border]',
            ):
                del table.attrib["border"]


class Markdown(ContentBase):
    """A Markdown content definition.

    Creates content elements from a markdown text and appends them to the container.
    """
    def __init__(
        self,
        text: str,
        class_: str | None = None,
        **kwargs: Any,
    ):
        """Create content from a markdown text.

        Args:
            text: The markdown text.
            class_: The container class attribute.
            **kwargs: Keyword arguments passed to the `markdown.markdown` function.

        Raises:
            ImportError: The markdown package is not installed.
        """
        if markdown is None:
            raise ImportError("The markdown package is not installed.")

        content = HTML(markdown.markdown(text, **kwargs), class_=class_)
        self.container = content.container


class Image(ContentBase):
    """An Image content definition.

    Creates content elements using an image data and appends them to the container.
    """
    def __init__(
        self,
        data: bytes | str,
        mime_subtype: str,
        class_: str | None = None,
    ):
        """Create content using image data.

        Args:
            data: The image data.
            mime_subtype: The image MIME subtype. Examples: "png", "svg+xml".
            class_: The container class attribute.
        """
        super().__init__(class_)

        if isinstance(data, str):
            data = data.encode()
        encoded_image = base64.b64encode(data).decode()

        element = ET.Element(
            "img",
            attrib={"src": f"data:image/{mime_subtype};base64,{encoded_image}"},
        )
        self.container.append(element)


class Plot(ContentBase):
    """A Plot content definition.

    Creates content elements from a plot object and appends them to the container.

    The supported plot types are the following:
    - Altair Chart,
    - Pyplot Axes and Figure,
    - Seaborn Plot (seaborn.objects interface).
    """
    def __init__(
        self,
        obj: Any,
        format: Literal["svg", "png"] | None = None,  # noqa: A002
        class_: str | None = None,
        **kwargs: Any,
    ):
        """Create content from a plot object.

        Args:
            obj: The plot object.
            format: The image format.
            class_: The container class attribute.
            **kwargs: Keyword arguments passed to a function
                which converts object to an image.

        Raises:
            TypeError: Plot type is not supported
                or required extra package is not installed.
        """
        if format is None:
            format = rico._config.get_config("image_format")  # noqa: A001

        if plt is not None and isinstance(obj, plt.Axes):
            obj = obj.figure

        if plt is not None and isinstance(obj, plt.Figure):  # type: ignore
            stream = io.StringIO() if format == "svg" else io.BytesIO()
            obj.savefig(stream, format=format, **kwargs)
            image = stream.getvalue()
        elif so is not None and isinstance(obj, so.Plot):
            stream = io.StringIO() if format == "svg" else io.BytesIO()
            obj.save(stream, format=format, **kwargs)
            image = stream.getvalue()
        elif alt is not None and isinstance(obj, alt.TopLevelMixin):
            convert = vlc.vegalite_to_svg if format == "svg" else vlc.vegalite_to_png  # type: ignore  # noqa: E501
            image = convert(  # type: ignore
                obj.to_json(),  # type: ignore
                vl_version="_".join(alt.SCHEMA_VERSION.split(".")[:2]),
                **kwargs,
            )
        else:
            error_msg = (
                f"Plot type {type(obj)} is not supported "
                "or required extra package is not installed."
            )
            raise TypeError(error_msg)

        mime_subtype = "svg+xml" if format == "svg" else format
        content = Image(data=image, mime_subtype=mime_subtype, class_=class_)  # type: ignore  # noqa: E501
        self.container = content.container

Chart = Plot


class Obj(ContentBase):
    """An arbitrary content definition.

    Creates content elements from arbitrary objects and appends them to the container.

    Automatically determines the content type.
    """
    def __init__(self, *objects: Any, class_: str | None = None):
        """Create content from arbitrary objects.

        Args:
            *objects: The objects which are used to create a content.
            class_: The container class attribute.
        """
        super().__init__(class_=class_)
        for obj in objects:
            if isinstance(obj, ContentBase):
                elements = (obj.container,)
            elif (
                alt is not None and isinstance(obj, alt.TopLevelMixin) or
                plt is not None and isinstance(obj, plt.Axes | plt.Figure) or  # type: ignore  # noqa: E501
                so is not None and isinstance(obj, so.Plot)
            ):
                elements = Plot(obj).container
            elif hasattr(obj, "_repr_html_") and callable(obj._repr_html_):
                elements = HTML(
                    obj._repr_html_(),
                    strip_dataframe_borders=True,
                ).container
            else:
                elements = Text(obj).container

            for element in elements:
                self.container.append(element)


class Script(ContentBase):
    """A script definition.

    Attributes:
        script (Element): The script element.
        footer (bool): Defines whether the script should be placed at a document footer,
            aftert all other content.
    """
    container: ET.Element
    footer: bool = False

    def __init__(
        self,
        text: str | None = None,
        src: str | None = None,
        inline: bool | None = None,
        defer: bool = False,
        attrib: dict[str, Any] = {},
        **extra: Any,
    ):
        """Create script.

        Either `text` or `src` should be used.

        Args:
            text: The script text.
            src: The script source link.
            inline: If True, load script inline, downdload it from source link
                and use it as a text.
            defer: The script "defer" attribute. For inline script defines whether
                it should be placed at a document footer, aftert all other content.
            attrib: The script attributes.
            **extra: Extra attributes.

        Raises:
            ValueError: Both text and src are not None.
            ValueError: Both text and src are None.
        """
        if inline is None:
            inline = rico._config.get_config("inline_scripts")

        if text is not None and src is not None:
            raise ValueError("Either `text` or `src` should be None.")

        if text is None and src is None:
            raise ValueError("Either `text` or `src` should be not None.")

        if inline and src is not None:
            with urllib.request.urlopen(src) as response:
                text = response.read().decode()
            src = None

        if src is not None:
            attrib = {"src": src, **attrib}
            if defer:
                attrib = {"defer": True, **attrib}
        else:
            self.footer = defer

        self.container = ET.Element("script", {**attrib, **extra})
        self.container.text = text


class Style(ContentBase):
    """A stylesheet definition.

    Attributes:
        style (Element): The style element.
    """
    container: ET.Element

    def __init__(
        self,
        text: str | None = None,
        src: str | None = None,
        inline: bool | None = None,
        attrib: dict[str, Any] = {},
        **extra: Any,
    ):
        """Create stylesheet.

        Either `text` or `src` should be used.

        Args:
            text: The stylesheet text.
            src: The stylesheet source link.
            inline: If True, load stylesheet inline, downdload it from source link
                and use it as a text.
            attrib: The stylesheet attributes.
            **extra: Extra attributes.

        Raises:
            ValueError: Both text and src are not None.
            ValueError: Both text and src are None.
        """
        if inline is None:
            inline = rico._config.get_config("inline_scripts")

        if text is not None and src is not None:
            raise ValueError("Either `text` or `src` should be None.")

        if text is None and src is None:
            raise ValueError("Either `text` or `src` should be not None.")

        if inline and src is not None:
            with urllib.request.urlopen(src) as response:
                text = response.read().decode()
            src = None

        if src is not None:
            tag = "link"
            attrib = {"href": src, **attrib}
            if "rel" not in attrib:
                attrib = {**attrib, "rel": "stylesheet"}
        else:
            tag = "style"

        self.container = ET.Element(tag, {**attrib, **extra})
        self.container.text = text
