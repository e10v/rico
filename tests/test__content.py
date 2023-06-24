# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
from __future__ import annotations

import base64
import importlib
import io
import textwrap
from typing import TYPE_CHECKING
import unittest.mock
import xml.etree.ElementTree as ET

import altair as alt
import matplotlib.pyplot as plt
import pytest
import seaborn.objects as so

import rico._content


if TYPE_CHECKING:
    from typing import Any, Literal


def test_import_error():
    with unittest.mock.patch.dict("sys.modules", {"altair": None}):
        importlib.reload(rico._content)
        assert rico._content.alt is None

    with unittest.mock.patch.dict("sys.modules", {"vl_convert": None}):
        importlib.reload(rico._content)
        assert rico._content.alt is None

    with unittest.mock.patch.dict("sys.modules", {"markdown": None}):
        importlib.reload(rico._content)
        assert rico._content.markdown is None

    with unittest.mock.patch.dict("sys.modules", {"matplotlib.pyplot": None}):
        importlib.reload(rico._content)
        assert rico._content.plt is None

    with unittest.mock.patch.dict("sys.modules", {"seaborn.objects": None}):
        importlib.reload(rico._content)
        assert rico._content.so is None

    importlib.reload(rico._content)


def test_content_base_simple():
    content = rico._content.ContentBase()
    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 0


def test_content_base_with_class():
    content = rico._content.ContentBase("row")
    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 0


@pytest.fixture
def content_base_subclass_sample():
    class ContentBaseSubclass(rico._content.ContentBase):
        def __init__(self, class_: str | None = None):
            super().__init__(class_)
            p = ET.Element("p")
            p.text = "Hello world"
            self.container.append(p)

    return ContentBaseSubclass("row")


def test_content_base_str(content_base_subclass_sample: rico._content.ContentBase):
    expectation = '<div class="row"><p>Hello world</p></div>'
    assert str(content_base_subclass_sample) == expectation


def test_content_base_indent(content_base_subclass_sample: rico._content.ContentBase):
    expectation = textwrap.dedent("""\
        <div class="row">
            <p>Hello world</p>
        </div>""")
    assert content_base_subclass_sample.serialize(
        indent=True, space="    ") == expectation


def test_content_base_strip(content_base_subclass_sample: rico._content.ContentBase):
    expectation = '<div class="row"><p>Hello world</p></div>'
    assert content_base_subclass_sample.serialize(strip=True) == expectation


def test_tag():
    content = rico._content.Tag(
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

    p = tuple(div)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {"class": "col", "id": "42"}
    assert p.text == "Hello"
    assert p.tail == "world"
    assert len(p) == 0


def test_text_simple():
    content = rico._content.Text("Hello world", class_="row")

    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    p = tuple(div)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {}
    assert p.text == "Hello world"
    assert p.tail is None
    assert len(p) == 0


def test_text_pre_mono():
    content = rico._content.Text("Hello\nworld", mono=True)
    div = content.container

    pre = tuple(div)[0]
    assert isinstance(pre, ET.Element)
    assert pre.tag == "pre"
    assert pre.attrib == {"class": "font-monospace"}
    assert pre.text == "Hello\nworld"
    assert pre.tail is None
    assert len(pre) == 0


def test_text_int_mono_wrap():
    content = rico._content.Text(42, mono=True, wrap=True)
    div = content.container

    p = tuple(div)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {"class": "font-monospace text-wrap"}
    assert p.text == "42"
    assert p.tail is None
    assert len(p) == 0


def test_code():
    content = rico._content.Code("Hello world", class_="row")

    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    pre = tuple(div)[0]
    assert isinstance(pre, ET.Element)
    assert pre.tag == "pre"
    assert pre.attrib == {}
    assert pre.text is None
    assert pre.tail is None
    assert len(pre) == 1

    code = tuple(pre)[0]
    assert isinstance(code, ET.Element)
    assert code.tag == "code"
    assert code.attrib == {}
    assert code.text == "Hello world"
    assert code.tail is None
    assert len(code) == 0


def test_html_simple():
    content = rico._content.HTML('<p border="1">Hello world</p>', True, class_="row")

    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    p = tuple(div)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {"border": "1"}
    assert p.text == "Hello world"
    assert p.tail is None
    assert len(p) == 0


@pytest.mark.parametrize("border", [True, False], ids=["border", "no border"])
@pytest.mark.parametrize("dataframe", [True, False], ids=["dataframe", "not dataframe"])
@pytest.mark.parametrize(
    "strip_dataframe_borders", [True, False], ids=["strip", "do not strip"])
@pytest.mark.parametrize(
    "wrap_in_div", [True, False], ids=["wrap in div", "do not wrap in div"])
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

    content = rico._content.HTML(df, strip_dataframe_borders)
    if wrap_in_div:
        div = tuple(content.container)[0]
        table = tuple(div)[0]
    else:
        table = tuple(content.container)[0]

    if border and (not dataframe or not strip_dataframe_borders):
        assert table.get("border") == "1"
    else:
        assert table.get("border", "no border") == "no border"


def test_markdown():
    content = rico._content.Markdown(
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

    h1 = tuple(div)[0]
    assert isinstance(h1, ET.Element)
    assert h1.tag == "h1"
    assert h1.attrib == {}
    assert h1.text == "Header 1"
    assert h1.tail == "\n"
    assert len(h1) == 0

    h2 = tuple(div)[1]
    assert isinstance(h2, ET.Element)
    assert h2.tag == "h2"
    assert h2.attrib == {}
    assert h2.text == "Header 2"
    assert h2.tail == "\n"
    assert len(h2) == 0

    p = tuple(div)[2]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {}
    assert p.text == "Hello world"
    assert p.tail is None
    assert len(p) == 0


def test_markdown_import_error():
    with (
        unittest.mock.patch.object(rico._content, "markdown", None),
        pytest.raises(ImportError),
    ):
        rico._content.Markdown("Hello world")


svg_data = (
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'xmlns:xlink="http://www.w3.org/1999/xlink" '
    'width="16" height="16" fill="currentColor" class="bi bi-dash">'
    '<path d="M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z"/>'
    "</svg>"
)

@pytest.mark.parametrize("data", [svg_data, svg_data.encode()], ids=["str", "bytes"])
def test_image_svg(data: str | bytes):
    content = rico._content.Image(data, mime_subtype="svg+xml", class_="row")

    if isinstance(data, str):
        data = data.encode()
    encoded_image = base64.b64encode(data).decode()

    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    img = tuple(div)[0]
    assert isinstance(img, ET.Element)
    assert img.tag == "img"
    assert img.attrib == {"src": f"data:image/svg+xml;base64,{encoded_image}"}
    assert img.text is None
    assert img.tail is None
    assert len(img) == 0


@pytest.mark.parametrize("data", [svg_data, svg_data.encode()], ids=["str", "bytes"])
def test_image_png(data: str | bytes):
    content = rico._content.Image(data, mime_subtype="png")

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

    img = tuple(div)[0]
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
    "plot",
    [altair_chart, pyplot_axes, pyplot_figure, seaborn_plot],
    ids=["altair", "pyplot_axes", "pyplot_figure", "seaborn_plot"],
)
@pytest.mark.parametrize("format", [None, "png"], ids=["svg", "png"])
def test_plot_complete(plot: Any, format: Literal["svg", "png"] | None):  # noqa: A002
    content = rico._content.Plot(plot, format=format, class_="row")

    div = content.container
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {"class": "row"}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    img = tuple(div)[0]
    assert isinstance(img, ET.Element)
    assert img.tag == "img"


@pytest.mark.parametrize(
    ("module", "err_plot", "plot"),
    [
        ("alt", altair_chart, seaborn_plot),
        ("plt", pyplot_axes, altair_chart),
        ("so", seaborn_plot, pyplot_axes),
    ],
    ids=["alt", "plt", "so"],
)
def test_plot_error(module: str, err_plot: Any, plot: Any):
    with unittest.mock.patch.object(rico._content, module, None):
        with pytest.raises(TypeError):
            rico._content.Plot(err_plot)

        content = rico._content.Plot(plot, class_="row")
        div = content.container
        assert isinstance(div, ET.Element)


def test_obj():
    class ReprHTML:
        def _repr_html_(self) -> str:
            return "<h1>Hello</h1>"

    content_base = rico._content.ContentBase(class_="col")

    content = rico._content.Obj(
        ReprHTML(),
        "world",
        pyplot_axes,
        content_base,
        class_="row",
    )

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 4

    h1 = tuple(div0)[0]
    assert isinstance(h1, ET.Element)
    assert h1.tag == "h1"
    assert h1.attrib == {}
    assert h1.text == "Hello"
    assert h1.tail is None
    assert len(h1) == 0

    p = tuple(div0)[1]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {}
    assert p.text == "world"
    assert p.tail is None
    assert len(p) == 0

    img = tuple(div0)[2]
    assert isinstance(img, ET.Element)
    assert img.tag == "img"

    div1 = tuple(div0)[3]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {"class": "col"}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 0


@pytest.mark.parametrize("defer", [True, False], ids=["defer", "not defer"])
def test_script_text(defer: bool):
    text = "alert('Hello World!');"
    attrib = {"async": True}
    content = rico._content.Script(text=text, defer=defer, attrib=attrib)

    script = content.container
    assert isinstance(script, ET.Element)
    assert script.tag == "script"
    assert script.attrib == attrib
    assert script.text == text
    assert script.tail is None
    assert len(script) == 0

    assert content.container == script
    assert content.footer == defer


@pytest.mark.parametrize("defer", [True, False], ids=["defer", "not defer"])
def test_script_src(defer: bool):
    src = "javascript.js"
    attrib = {"async": True}
    content = rico._content.Script(src=src, defer=defer, attrib=attrib)

    attrib = {"src": src, **attrib}
    if defer:
        attrib = {"defer": True, **attrib}

    script = content.container
    assert isinstance(script, ET.Element)
    assert script.tag == "script"
    assert script.attrib == attrib
    assert script.text is None
    assert script.tail is None
    assert len(script) == 0

    assert content.container == script
    assert content.footer is False


@pytest.mark.parametrize("defer", [True, False], ids=["defer", "not defer"])
def test_script_inline(defer: bool):
    text = "alert('Hello World!');"
    src = "javascript.js"
    attrib = {"async": True}

    with unittest.mock.patch("rico._content.urllib.request.urlopen") as urlopen:
        urlopen.return_value = io.BytesIO(text.encode())
        content = rico._content.Script(src=src, inline=True, defer=defer, attrib=attrib)
        urlopen.assert_called_once_with(src)

    script = content.container
    assert isinstance(script, ET.Element)
    assert script.tag == "script"
    assert script.attrib == attrib
    assert script.text == text
    assert script.tail is None
    assert len(script) == 0

    assert content.container == script
    assert content.footer == defer


def test_script_raises():
    with pytest.raises(ValueError):
        rico._content.Script()
    with pytest.raises(ValueError):
        rico._content.Script(src="javascript.js", text="alert('Hello World!');")


def test_style_text():
    text = "p {color: red;}"
    attrib = {"title": "Style title"}
    content = rico._content.Style(text=text, attrib=attrib)

    style = content.container
    assert isinstance(style, ET.Element)
    assert style.tag == "style"
    assert style.attrib == attrib
    assert style.text == text
    assert style.tail is None
    assert len(style) == 0

    assert content.container == style


def test_style_src():
    src = "style.css"
    attrib = {"crossorigin": "anonymous"}
    content = rico._content.Style(src=src, attrib=attrib)

    attrib = {"href": src, **attrib, "rel": "stylesheet"}

    link = content.container
    assert isinstance(link, ET.Element)
    assert link.tag == "link"
    assert link.attrib == attrib
    assert link.text is None
    assert link.tail is None
    assert len(link) == 0

    assert content.container == link


def test_style_inline():
    text = "p {color: red;}"
    src = "style.css"
    attrib = {"title": "Style title"}

    with unittest.mock.patch("rico._content.urllib.request.urlopen") as urlopen:
        urlopen.return_value = io.BytesIO(text.encode())
        content = rico._content.Style(src=src, inline=True, attrib=attrib)
        urlopen.assert_called_once_with(src)

    style = content.container
    assert isinstance(style, ET.Element)
    assert style.tag == "style"
    assert style.attrib == attrib
    assert style.text == text
    assert style.tail is None
    assert len(style) == 0

    assert content.container == style


def test_style_raises():
    with pytest.raises(ValueError):
        rico._content.Style()
    with pytest.raises(ValueError):
        rico._content.Style(src="style.css", text="p {color: red;}")
