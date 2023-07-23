# ruff: noqa: F401
# pyright: reportUnusedImport=false
"""Rich content to HTML as easy as Doc(df, plot).

A Python package for creating HTML documents from rich content:
dataframes, plots, images, markdown etc.
It provides a high-level, easy-to-use API with reasonable defaults,
as well as low-level access for better control.
"""

from rico._config import config_context, get_config, set_config
from rico._container import Div, Doc
from rico._content import (
    Code,
    ContentBase,
    HTML,
    Image,
    Markdown,
    Obj,
    Plot,
    Script,
    Style,
    Tag,
    Text,
)
from rico._html import indent_html, parse_html, serialize_html, strip_html
from rico._version import __version__
