# pyright: reportUnknownMemberType=false, reportUnknownArgumentType=false
from __future__ import annotations

import xml.etree.ElementTree as ET

import matplotlib.pyplot as plt
import pytest

import rico._config
import rico._container
import rico._content


def test_div_init():
    content = rico._container.Div(
        "Hello, World",
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
    assert p.text == "Hello, World"
    assert p.tail is None
    assert len(p) == 0

    div2 = tuple(div0)[1]
    assert isinstance(div2, ET.Element)
    assert div2.tag == "div"
    assert div2.attrib == {"class": "col"}
    assert div2.text is None
    assert div2.tail is None
    assert len(div2) == 1

    h1 = tuple(div2)[0]
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
    div_container.append_tag("h1", "Hello, World")
    content = rico._content.Tag("h1", "Hello, World")
    assert str(div_container) == f"<div>{content}</div>"


def test_div_append_text(div_container: rico._container.Div):
    div_container.append_text("Hello, World")
    content = rico._content.Text("Hello, World")
    assert str(div_container) == f"<div>{content}</div>"


def test_div_append_code(div_container: rico._container.Div):
    div_container.append_code("Hello, World")
    content = rico._content.Code("Hello, World")
    assert str(div_container) == f"<div>{content}</div>"


def test_div_append_html(div_container: rico._container.Div):
    div_container.append_html("<p>Hello, World</p>")
    content = rico._content.HTML("<p>Hello, World</p>")
    assert str(div_container) == f"<div>{content}</div>"


def test_div_append_markdown(div_container: rico._container.Div):
    div_container.append_markdown("# Hello, World")
    content = rico._content.Markdown("# Hello, World")
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


pyplot_figure, pyplot_axes = plt.subplots()  # type: ignore
pyplot_axes.plot([1, 2, 3, 4], [1, 4, 2, 3])  # type: ignore

def test_div_append_plot(div_container: rico._container.Div):
    div_container.append_plot(pyplot_figure)

    div = div_container.container[0]
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    img = tuple(div)[0]
    assert isinstance(img, ET.Element)
    assert img.tag == "img"


def test_div_append(div_container: rico._container.Div):
    div_container.append("Hello, World")
    content = rico._content.Obj("Hello, World")
    assert str(div_container) == f"<div>{content}</div>"


def test_doc_init_default():  # noqa: PLR0915
    doc = rico._container.Doc("Hello, World")

    html = doc.html
    assert isinstance(html, ET.Element)
    assert html.tag == "html"
    assert html.attrib == {}
    assert html.text is None
    assert html.tail is None
    assert len(html) == 2

    head = doc.head
    assert head == tuple(html)[0]
    assert isinstance(head, ET.Element)
    assert head.tag == "head"
    assert head.attrib == {}
    assert head.text is None
    assert head.tail is None
    assert len(head) == 4

    charset = tuple(head)[0]
    assert isinstance(charset, ET.Element)
    assert charset.tag == "meta"
    assert charset.attrib == {"charset": "utf-8"}
    assert charset.text is None
    assert charset.tail is None
    assert len(charset) == 0

    viewport = tuple(head)[1]
    assert isinstance(viewport, ET.Element)
    assert viewport.tag == "meta"
    assert viewport.attrib == {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1",
    }
    assert viewport.text is None
    assert viewport.tail is None
    assert len(viewport) == 0

    bootstrap_css = tuple(head)[2]
    assert isinstance(bootstrap_css, ET.Element)
    assert bootstrap_css.tag == "link"
    assert bootstrap_css.attrib == {
        "href": rico._config.BOOTSTRAP_CSS,
        "rel": "stylesheet",
    }
    assert bootstrap_css.text is None
    assert bootstrap_css.tail is None
    assert len(bootstrap_css) == 0

    df_style = tuple(head)[3]
    assert isinstance(df_style, ET.Element)
    assert df_style.tag == "style"
    assert df_style.attrib == {}
    assert df_style.text == rico._config.DATAFRAME_STYLE
    assert df_style.tail is None
    assert len(df_style) == 0

    body = doc.body
    assert body == tuple(html)[1]
    assert isinstance(body, ET.Element)
    assert body.tag == "body"
    assert body.attrib == {}
    assert body.text is None
    assert body.tail is None
    assert len(body) == 1

    div0 = doc.container
    assert div0 == tuple(body)[0]
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {"class": "container"}
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
    assert p.text == "Hello, World"
    assert p.tail is None
    assert len(p) == 0


def test_doc_init_nondefault():  # noqa: PLR0915
    extra_style = rico._content.Style(src="style.css")
    extra_script = rico._content.Script(text="alert('Hello, World!');")
    extra_script.footer = True

    with rico._config.config_context(
        meta_charset="",
        meta_viewport="",
        dataframe_style="",
    ):
        doc = rico._container.Doc(
            "Hello, World",
            title="Title",
            bootstrap="full",
            extra_styles=(extra_style,),
            extra_scripts=(extra_script,),
            class_=None,
        )

    html = doc.html
    assert isinstance(html, ET.Element)
    assert html.tag == "html"
    assert html.attrib == {}
    assert html.text is None
    assert html.tail is None
    assert len(html) == 2

    head = doc.head
    assert head == tuple(html)[0]
    assert isinstance(head, ET.Element)
    assert head.tag == "head"
    assert head.attrib == {}
    assert head.text is None
    assert head.tail is None
    assert len(head) == 4

    title = tuple(head)[0]
    assert isinstance(title, ET.Element)
    assert title.tag == "title"
    assert title.attrib == {}
    assert title.text == "Title"
    assert title.tail is None
    assert len(title) == 0

    bootstrap_css = tuple(head)[1]
    assert isinstance(bootstrap_css, ET.Element)
    assert bootstrap_css.tag == "link"
    assert bootstrap_css.attrib == {
        "href": rico._config.BOOTSTRAP_CSS,
        "rel": "stylesheet",
    }
    assert bootstrap_css.text is None
    assert bootstrap_css.tail is None
    assert len(bootstrap_css) == 0

    style = tuple(head)[2]
    style = extra_style.container
    assert isinstance(style, ET.Element)
    assert style.tag == "link"
    assert style.attrib == {"href": "style.css", "rel": "stylesheet"}
    assert style.text is None
    assert style.tail is None
    assert len(style) == 0

    bootstrap_js = tuple(head)[3]
    assert isinstance(bootstrap_js, ET.Element)
    assert bootstrap_js.tag == "script"
    assert bootstrap_js.attrib == {"src": rico._config.BOOTSTRAP_JS}
    assert bootstrap_js.text is None
    assert bootstrap_js.tail is None
    assert len(bootstrap_js) == 0

    body = doc.body
    assert body == tuple(html)[1]
    assert isinstance(body, ET.Element)
    assert body.tag == "body"
    assert body.attrib == {}
    assert body.text is None
    assert body.tail is None
    assert len(body) == 2

    div0 = doc.container
    assert div0 == tuple(body)[0]
    assert isinstance(div0, ET.Element)
    assert div0.tag == "div"
    assert div0.attrib == {}
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
    assert p.text == "Hello, World"
    assert p.tail is None
    assert len(p) == 0

    script = tuple(body)[1]
    assert script == extra_script.container
    assert isinstance(script, ET.Element)
    assert script.tag == "script"
    assert script.attrib == {}
    assert script.text  == "alert('Hello, World!');"
    assert script.tail is None
    assert len(script) == 0


def test_doc_serialize():
    with rico._config.config_context(dataframe_style=""):
        doc = rico._container.Doc("Hello, World", bootstrap="none")

    assert doc.serialize() == (
        '<!doctype html>\n<html><head><meta charset="utf-8"/>'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/></head>'
        '<body><div class="container"><div><p>Hello, World</p></div></div></body>'
        '</html>'
    )
