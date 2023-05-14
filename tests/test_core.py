from __future__ import annotations

import itertools
import textwrap
import xml.etree.ElementTree as ET  # noqa: N817

import pytest

from rico import core


def test_content_base_simple():
    element = core.ContentBase()
    div = element.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {}
    assert div.text is None
    assert div.tail is None


def test_content_base_with_class():
    element = core.ContentBase("row")
    div = element.container
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


def test_tag():
    element = core.Tag(
        "p",
        attrib={"class": "col"},
        id="42",
        text="Hello",
        tail="world",
        class_="row",
    )

    div = element.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    p = list(div)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {"class": "col", "id": "42"}
    assert p.text == "Hello"
    assert p.tail == "world"


def test_html_simple():
    element = core.HTML('<p border="1">Hello world</p>', True, class_="row")

    div = element.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    p = list(div)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {"border": "1"}
    assert p.text == "Hello world"
    assert p.tail is None


@pytest.mark.parametrize(
    ("border", "dataframe", "strip_dataframe_borders", "wrap_in_div"),
    itertools.product([True, False], [True, False], [True, False], [True, False]),
)
def test_html_table_border(
    border: bool,
    dataframe: bool,
    strip_dataframe_borders: bool,
    wrap_in_div: bool,
):
    border_attr = ' border="1"' if border else ""
    dataframe_attr = ' class="dataframe"' if dataframe else ""

    df = (
        f"<table{border_attr}{dataframe_attr}>"
        "<tbody><tr><td>1<td></tr></tbody></table>"
    )

    if wrap_in_div:
        df = f"<div>{df}</div>"

    element = core.HTML(df, strip_dataframe_borders)
    if wrap_in_div:
        div = list(element.container)[0]
        table = list(div)[0]
    else:
        table = list(element.container)[0]

    if border and (not dataframe or not strip_dataframe_borders):
        assert table.get("border") == "1"
    else:
        assert table.get("border", "no border") == "no border"


def test_text_simple():
    element = core.Text("Hello world", class_="row")

    div = element.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    p = list(div)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {}
    assert p.text == "Hello world"
    assert p.tail is None


def test_text_pre_mono():
    element = core.Text("Hello\nworld", mono=True)
    div = element.container

    pre = list(div)[0]
    assert isinstance(pre, ET.Element)
    assert pre.tag == "pre"
    assert pre.attrib == {"class": "font-monospace"}
    assert pre.text == "Hello\nworld"
    assert pre.tail is None


def test_text_int_mono_wrap():
    element = core.Text(42, mono=True, wrap=True)
    div = element.container

    p = list(div)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {"class": "font-monospace text-wrap"}
    assert p.text == "42"
    assert p.tail is None
