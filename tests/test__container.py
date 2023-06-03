# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
from __future__ import annotations

import xml.etree.ElementTree as ET

import altair as alt
import pytest

import rico._container
import rico._content


def test_div_init():
    content = rico._container.Div(
        "Hello world",
        rico._content.Tag("h1", "Header", class_="col"),
        class_="row",
    )

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 2

    div1 = list(div0)[0]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 1

    p = list(div1)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {}
    assert p.text == "Hello world"
    assert p.tail is None
    assert len(p) == 0

    div2 = list(div0)[1]
    assert isinstance(div2, ET.Element)
    assert div2.tag == "div"
    assert div2.attrib == {"class": "col"}
    assert div2.text is None
    assert div2.tail is None
    assert len(div2) == 1

    h1 = list(div2)[0]
    assert isinstance(h1, ET.Element)
    assert h1.tag == "h1"
    assert h1.attrib == {}
    assert h1.text == "Header"
    assert h1.tail is None
    assert len(h1) == 0


@pytest.fixture
def div_container() -> rico._container.Div:
    return rico._container.Div()


def test_div_append_tag(div_container: rico._container.Div):
    div_container.append_tag("h1", "Hello world")
    content = rico._content.Tag("h1", "Hello world")
    assert str(div_container) == f"<div>{content}</div>"


def test_div_append_text(div_container: rico._container.Div):
    div_container.append_text("Hello world")
    content = rico._content.Text("Hello world")
    assert str(div_container) == f"<div>{content}</div>"


def test_div_append_code(div_container: rico._container.Div):
    div_container.append_code("Hello world")
    content = rico._content.Code("Hello world")
    assert str(div_container) == f"<div>{content}</div>"


def test_div_append_html(div_container: rico._container.Div):
    div_container.append_html("<p>Hello world</p>")
    content = rico._content.HTML("<p>Hello world</p>")
    assert str(div_container) == f"<div>{content}</div>"


def test_div_append_markdown(div_container: rico._container.Div):
    div_container.append_markdown("# Hello world")
    content = rico._content.Markdown("# Hello world")
    assert str(div_container) == f"<div>{content}</div>"


svg_data = (
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'xmlns:xlink="http://www.w3.org/1999/xlink" '
    'width="16" height="16" fill="currentColor" class="bi bi-dash">'
    '<path d="M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z"/>'
    "</svg>"
)

def test_div_append_image(div_container: rico._container.Div):
    div_container.append_image(svg_data, "svg")
    content = rico._content.Image(svg_data, "svg")
    assert str(div_container) == f"<div>{content}</div>"


altair_chart = alt.Chart(
    alt.Data(values=[
        {"x": "A", "y": 5},
        {"x": "B", "y": 3},
        {"x": "C", "y": 6},
        {"x": "D", "y": 7},
        {"x": "E", "y": 2},
    ]),
).mark_bar().encode(x="x:N", y="y:Q")

def test_div_append_chart(div_container: rico._container.Div):
    div_container.append_chart(altair_chart)
    content = rico._content.Chart(altair_chart)
    assert str(div_container) == f"<div>{content}</div>"


def test_div_append(div_container: rico._container.Div):
    div_container.append("Hello world", altair_chart)
    content = rico._content.Obj("Hello world", altair_chart)
    assert str(div_container) == f"<div>{content}</div>"
