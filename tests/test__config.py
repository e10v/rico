# pyright: reportPrivateUsage=false
from __future__ import annotations

import importlib
from typing import TYPE_CHECKING
import unittest.mock

import markdown
import markdown_it
import pytest

import rico._config


if TYPE_CHECKING:
    from collections.abc import Callable, Generator
    from typing import Any


def assert_fn_eq(fn1: Callable[..., Any], fn2: Callable[..., Any]) -> None:
    assert fn1.__annotations__ == fn2.__annotations__
    assert fn1.__code__ == fn2.__code__
    assert fn1.__defaults__ == fn2.__defaults__
    assert fn1.__dict__ == fn2.__dict__
    assert fn1.__doc__ == fn2.__doc__
    assert fn1.__kwdefaults__ == fn2.__kwdefaults__
    assert fn1.__module__ == fn2.__module__
    assert fn1.__name__ == fn2.__name__
    assert fn1.__qualname__ == fn2.__qualname__

def test_markdown_import():
    md_renderer = rico._config._global_config["markdown_renderer"]
    assert callable(md_renderer)
    assert_fn_eq(md_renderer, markdown_it.MarkdownIt().render)

    with unittest.mock.patch.dict("sys.modules", {"markdown_it": None}):
        importlib.reload(rico._config)
        md_renderer = rico._config._global_config["markdown_renderer"]
        assert callable(md_renderer)
        assert_fn_eq(md_renderer, markdown.markdown)

    with unittest.mock.patch.dict(
        "sys.modules",
        {"markdown_it": None, "markdown": None},
    ):
        importlib.reload(rico._config)
        md_renderer = rico._config._global_config["markdown_renderer"]
        assert md_renderer is None

    importlib.reload(rico._config)


@pytest.fixture
def reset_config() -> Generator[None, Any, None]:  # noqa: PT004
    old_config = rico._config._global_config.copy()

    try:
        yield
    finally:
        rico._config._global_config = old_config


@pytest.mark.usefixtures("reset_config")
def test_get_config():
    config = rico._config.get_config()
    assert config == rico._config._global_config
    config["indent_html"] = not config["indent_html"]
    assert config != rico._config._global_config

    assert (
        rico._config.get_config("indent_html") ==
        rico._config._global_config["indent_html"]
    )


@pytest.mark.usefixtures("reset_config")
def test_set_config():
    rico._config.set_config(indent_html=True)
    assert rico._config._global_config["indent_html"] is True

    rico._config.set_config(indent_html=False)
    assert rico._config._global_config["indent_html"] is False


@pytest.mark.usefixtures("reset_config")
def test_config_context():
    old_indent_html = rico._config._global_config["indent_html"]

    with rico._config.config_context(indent_html=not old_indent_html):
        assert rico._config._global_config["indent_html"] is not old_indent_html

    assert rico._config._global_config["indent_html"] is old_indent_html
