"""Container classes."""

from __future__ import annotations

from typing import TYPE_CHECKING

import rico._content


if TYPE_CHECKING:
    from typing import Any


class Div(rico._content.ContentBase):
    """A <div> container definition.

    Creates <div> container with content based on arbitrary objects.
    """
    def __init__(self, *objects: Any, class_: str | None = None):
        """Initialize <div> container with content from arbitrary objects.

        Args:
            *objects: The objects which are used to create a content.
            class_: The container class attribute.
        """
        super().__init__(class_=class_)
        for obj in objects:
            if isinstance(obj, rico._content.ContentBase):
                self.container.append(obj.container)
            else:
                self.container.append(rico._content.Obj(obj).container)
