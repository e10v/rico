# ruff: noqa: F401
# pyright: reportUnusedImport=false
"""Rich content to HTML as easy as `Doc(df, plot)`."""

from rico._config import config_context, get_config, set_config
from rico._container import (
    BOOTSTRAP_CSS,
    BOOTSTRAP_JS,
    BOOTSTRAP_VER,
    DATAFRAME_CLASS,
    Div,
    Doc,
)
from rico._content import (
    Chart,
    Code,
    ContentBase,
    HTML,
    Image,
    Markdown,
    Obj,
    Script,
    Style,
    Tag,
    Text,
)
from rico._html import HTMLParser, indent_html, parse_html, serialize_html, strip_html
from rico._version import __version__
