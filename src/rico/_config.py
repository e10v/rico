# ruff: noqa: ARG001, PLR0913
"""Global config."""

from __future__ import annotations

import contextlib
import textwrap
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from typing import Any, Literal


try:
    import markdown_it
    md_renderer = markdown_it.MarkdownIt().render
except ImportError:
    try:
        import markdown
        md_renderer = markdown.markdown
    except ImportError:
        md_renderer = None


BOOTSTRAP_BASE = "https://cdn.jsdelivr.net/npm/bootstrap@5/dist/"
BOOTSTRAP_CSS = BOOTSTRAP_BASE + "css/bootstrap.min.css"
BOOTSTRAP_JS = BOOTSTRAP_BASE + "js/bootstrap.min.js"

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
    "markdown_renderer": md_renderer,
    "meta_charset": "utf-8",
    "meta_viewport": "width=device-width, initial-scale=1",
    "strip_html": False,
    "text_mono": False,
    "text_wrap": False,
}


def get_config(option: str | None = None) -> Any:
    """Get global configuration.

    Args:
        option: The option name.

    Returns:
        The value of the option if it's not None,
        or a dictionary with all options otherwise.
    """
    if option is not None:
        return _global_config[option]
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
    markdown_renderer: Callable[..., str] | None = None,
    meta_charset: str | None = None,
    meta_viewport: str | None = None,
    strip_html: bool | None = None,
    text_mono: bool | None = None,
    text_wrap: bool | None = None,
) -> None:
    """Set global configuration.

    Args:
        bootstrap_css: A link to the Bootstrap CSS file.
            If empty, then the Bootstrap CSS is not loaded.
        bootstrap_js: A link to the Bootstrap JS file.
            If empty, then the Bootstrap JS is not loaded.
        dataframe_style: A dataframe style. If empty, then it's not used.
        image_format: Default plot image format.
        indent_html: Default value of the `indent` parameter for serialization methods.
            If True, indent the elements.
        indent_space: Default value of the `space` parameter for serialization methods.
            Whitespace for indentation.
        inline_scripts: Default value of the `inline` parameter of the Script class.
            If True, load script inline, downdload it from source link.
        inline_styles: Default value of the `inline` parameter of the Style class.
            If True, load stylesheet inline, downdload it from source link.
        markdown_renderer: A callable that converts Markdown to HTML.
            Should accept a Markdown string as the first argument and
            return HTML as a string.
        meta_charset: HTML document charset. If empty, then it's not used.
        meta_viewport: HTML document viewport property. If empty, then it's not used.
        strip_html: Default value of the `strip` parameter for serialization methods.
            If True, strip unnecessary whitespace.
        text_mono: Default value of the `mono` parameter of the Text class.
            If True, set the text font to monospaced.
        text_wrap: Default value of the `wrap` parameter of the Text class.
            If True, wrap the text.
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
    markdown_renderer: Callable[..., str] | None = None,
    meta_charset: str | None = None,
    meta_viewport: str | None = None,
    strip_html: bool | None = None,
    text_mono: bool | None = None,
    text_wrap: bool | None = None,
) -> Generator[None, Any, None]:
    """Context manager for configuration.

    Args:
        bootstrap_css: A link to the Bootstrap CSS file.
            If empty, then the Bootstrap CSS is not loaded.
        bootstrap_js: A link to the Bootstrap JS file.
            If empty, then the Bootstrap JS is not loaded.
        dataframe_style: A dataframe style. If empty, then it's not used.
        image_format: Default plot image format.
        indent_html: Default value of the `indent` parameter for serialization methods.
            If True, indent the elements.
        indent_space: Default value of the `space` parameter for serialization methods.
            Whitespace for indentation.
        inline_scripts: Default value of the `inline` parameter of the Script class.
            If True, load script inline, downdload it from source link.
        inline_styles: Default value of the `inline` parameter of the Style class.
            If True, load stylesheet inline, downdload it from source link.
        markdown_renderer: A callable that converts Markdown to HTML.
            Should accept a Markdown string as the first argument and
            return HTML as a string.
        meta_charset: HTML document charset. If empty, then it's not used.
        meta_viewport: HTML document viewport property. If empty, then it's not used.
        strip_html: Default value of the `strip` parameter for serialization methods.
            If True, strip unnecessary whitespace.
        text_mono: Default value of the `mono` parameter of the Text class.
            If True, set the text font to monospaced.
        text_wrap: Default value of the `wrap` parameter of the Text class.
            If True, wrap the text.
    """
    new_config = locals()
    old_config = get_config()
    set_config(**new_config)

    try:
        yield
    finally:
        set_config(**old_config)
