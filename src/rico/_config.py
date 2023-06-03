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
    "indent_html": False,
    "indent_space": "  ",
    "strip_html": False,
    "image_format": "svg",
    "inline_scripts": False,
    "inline_styles": False,
    "bootstrap_css": BOOTSTRAP_CSS,
    "bootstrap_js": "",
    "dataframe_style": DATAFRAME_STYLE,
}


def get_config(param: str | None = None) -> Any:
    """Get global configuration.

    Args:
        param: Paramater name.

    Returns:
        Parameter value if `param` is not None, or dict with all parameters otherwise.
    """
    config = _global_config.copy()
    if param is not None:
        return config[param]
    return config


def set_config(
    indent_html: bool | None = None,
    indent_space: str | None = None,
    strip_html: bool | None = None,
    image_format: Literal["svg", "png"] | None = None,
    inline_scripts: bool | None = None,
    inline_styles: bool | None = None,
    bootstrap_css: str | None = None,
    bootstrap_js: str | None = None,
    dataframe_style: str | None = None,
) -> None:
    """Set global configuration.

    Args:
        indent_html: Indent HTML elements in serialization methods.
        indent_space: Default indent space.
        strip_html: Strip HTML elements in serialization methods.
        image_format: Default chart image format.
        inline_scripts: If True then scripts are loaded inline.
        inline_styles: If True then styles are loaded inline.
        bootstrap_css: A link to a bootstrap css file.
            If empty then bootstrap css is not loaded.
        bootstrap_js: A link to a bootstrap javascript file.
            If empty then bootstrap javascript is not loaded.
        dataframe_style: A dataframe table stylesheet.
            If empty then it's not used.
    """
    for param, value in locals().items():
        if value is not None:
            _global_config[param] = value


@contextlib.contextmanager
def config_context(
    indent_html: bool | None = None,
    indent_space: str | None = None,
    strip_html: bool | None = None,
    image_format: Literal["svg", "png"] | None = None,
    inline_scripts: bool | None = None,
    inline_styles: bool | None = None,
    bootstrap_css: str | None = None,
    bootstrap_js: str | None = None,
    dataframe_style: str | None = None,
) -> Generator[None, Any, None]:
    """Context manager for configuration.

    Args:
        indent_html: Indent HTML elements in serialization methods.
        indent_space: Default indent space.
        strip_html: Strip HTML elements in serialization methods.
        image_format: Default chart image format.
        inline_scripts: If True then scripts are loaded inline.
        inline_styles: If True then styles are loaded inline.
        bootstrap_css: A link to a bootstrap css file.
            If empty then bootstrap css is not loaded.
        bootstrap_js: A link to a bootstrap javascript file.
            If empty then bootstrap javascript is not loaded.
        dataframe_style: A dataframe table stylesheet.
            If empty then it's not used.
    """
    new_config = locals()
    old_config = get_config()
    set_config(**new_config)

    try:
        yield
    finally:
        set_config(**old_config)
