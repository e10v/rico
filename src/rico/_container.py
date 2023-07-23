"""Container classes."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET

import rico._config
import rico._content
import rico._html


if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Any, Concatenate, Literal, ParamSpec

    P = ParamSpec("P")


def _append(
    content_type: type[rico._content.ContentBase],
    init: Callable[Concatenate[Any, P], None],
) -> Callable[Concatenate[Any, P], None]:
    @functools.wraps(init)
    def method(
        self: Any,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        content = content_type(*args, **kwargs)
        self.container.append(content.container)

    return method

class Div(rico._content.Obj):
    def __init__(self, *objects: Any, class_: str | None = None):
        """Create a <div> container, create HTML elements and add them to the container.

        Each HTML element is also wrapped in a separate <div> container.

        Args:
            *objects: Objects that are used to create HTML elements.
            class_: The container class attribute.
        """
        super().__init__(*objects, class_=class_)

    append_tag = _append(rico._content.Tag, rico._content.Tag.__init__)
    append_text = _append(rico._content.Text, rico._content.Text.__init__)
    append_code = _append(rico._content.Code, rico._content.Code.__init__)
    append_html = _append(rico._content.HTML, rico._content.HTML.__init__)
    append_markdown = _append(rico._content.Markdown, rico._content.Markdown.__init__)
    append_image = _append(rico._content.Image, rico._content.Image.__init__)
    append_plot = _append(rico._content.Plot, rico._content.Plot.__init__)
    append = _append(rico._content.Obj, rico._content.Obj.__init__)


class Doc(Div):
    html: ET.Element
    head: ET.Element
    body: ET.Element

    def __init__(
        self,
        *objects: Any,
        title: str | None = None,
        bootstrap: Literal["css", "full", "none"] = "css",
        extra_styles: Iterable[rico._content.Style] = (),
        extra_scripts: Iterable[rico._content.Script] = (),
        class_: str | None = "container",
    ):
        """Create an HTML document.

        Creates a <div> container inside the <body> element.
        Create HTML elements and add them to the container.
        Each HTML element is also wrapped in a separate <div> container.

        Args:
            *objects: Objects that are used to create HTML elements.
            title: The document title.
            bootstrap: Defines which Bootatrap files are included in the document.
                If "css", include only CSS.
                If "full", include both the CSS and JS.
                If "none", don'e include Bootstrap.
            extra_styles: Extra styles to include in the document.
            extra_scripts: Extra scripts to include in the document.
            class_: The container class attribute.
        """
        super().__init__(*objects, class_=class_)
        self.html = ET.Element("html")
        self.head = ET.Element("head")
        self.body = ET.Element("body")
        self.html.append(self.head)
        self.html.append(self.body)
        self.body.append(self.container)

        if title is not None:
            title_element = ET.Element("title")
            title_element.text = title
            self.head.append(title_element)

        global_config = rico._config.get_config()
        if global_config["meta_charset"]:
            self.head.append(ET.Element("meta", charset=global_config["meta_charset"]))
        if global_config["meta_viewport"]:
            self.head.append(ET.Element(
                "meta",
                name="viewport",
                content=global_config["meta_viewport"],
            ))

        styles : list[rico._content.Style] = []
        scripts : list[rico._content.Script] = []

        if bootstrap.lower() in {"css", "full"}:
            styles.append(rico._content.Style(src=global_config["bootstrap_css"]))
        if bootstrap.lower() == "full":
            scripts.append(rico._content.Script(src=global_config["bootstrap_js"]))
        if global_config["dataframe_style"]:
            styles.append(rico._content.Style(text=global_config["dataframe_style"]))

        for style in (*styles, *extra_styles):
            self.head.append(style.container)

        for script in (*scripts, *extra_scripts):
            if script.footer:
                self.body.append(script.container)
            else:
                self.head.append(script.container)

    def serialize(
        self,
        indent: bool | None = None,
        space: str | None = None,
        strip: bool | None = None,
    ) -> str:
        """Serialize the HTML document to s string.

        Args:
            indent: If True, indent the elements.
            space: Whitespace for indentation.
            strip: If True, strip unnecessary whitespace.

        Returns:
            A string with serialized HTML.
        """
        return "<!doctype html>\n" + rico._html.serialize_html(
            self.html, indent=indent, space=space, strip=strip)
