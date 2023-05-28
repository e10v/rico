# ruff: noqa: ARG001
"""Global config."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any, Literal


_global_config = {
    "indent_html": False,
    "indent_space": "  ",
    "strip_html": False,
    "image_format": "svg",
    "inline_scripts": False,
    "inline_styles": False,
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
) -> None:
    """Set global configuration.

    Args:
        indent_html: Indent HTML elements in serialization methods.
        indent_space: Default indent space.
        strip_html: Strip HTML elements in serialization methods.
        image_format: Default chart image format.
        inline_scripts: If True, scripts are loaded inline.
        inline_styles: If True, styles are loaded inline.
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
) -> Generator[None, Any, None]:
    """Context manager for configuration.

    Args:
        indent_html: Indent HTML elements in serialization methods.
        indent_space: Default indent space.
        strip_html: Strip HTML elements in serialization methods.
        image_format: Default chart image format.
        inline_scripts: If True, scripts are loaded inline.
        inline_styles: If True, styles are loaded inline.
    """
    new_config = locals()
    old_config = get_config()
    set_config(**new_config)

    try:
        yield
    finally:
        set_config(**old_config)
