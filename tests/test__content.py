# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
from __future__ import annotations

import base64
import importlib
import io
import textwrap
from typing import TYPE_CHECKING
import unittest.mock
import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
import pytest

import rico._config
import rico._content


if TYPE_CHECKING:
    from typing import Any, Literal


def test_import_error():
    with unittest.mock.patch.dict("sys.modules", {"matplotlib.pyplot": None}):
        importlib.reload(rico._content)
        assert rico._content.plt is None

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
            p.text = "Hello, World"
            self.container.append(p)

    return ContentBaseSubclass("row")


def test_content_base_str(content_base_subclass_sample: rico._content.ContentBase):
    expectation = '<div class="row"><p>Hello, World</p></div>'
    assert str(content_base_subclass_sample) == expectation


def test_content_base_indent(content_base_subclass_sample: rico._content.ContentBase):
    expectation = textwrap.dedent("""\
        <div class="row">
            <p>Hello, World</p>
        </div>""")
    assert content_base_subclass_sample.serialize(
        indent=True, space="    ") == expectation


def test_content_base_strip(content_base_subclass_sample: rico._content.ContentBase):
    expectation = '<div class="row"><p>Hello, World</p></div>'
    assert content_base_subclass_sample.serialize(strip=True) == expectation


def test_tag():
    content = rico._content.Tag(
        "p",
        attrib={"class": "col"},
        id="42",
        text="Hello,",
        tail="World",
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
    assert p.text == "Hello,"
    assert p.tail == "World"
    assert len(p) == 0


def test_text_simple():
    content = rico._content.Text("Hello, World", class_="row")

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
    assert p.text == "Hello, World"
    assert p.tail is None
    assert len(p) == 0


def test_text_pre_mono():
    content = rico._content.Text("Hello,\nWorld", mono=True)
    div = content.container

    pre = tuple(div)[0]
    assert isinstance(pre, ET.Element)
    assert pre.tag == "pre"
    assert pre.attrib == {"class": "font-monospace"}
    assert pre.text == "Hello,\nWorld"
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
    content = rico._content.Code("Hello, World", class_="row")

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
    assert code.text == "Hello, World"
    assert code.tail is None
    assert len(code) == 0


def test_html_simple():
    content = rico._content.HTML('<p border="1">Hello, World</p>', True, class_="row")

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
    assert p.text == "Hello, World"
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
            Hello, World"""),
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
    assert p.text == "Hello, World"
    assert len(p) == 0


def test_markdown_error():
    with unittest.mock.patch.dict(
        "sys.modules",
        {"markdown_it": None, "markdown": None},
    ):
        importlib.reload(rico._config)
        with pytest.raises(RuntimeError):
            rico._content.Markdown("Hello, World")

    importlib.reload(rico._config)


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


pyplot_figure, pyplot_axes = plt.subplots()  # type: ignore
pyplot_axes.plot([1, 2, 3, 4], [1, 4, 2, 3])  # type: ignore

@pytest.mark.parametrize(
    "plot",
    [pyplot_axes, pyplot_figure],
    ids=["pyplot_axes", "pyplot_figure"],
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


def test_plot_import_error():
    with (
        unittest.mock.patch.object(rico._content, "plt", None),
        pytest.raises(ImportError),
    ):
            rico._content.Plot(pyplot_axes)


def test_plot_type_error():
    with pytest.raises(TypeError):
        rico._content.Plot("text")


@pytest.mark.parametrize("defer", [True, False], ids=["defer", "not defer"])
def test_script_text(defer: bool):
    text = "alert('Hello, World!');"
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
    text = "alert('Hello, World!');"
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
        rico._content.Script(src="javascript.js", text="alert('Hello, World!');")


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


def test_obj_content_base():
    content = rico._content.Obj(
        rico._content.ContentBase(class_="col"),
        class_="row",
    )

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 1

    div1 = tuple(div0)[0]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {"class": "col"}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 0


def test_obj_pyplot():
    content = rico._content.Obj(pyplot_axes, class_="row")

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 1

    div1 = tuple(div0)[0]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 1

    img = tuple(div1)[0]
    assert isinstance(img, ET.Element)
    assert img.tag == "img"
    assert len(img) == 0


def test_obj_javascript():
    class Repr:
        def _repr_javascript_(self) -> str:
            return "alert('Hello, World!');"

    content = rico._content.Obj(Repr(), class_="row")

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 1

    script = tuple(div0)[0]
    assert isinstance(script, ET.Element)
    assert script.tag == "script"
    assert script.attrib == {}
    assert script.text == "alert('Hello, World!');"
    assert script.tail is None
    assert len(script) == 0


def test_obj_html():
    class Repr:
        def _repr_html_(self) -> str:
            return "<p>Hello, World!</p>"

    content = rico._content.Obj(Repr(), class_="row")

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 1

    div1 = tuple(div0)[0]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 1

    p = tuple(div1)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {}
    assert p.text == "Hello, World!"
    assert p.tail is None
    assert len(p) == 0


def test_obj_markdown():
    class Repr:
        def _repr_markdown_(self) -> str:
            return "# Hello, World!"

    content = rico._content.Obj(Repr(), class_="row")

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 1

    div1 = tuple(div0)[0]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 1

    h1 = tuple(div1)[0]
    assert isinstance(h1, ET.Element)
    assert h1.tag == "h1"
    assert h1.attrib == {}
    assert h1.text == "Hello, World!"
    assert len(h1) == 0


def test_obj_svg():
    image = svg_data
    class Repr:
        def _repr_svg_(self) -> str:
            return image

    content = rico._content.Obj(Repr(), class_="row")

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 1

    div1 = tuple(div0)[0]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 1

    encoded_image = base64.b64encode(image.encode()).decode()

    img = tuple(div1)[0]
    assert isinstance(img, ET.Element)
    assert img.tag == "img"
    assert img.attrib == {"src": f"data:image/svg+xml;base64,{encoded_image}"}
    assert img.text is None
    assert img.tail is None
    assert len(img) == 0


def test_obj_png():
    image = svg_data.encode()
    class Repr:
        def _repr_png_(self) -> bytes:
            return image

    content = rico._content.Obj(Repr(), class_="row")

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 1

    div1 = tuple(div0)[0]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 1

    encoded_image = base64.b64encode(image).decode()

    img = tuple(div1)[0]
    assert isinstance(img, ET.Element)
    assert img.tag == "img"
    assert img.attrib == {"src": f"data:image/png;base64,{encoded_image}"}
    assert img.text is None
    assert img.tail is None
    assert len(img) == 0


def test_obj_jpeg():
    image = svg_data.encode()
    class Repr:
        def _repr_jpeg_(self) -> bytes:
            return image

    content = rico._content.Obj(Repr(), class_="row")

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 1

    div1 = tuple(div0)[0]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 1

    encoded_image = base64.b64encode(image).decode()

    img = tuple(div1)[0]
    assert isinstance(img, ET.Element)
    assert img.tag == "img"
    assert img.attrib == {"src": f"data:image/jpeg;base64,{encoded_image}"}
    assert img.text is None
    assert img.tail is None
    assert len(img) == 0


def test_obj_gif():
    image = svg_data.encode()
    class Repr:
        def _repr_mimebundle_(self) -> dict[str, Any]:
            return {"image/gif": image}

    content = rico._content.Obj(Repr(), class_="row")

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 1

    div1 = tuple(div0)[0]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 1

    encoded_image = base64.b64encode(image).decode()

    img = tuple(div1)[0]
    assert isinstance(img, ET.Element)
    assert img.tag == "img"
    assert img.attrib == {"src": f"data:image/gif;base64,{encoded_image}"}
    assert img.text is None
    assert img.tail is None
    assert len(img) == 0


def test_obj_text():
    class Repr:
        def _repr_mimebundle_(self) -> dict[str, Any]:
            return {"text/plain": "Hello, World!"}

    content = rico._content.Obj(Repr(), class_="row")

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 1

    div1 = tuple(div0)[0]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 1

    p = tuple(div1)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {}
    assert p.text == "Hello, World!"
    assert p.tail is None
    assert len(p) == 0


def test_obj_priority():
    class Repr:
        def _repr_javascript_(self) -> str:
            return "alert('Hello, World!');"

        def _repr_mimebundle_(self) -> dict[str, Any]:
            return {
                "text/plain": "Hello, World!",
                "text/markdown": "# Hello, World!",
            }

    content = rico._content.Obj(Repr(), class_="row")

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 1

    div1 = tuple(div0)[0]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 1

    h1 = tuple(div1)[0]
    assert isinstance(h1, ET.Element)
    assert h1.tag == "h1"
    assert h1.attrib == {}
    assert h1.text == "Hello, World!"
    assert len(h1) == 0


def test_obj_corner_cases():
    class Repr:
        def _repr_javascript_(self) -> str | None:
            return None

        def _repr_markdown_(self) -> tuple[str, Any]:
            return "# Hello, World!", "metadata"

    content = rico._content.Obj(Repr(), class_="row")

    div0 = content.container
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "row"}
    assert div0.text is None
    assert div0.tail is None
    assert len(div0) == 1

    div1 = tuple(div0)[0]
    assert isinstance(div1, ET.Element)
    assert div1.tag == "div"
    assert div1.attrib == {}
    assert div1.text is None
    assert div1.tail is None
    assert len(div1) == 1

    h1 = tuple(div1)[0]
    assert isinstance(h1, ET.Element)
    assert h1.tag == "h1"
    assert h1.attrib == {}
    assert h1.text == "Hello, World!"
    assert len(h1) == 0
