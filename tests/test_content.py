# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
from __future__ import annotations

import base64
import itertools
import textwrap
from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET

import altair as alt
import matplotlib.pyplot as plt
import pytest
import seaborn.objects as so

import rico.content


if TYPE_CHECKING:
    from typing import Any, Literal


def test_content_base_simple():
    content = rico.content.ContentBase()
    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 0


def test_content_base_with_class():
    content = rico.content.ContentBase("row")
    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 0


@pytest.fixture
def content_base_subclass_sample():
    class ContentBaseSubclass(rico.content.ContentBase):
        def __init__(self, class_: str | None = None):
            super().__init__(class_)
            p = ET.Element("p")
            p.text = "Hello world"
            self.container.append(p)

    return ContentBaseSubclass("row")


def test_content_base_str(content_base_subclass_sample: rico.content.ContentBase):
    expectation = '<div class="row"><p>Hello world</p></div>'
    assert str(content_base_subclass_sample) == expectation


def test_content_base_indent(content_base_subclass_sample: rico.content.ContentBase):
    expectation = textwrap.dedent("""\
        <div class="row">
            <p>Hello world</p>
        </div>""")
    assert content_base_subclass_sample.serialize("    ") == expectation


def test_content_base_strip(content_base_subclass_sample: rico.content.ContentBase):
    expectation = '<div class="row"><p>Hello world</p></div>'
    assert content_base_subclass_sample.serialize(strip=True) == expectation


def test_tag():
    content = rico.content.Tag(
        "p",
        attrib={"class": "col"},
        id="42",
        text="Hello",
        tail="world",
        class_="row",
    )

    div = content.container
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
    assert len(p) == 0


def test_text_simple():
    content = rico.content.Text("Hello world", class_="row")

    div = content.container
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
    assert len(p) == 0


def test_text_pre_mono():
    content = rico.content.Text("Hello\nworld", mono=True)
    div = content.container

    pre = list(div)[0]
    assert isinstance(pre, ET.Element)
    assert pre.tag == "pre"
    assert pre.attrib == {"class": "font-monospace"}
    assert pre.text == "Hello\nworld"
    assert pre.tail is None
    assert len(pre) == 0


def test_text_int_mono_wrap():
    content = rico.content.Text(42, mono=True, wrap=True)
    div = content.container

    p = list(div)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {"class": "font-monospace text-wrap"}
    assert p.text == "42"
    assert p.tail is None
    assert len(p) == 0


def test_code():
    content = rico.content.Code("Hello world", class_="row")

    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    pre = list(div)[0]
    assert isinstance(pre, ET.Element)
    assert pre.tag == "pre"
    assert pre.attrib == {}
    assert pre.text is None
    assert pre.tail is None
    assert len(pre) == 1

    code = list(pre)[0]
    assert isinstance(code, ET.Element)
    assert code.tag == "code"
    assert code.attrib == {}
    assert code.text == "Hello world"
    assert code.tail is None
    assert len(code) == 0


def test_html_simple():
    content = rico.content.HTML('<p border="1">Hello world</p>', True, class_="row")

    div = content.container
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
    assert len(p) == 0


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

    content = rico.content.HTML(df, strip_dataframe_borders)
    if wrap_in_div:
        div = list(content.container)[0]
        table = list(div)[0]
    else:
        table = list(content.container)[0]

    if border and (not dataframe or not strip_dataframe_borders):
        assert table.get("border") == "1"
    else:
        assert table.get("border", "no border") == "no border"


def test_markdown():
    content = rico.content.Markdown(
        textwrap.dedent("""\
            # Header 1
            ## Header 2
            Hello world"""),
        class_="row",
    )

    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 3

    h1 = list(div)[0]
    assert isinstance(h1, ET.Element)
    assert h1.tag == "h1"
    assert h1.attrib == {}
    assert h1.text == "Header 1"
    assert h1.tail == "\n"
    assert len(h1) == 0

    h2 = list(div)[1]
    assert isinstance(h2, ET.Element)
    assert h2.tag == "h2"
    assert h2.attrib == {}
    assert h2.text == "Header 2"
    assert h2.tail == "\n"
    assert len(h2) == 0

    p = list(div)[2]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {}
    assert p.text == "Hello world"
    assert p.tail is None
    assert len(p) == 0


svg_data = (
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'xmlns:xlink="http://www.w3.org/1999/xlink" '
    'width="16" height="16" fill="currentColor" class="bi bi-dash">'
    '<path d="M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z"/>'
    "</svg>"
)

@pytest.mark.parametrize("data", [svg_data, svg_data.encode()], ids=["str", "bytes"])
def test_image_svg(data: str | bytes):
    content = rico.content.Image(data, format="svg", class_="row")

    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    svg = list(div)[0]
    assert isinstance(svg, ET.Element)
    assert svg.tag == "svg"
    assert svg.attrib == {
        "xmlns": "http://www.w3.org/2000/svg",
        "xmlns:xlink": "http://www.w3.org/1999/xlink",
        "width": "16",
        "height": "16",
        "fill": "currentColor",
        "class": "bi bi-dash",
    }
    assert svg.text is None
    assert svg.tail is None
    assert len(svg) == 1

    path = list(svg)[0]
    assert isinstance(path, ET.Element)
    assert path.tag == "path"
    assert path.attrib == {
        "d": "M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z",
    }
    assert path.text is None
    assert path.tail is None
    assert len(path) == 0


@pytest.mark.parametrize("data", [svg_data, svg_data.encode()], ids=["str", "bytes"])
def test_image_png(data: str | bytes):
    content = rico.content.Image(data, format="png")

    if isinstance(data, str):
        data = data.encode()
    encoded_image = base64.b64encode(data).decode()

    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    img = list(div)[0]
    assert isinstance(img, ET.Element)
    assert img.tag == "img"
    assert img.attrib == {"src": f"data:image/png;base64,{encoded_image}"}
    assert img.text is None
    assert img.tail is None
    assert len(img) == 0


altair_chart = alt.Chart(
    alt.Data(values=[
        {"x": "A", "y": 5},
        {"x": "B", "y": 3},
        {"x": "C", "y": 6},
        {"x": "D", "y": 7},
        {"x": "E", "y": 2},
    ]),
).mark_bar().encode(x="x:N", y="y:Q")

pyplot_figure, pyplot_axes = plt.subplots()  # type: ignore
pyplot_axes.plot([1, 2, 3, 4], [1, 4, 2, 3])  # type: ignore

seaborn_plot = so.Plot({"x": [1, 2, 3, 4], "y": [1, 4, 2, 3]})  # type: ignore

@pytest.mark.parametrize(
    "chart",
    [altair_chart, pyplot_axes, pyplot_figure, seaborn_plot],
    ids=["altair", "pyplot_axes", "pyplot_figure", "seaborn_plot"],
)
@pytest.mark.parametrize("format", ["svg", "png"], ids=["svg", "png"])
def test_chart(chart: Any, format: Literal["svg", "png"]):  # noqa: A002
    content = rico.content.Chart(chart, format=format, class_="row")

    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    if format == "svg":
        svg = list(div)[0]
        assert isinstance(svg, ET.Element)
        assert svg.tag == "svg"
    else:
        img = list(div)[0]
        assert isinstance(img, ET.Element)
        assert img.tag == "img"


def test_content():
    class ReprHTML:
        def _repr_html_(self) -> str:
            return "<h1>Hello</h1>"

    content = rico.content.Content(ReprHTML(), "world", pyplot_axes, class_="row")

    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 3

    h1 = list(div)[0]
    assert isinstance(h1, ET.Element)
    assert h1.tag == "h1"
    assert h1.attrib == {}
    assert h1.text == "Hello"
    assert h1.tail is None
    assert len(h1) == 0

    p = list(div)[1]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {}
    assert p.text == "world"
    assert p.tail is None
    assert len(p) == 0

    svg = list(div)[2]
    assert isinstance(svg, ET.Element)
    assert svg.tag == "svg"
