from __future__ import annotations

import textwrap
import xml.etree.ElementTree as ET  # noqa: N817

import pytest

from rico import core


def test_content_base_simple():
    content = core.ContentBase()
    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {}
    assert div.text is None
    assert div.tail is None


def test_content_base_with_class():
    content = core.ContentBase("row")
    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None


@pytest.fixture
def content_base_subclass_sample():
    class ContentBaseSubclass(core.ContentBase):
        def __init__(self, class_: str | None = None):
            super().__init__(class_)
            p = ET.Element("p")
            p.text = "Hello world"
            self.container.append(p)

    return ContentBaseSubclass("row")


def test_content_base_str(content_base_subclass_sample: core.ContentBase):
    expectation = '<div class="row"><p>Hello world</p></div>'
    assert str(content_base_subclass_sample) == expectation


def test_content_base_indent(content_base_subclass_sample: core.ContentBase):
    expectation = textwrap.dedent("""\
        <div class="row">
            <p>Hello world</p>
        </div>""")
    assert content_base_subclass_sample.serialize("    ") == expectation
