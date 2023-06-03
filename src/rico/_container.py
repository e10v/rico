"""Container classes."""

from __future__ import annotations

import functools
import textwrap
from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET

import rico._content


if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Any, Concatenate, ParamSpec

    P = ParamSpec("P")


BOOTSTRAP_VER = "5.2"
BOOTSTRAP_CSS= f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VER}/dist/css/bootstrap.min.css"
BOOTSTRAP_JS = f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VER}/dist/js/bootstrap.min.js"

DATAFRAME_CLASS = rico._content.Style(text=textwrap.dedent("""\
    .dataframe table {
        border: none;
        border-collapse: collapse;
        border-spacing: 0;
        margin-bottom: 1em;
        margin-left: 0;
        margin-right: 0;
    }

    .dataframe thead {
        border-bottom: var(--bs-border-width) solid var(--bs-border-color);
        vertical-align: bottom;
    }

    .dataframe td,
    .dataframe th,
    .dataframe tr {
        border: none;
        line-height: var(--bs-body-line-height);
        max-width: none;
        padding: .25rem .5rem;
        text-align: right;
        vertical-align: middle;
        white-space: normal;
    }

    .dataframe th {
        font-weight: bold;
    }
"""))


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


class Div(rico._content.ContentBase):
    """A <div> container definition.

    Creates <div> container with content based on arbitrary objects.
    """
    def __init__(self, *objects: Any, class_: str | None = None):
        """Initialize <div> container with content from arbitrary objects.

        Args:
            *objects: The objects which are used to create a content.
            class_: The container class attribute.
        """
        super().__init__(class_=class_)
        for obj in objects:
            if isinstance(obj, rico._content.ContentBase):
                self.container.append(obj.container)
            else:
                self.container.append(rico._content.Obj(obj).container)

    append_tag = _append(rico._content.Tag, rico._content.Tag.__init__)
    append_text = _append(rico._content.Text, rico._content.Text.__init__)
    append_code = _append(rico._content.Code, rico._content.Code.__init__)
    append_html = _append(rico._content.HTML, rico._content.HTML.__init__)
    append_markdown = _append(rico._content.Markdown, rico._content.Markdown.__init__)
    append_image = _append(rico._content.Image, rico._content.Image.__init__)
    append_chart = _append(rico._content.Chart, rico._content.Chart.__init__)
    append = _append(rico._content.Obj, rico._content.Obj.__init__)


class Doc(Div):
    def __init__(
        self,
        *objects: Any,
        title: str | None = None,
        styles: Iterable[rico._content.Style | str] | None = (
            BOOTSTRAP_CSS, DATAFRAME_CLASS),
        scripts: Iterable[rico._content.Script | str] | None = None,
        class_: str | None = "container",
    ):
        super().__init__(*objects, class_=class_)
        self.html = ET.Element("html")
        self.head = ET.Element("head")
        self.body = ET.Element("body")
        self.html.append(self.head)
        self.html.append(self.body)
        self.body.append(self.container)

        self.head.append(ET.Element("meta", charset="utf-8"))
        self.head.append(ET.Element(
            "meta",
            name="viewport",
            content="width=device-width, initial-scale=1",
        ))

        if title is not None:
            title_element = ET.Element("title")
            title_element.text = title
            self.head.append(title_element)