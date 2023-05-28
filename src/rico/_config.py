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
    "chart_format": "svg",
    "image_format": "svg",
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
    chart_format: Literal["svg", "png"] | None = None,
    image_format: str | None = None,
) -> None:
    """Set global configuration.

    Args:
        indent_html: Indent HTML elements in serialization methods.
        indent_space: Default indent space.
        strip_html: Strip HTML elements in serialization methods.
        chart_format: Default chart image format.
        image_format: Default image format.
    """
    for param, value in locals().items():
        if value is not None:
            _global_config[param] = value


@contextlib.contextmanager
def config_context(
    indent_html: bool | None = None,
    indent_space: str | None = None,
    strip_html: bool | None = None,
    chart_format: Literal["svg", "png"] | None = None,
    image_format: str | None = None,
) -> Generator[None, Any, None]:
    """Context manager for configuration.

    Args:
        indent_html: Indent HTML elements in serialization methods.
        indent_space: Default indent space.
        strip_html: Strip HTML elements in serialization methods.
        chart_format: Default chart image format.
        image_format: Default image format.
    """
    new_config = locals()
    old_config = get_config()
    set_config(**new_config)

    try:
        yield
    finally:
        set_config(**old_config)
