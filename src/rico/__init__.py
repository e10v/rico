# ruff: noqa: F401
# pyright: reportUnusedImport=false
"""Rich content to HTML as easy as Doc([df, plot])."""

from rico._content import (
    Chart,
    Code,
    Content,
    ContentBase,
    HTML,
    Image,
    Markdown,
    Script,
    Style,
    Tag,
    Text,
)
from rico._html import HTMLParser, indent_html, parse_html, serialize_html, strip_html
from rico._version import __version__
