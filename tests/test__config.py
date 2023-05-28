# pyright: reportPrivateUsage=false
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

import rico._config


if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any


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
