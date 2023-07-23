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

    _ReprResult = str | bytes | dict[str, str | bytes]


try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


class ContentBase:
    container: ET.Element

    def __init__(self, class_: str | None = None):
        """Create an empty <div> container.

        Args:
            class_: The container class attribute.
        """
        attrib = {"class": class_} if class_ is not None else {}
        self.container = ET.Element("div", attrib=attrib)

    def serialize(
        self,
        indent: bool | None = None,
        space: str | None = None,
        strip: bool | None = None,
    ) -> str:
        """Serialize the object's HTML elements to a string.

        Args:
            indent: If True, indent the elements.
            space: Whitespace for indentation.
            strip: If True, strip unnecessary whitespace.

        Returns:
            A string with serialized HTML.
        """
        return rico._html.serialize_html(
            self.container, indent=indent, space=space, strip=strip)

    def __str__(self) -> str:
        """Serialize the object's HTML elements to a string."""
        return self.serialize()


class Tag(ContentBase):
    def __init__(
        self,
        tag: str,
        text: str | None = None,
        tail: str | None = None,
        attrib: dict[str, Any] = {},
        class_: str | None = None,
        **extra: Any,
    ):
        """Create an HTML element using tag parameters and wrap it in a <div> container.

        Args:
            tag: The tag name.
            text: Text before first subelement.
            tail: Text after the closing tag.
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
    def __init__(
        self,
        obj: Any,
        mono: bool | None = None,
        wrap: bool | None = None,
        class_: str | None = None,
    ):
        """Create an HTML element from text and wrap it in a <div> container.

        The default tag is <p> if the text doesn't contains a line break.
        Otherwise, the <pre> tag is used.

        The `mono` and `wrap` parameters rely on Bootstrap CSS.

        Args:
            obj: The text. If it's not an instance of str, then it's converted to str.
            mono: If True, set the text font to monospaced.
            wrap: If True, wrap the text.
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
    def __init__(self, text: str, class_: str | None = None):
        """Create HTML elements from code and wrap them in a <div> container.

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
    def __init__(
        self,
        text: str,
        strip_dataframe_borders: bool = True,
        class_: str | None = None,
    ):
        """Create HTML elements from raw HTML and wrap them in a <div> container.

        Args:
            text: A string with raw HTML.
            strip_dataframe_borders: If True, remove borders attributes from dataframes.
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
    def __init__(
        self,
        text: str,
        class_: str | None = None,
        **kwargs: Any,
    ):
        """Create HTML elements from Markdown text and wrap them in a <div> container.

        Args:
            text: The Markdown text.
            class_: The container class attribute.
            **kwargs: Keyword arguments passed to the `markdown.markdown` function.

        Raises:
            RuntimeError: The markdown renderer is not defined.
        """
        md_renderer = rico._config.get_config("markdown_renderer")
        if md_renderer is None:
            raise RuntimeError("The markdown renderer is not defined.")

        content = HTML(md_renderer(text, **kwargs), class_=class_)
        self.container = content.container


class Image(ContentBase):
    def __init__(
        self,
        data: bytes | str,
        mime_subtype: str,
        class_: str | None = None,
    ):
        """Create an HTML element from image data and wrap it in a <div> container.

        The image is byte64-encoded.

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
    def __init__(
        self,
        obj: Any,
        format: Literal["svg", "png"] | None = None,  # noqa: A002
        class_: str | None = None,
        **kwargs: Any,
    ):
        """Create an HTML element from a plot object and wrap it in a <div> container.

        Args:
            obj: The Matplotlib Pyplot Axes or Figure object.
            format: Image format.
            class_: The container class attribute.
            **kwargs: Keyword arguments passed to the `savefig` method.

        Raises:
            ImportError: Matplotlib is not installed.
            TypeError: The object type should be an instance of plt.Figure or plt.Axes.
        """
        if plt is None:
            raise ImportError("Matplotlib is not installed.")

        if not isinstance(obj, plt.Figure | plt.Axes):  # type: ignore
            raise TypeError(
                "The object type should be an instance of plt.Figure or plt.Axes.")

        if format is None:
            format = rico._config.get_config("image_format")  # noqa: A001

        if isinstance(obj, plt.Axes):
            obj = obj.figure

        stream = io.StringIO() if format == "svg" else io.BytesIO()
        obj.savefig(stream, format=format, **kwargs)
        image = stream.getvalue()

        mime_subtype = "svg+xml" if format == "svg" else "png"
        content = Image(data=image, mime_subtype=mime_subtype, class_=class_)
        self.container = content.container


class Script(ContentBase):
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
        """Create an HTML script element.

        Either `text` or `src` should be used.

        Keep in mind that script files can contain links to other external resources.
        **rico** doesn't parse or change them, even if the `inline` parameter is set
        to `True`.
        As a result:
        * These resurces should be availble when someone opens an HTML document.
        * Links with relative paths to external resources will not work.

        Args:
            text: The script text.
            src: The script source link.
            inline: If True, load script inline, downdload it from source link
                and use it as `text`.
            defer: The "defer" attribute of the script. For an inline script, defines
                whether it should be placed in the footer of the document aftert all
                other content.
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
    def __init__(
        self,
        text: str | None = None,
        src: str | None = None,
        inline: bool | None = None,
        attrib: dict[str, Any] = {},
        **extra: Any,
    ):
        """Create an HTML style element.

        Either `text` or `src` should be used.

        Keep in mind that style files can contain links to other external resources.
        **rico** doesn't parse or change them, even if the `inline` parameter is set
        to `True`.
        As a result:
        * These resurces should be availble when someone opens an HTML document.
        * Links with relative paths to external resources will not work.

        Args:
            text: The stylesheet text.
            src: The stylesheet source link.
            inline: If True, load stylesheet inline, downdload it from source link
                and use it as `text`.
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


def _call_repr(
    obj: Any,
    repr_name: str,
    mime_type: str = "text/plain",
) -> dict[str, str | bytes]:
    if hasattr(obj, repr_name):
        repr_fn = getattr(obj, repr_name)
        if callable(repr_fn):
            data : _ReprResult | tuple[_ReprResult, _ReprResult] | None = repr_fn()
            if isinstance(data, tuple):
                data = data[0]
            if data is None:
                return {}
            if not isinstance(data, dict):
                return {mime_type: data}
            return data
    return {}

def _decode(data: str | bytes) -> str:
    return data.decode() if isinstance(data, bytes) else data

def _get_repr(obj: Any) -> ContentBase:  # noqa: C901, PLR0911, PLR0912
    data = {k.lower(): v for k, v in _call_repr(obj, "_repr_mimebundle_").items()}

    if data == {}:
        data = _call_repr(obj, "_repr_javascript_", "application/javascript")
    if data == {}:
        data = _call_repr(obj, "_repr_html_", "text/html")
    if data == {}:
        data = _call_repr(obj, "_repr_markdown_", "text/markdown")
    if data == {}:
        data = _call_repr(obj, "_repr_svg_", "image/svg+xml")
    if data == {}:
        data = _call_repr(obj, "_repr_png_", "image/png")
    if data == {}:
        data = _call_repr(obj, "_repr_jpeg_", "image/jpeg")

    if "application/javascript" in data and data["application/javascript"]:
        return Script(_decode(data["application/javascript"]))
    if "text/html" in data and data["text/html"]:
        return HTML(_decode(data["text/html"]), strip_dataframe_borders=True)
    if "text/markdown" in data and data["text/markdown"]:
        return Markdown(_decode(data["text/markdown"]))
    if "image/svg+xml" in data and data["image/svg+xml"]:
        return Image(data["image/svg+xml"], "svg+xml")
    if "image/png" in data and data["image/png"]:
        return Image(data["image/png"], "png")
    if "image/jpeg" in data and data["image/jpeg"]:
        return Image(data["image/jpeg"], "jpeg")
    if "image/gif" in data and data["image/gif"]:
        return Image(data["image/gif"], "gif")
    if "text/plain" in data and data["text/plain"]:
        return Text(data["text/plain"])
    return Text(str(obj))

class Obj(ContentBase):
    def __init__(self, *objects: Any, class_: str | None = None):
        """Create HTML elements from objects and wrap them in a <div> container.

        Automatically determines the content type in the following order:
        1. `rico` content classes (subclasses of `ContentBase`).
        2. Matplotlib Pyplot.
        3. Dataframes and other types IPython rich replresentation methods.
        All other types are converted to text.

        More about IPython rich representation methods:
        https://ipython.readthedocs.io/en/stable/config/integrating.html

        Args:
            *objects: The objects.
            class_: The container class attribute.
        """
        super().__init__(class_=class_)
        for obj in objects:
            if isinstance(obj, ContentBase):
                content = obj
            elif plt is not None and isinstance(obj, plt.Axes | plt.Figure):  # type: ignore  # noqa: E501
                content = Plot(obj)
            else:
                content = _get_repr(obj)
            self.container.append(content.container)
