"""Package version."""

import importlib.metadata
import importlib.resources


try:
    __version__ = importlib.metadata.version(__package__ or "rico")
except importlib.metadata.PackageNotFoundError:
    __version__ = (
        importlib.resources.files("rico")
        .joinpath("_version.txt")
        .read_text()
        .strip()
    )
