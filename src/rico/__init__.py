# ruff: noqa: F401
# pyright: reportUnusedImport=false
"""Rich content to HTML as easy as doc.print(x)."""

from rico._version import __version__
from rico.content import (
    Chart,
    Code,
    Content,
    ContentBase,
    HTML,
    Image,
    Markdown,
    Tag,
    Text,
)
from rico.html import (
    HTMLParser,
    indent_html,
    parse_html,
    serialize_html,
    strip_html,
)
