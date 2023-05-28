"""Container classes."""

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET

import rico._content


if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any


BOOTSTRAP_VER = "5.2"
BOOTSTRAP_STYLE= f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VER}/dist/css/bootstrap.min.css"
BOOTSTRAP_SCRIPT = f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VER}/dist/js/bootstrap.min.js"

DATAFRAME_STYLE = rico._content.Style(text=textwrap.dedent("""\
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


class Doc(Div):
    def __init__(
        self,
        *objects: Any,
        title: str | None = None,
        styles: Iterable[rico._content.Style | str] | None = (
            BOOTSTRAP_STYLE, DATAFRAME_STYLE),
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
