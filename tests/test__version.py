from __future__ import annotations

import importlib
import importlib.metadata
import unittest.mock

import rico._version


def test_version():
    assert isinstance(rico._version.__version__, str)

    with (
        unittest.mock.patch("rico._version.importlib.metadata.version") as version,
        unittest.mock.patch("rico._version.importlib.resources.files") as files,
    ):
        (
            files.return_value
            .joinpath.return_value
            .read_text.return_value
            .strip.return_value
        ) = "version"

        version.side_effect = importlib.metadata.PackageNotFoundError("Not found")
        importlib.reload(rico._version)
        assert isinstance(rico._version.__version__, str)
