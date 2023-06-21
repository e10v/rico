# ruff: noqa: ARG001, PLR0913
"""Global config."""

from __future__ import annotations

import contextlib
import textwrap
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any, Literal


BOOTSTRAP_VER = "5"
BOOTSTRAP_CSS= f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VER}/dist/css/bootstrap.min.css"
BOOTSTRAP_JS = f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VER}/dist/js/bootstrap.min.js"

DATAFRAME_STYLE = textwrap.dedent("""\
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
""")


_global_config = {
    "bootstrap_css": BOOTSTRAP_CSS,
    "bootstrap_js": BOOTSTRAP_JS,
    "dataframe_style": DATAFRAME_STYLE,
    "image_format": "svg",
    "indent_html": False,
    "indent_space": "  ",
    "inline_scripts": False,
    "inline_styles": False,
    "meta_charset": "utf-8",
    "meta_viewport": "width=device-width, initial-scale=1",
    "strip_html": False,
    "text_mono": False,
    "text_wrap": False,
}


def get_config(param: str | None = None) -> Any:
    """Get global configuration.

    Args:
        param: Paramater name.

    Returns:
        Parameter value if `param` is not None, or dict with all parameters otherwise.
    """
    if param is not None:
        return _global_config[param]
    return _global_config.copy()


def set_config(
    bootstrap_css: str | None = None,
    bootstrap_js: str | None = None,
    dataframe_style: str | None = None,
    image_format: Literal["svg", "png"] | None = None,
    indent_html: bool | None = None,
    indent_space: str | None = None,
    inline_scripts: bool | None = None,
    inline_styles: bool | None = None,
    meta_charset: str | None = None,
    meta_viewport: str | None = None,
    strip_html: bool | None = None,
    text_mono: bool | None = None,
    text_wrap: bool | None = None,
) -> None:
    """Set global configuration.

    Args:
        bootstrap_css: A link to a bootstrap css file.
            If empty then bootstrap css is not loaded.
        bootstrap_js: A link to a bootstrap javascript file.
            If empty then bootstrap javascript is not loaded.
        dataframe_style: A dataframe table stylesheet.
            If empty then it's not used.
        image_format: Default plot image format.
        indent_html: Indent HTML elements in serialization methods.
        indent_space: Default indent space.
        inline_scripts: If True then scripts are loaded inline.
        inline_styles: If True then styles are loaded inline.
        meta_charset: An HTML document charset.
            If empty then it's not used.
        meta_viewport: An HTML document viewport property.
            If empty then it's not used.
        strip_html: Strip HTML elements in serialization methods.
        text_mono: Default value for the `mono` arg of the Text class.
        text_wrap: Default value for the `wrap` arg of the Text class.
    """
    for param, value in locals().items():
        if value is not None:
            _global_config[param] = value


@contextlib.contextmanager
def config_context(
    bootstrap_css: str | None = None,
    bootstrap_js: str | None = None,
    dataframe_style: str | None = None,
    image_format: Literal["svg", "png"] | None = None,
    indent_html: bool | None = None,
    indent_space: str | None = None,
    inline_scripts: bool | None = None,
    inline_styles: bool | None = None,
    meta_charset: str | None = None,
    meta_viewport: str | None = None,
    strip_html: bool | None = None,
    text_mono: bool | None = None,
    text_wrap: bool | None = None,
) -> Generator[None, Any, None]:
    """Context manager for configuration.

    Args:
        bootstrap_css: A link to a bootstrap css file.
            If empty then bootstrap css is not loaded.
        bootstrap_js: A link to a bootstrap javascript file.
            If empty then bootstrap javascript is not loaded.
        dataframe_style: A dataframe table stylesheet.
            If empty then it's not used.
        image_format: Default plot image format.
        indent_html: Indent HTML elements in serialization methods.
        indent_space: Default indent space.
        inline_scripts: If True then scripts are loaded inline.
        inline_styles: If True then styles are loaded inline.
        meta_charset: An HTML document charset.
            If empty then it's not used.
        meta_viewport: An HTML document viewport property.
            If empty then it's not used.
        strip_html: Strip HTML elements in serialization methods.
        text_mono: Default value for the `mono` arg of the Text class.
        text_wrap: Default value for the `wrap` arg of the Text class.
    """
    new_config = locals()
    old_config = get_config()
    set_config(**new_config)

    try:
        yield
    finally:
        set_config(**old_config)
