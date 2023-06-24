from __future__ import annotations

import textwrap
import xml.etree.ElementTree as ET

import pytest

import rico._html


def elem_to_string(elem: ET.Element | tuple[ET.Element], sep: str = "") -> str:
    if isinstance(elem, tuple):
        return sep.join(elem_to_string(e) for e in elem)
    return ET.tostring(elem, encoding="unicode", method="html")


def test_parse_html_two_elements():
    text = "<p>Hello</p><p>world</p>"
    elements = rico._html.parse_html(text)

    assert elem_to_string(elements) == text
    assert isinstance(elements, tuple)
    assert len(elements) == 2

    p0 = elements[0]
    assert isinstance(p0, ET.Element)
    assert p0.tag == "p"
    assert p0.attrib == {}
    assert p0.text == "Hello"
    assert p0.tail is None
    assert len(p0) == 0

    p1 = elements[1]
    assert isinstance(p1, ET.Element)
    assert p1.tag == "p"
    assert p1.attrib == {}
    assert p1.text == "world"
    assert p1.tail is None
    assert len(p1) == 0


def test_parse_html_nested_tags():
    text = "<div><p>Hello <strong>world</strong>!</p></div>"
    elements = rico._html.parse_html(text)

    assert elem_to_string(elements) == text
    assert isinstance(elements, tuple)
    assert len(elements) == 1

    div = elements[0]
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    p = tuple(div)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {}
    assert p.text == "Hello "
    assert p.tail is None
    assert len(p) == 1

    strong = tuple(p)[0]
    assert isinstance(strong, ET.Element)
    assert strong.tag == "strong"
    assert strong.attrib == {}
    assert strong.text == "world"
    assert strong.tail == "!"
    assert len(strong) == 0


def test_parse_html_attributes():
    script_src = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"
    text = f"<script defer src='{script_src}' crossorigin='anonymous'></script>"
    elements = rico._html.parse_html(text)

    assert isinstance(elements, tuple)
    assert len(elements) == 1

    script = elements[0]
    assert isinstance(script, ET.Element)
    assert script.tag == "script"
    assert script.attrib == {
        "defer": None,
        "src": script_src,
        "crossorigin": "anonymous",
    }
    assert script.text is None
    assert script.tail is None
    assert len(script) == 0


def test_parse_html_svg():
    text = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'width="16" height="16" fill="currentColor" class="bi bi-dash">'
        '<path d="M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z"/>'
        "</svg>"
    )
    elements = rico._html.parse_html(text)

    assert isinstance(elements, tuple)
    assert len(elements) == 1

    svg = elements[0]
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

    path = tuple(svg)[0]
    assert isinstance(path, ET.Element)
    assert path.tag == "path"
    assert path.attrib == {
        "d": "M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z",
    }
    assert path.text is None
    assert path.tail is None
    assert len(path) == 0


@pytest.fixture
def sample_elem():
    div0 = ET.Element("div", {"class": "container"})
    div0.text = "\n"
    p0 = ET.SubElement(div0, "p")
    p0.text = " Hello "
    p0.tail = "\n"
    strong = ET.SubElement(p0, "strong")
    strong.text = " world "
    strong.tail = " ! "
    div1 = ET.SubElement(div0, "div", {"class": '>&"'})
    div1.text = "\n"
    div1.tail = "\n"
    code0 = ET.SubElement(div1, "code")
    code0.text = " should be indented "
    code0.tail = "\n"
    pre = ET.SubElement(div0, "pre")
    pre.text = "\n"
    pre.tail = "\n"
    code1 = ET.SubElement(pre, "code")
    code1.text = " should not be indented "
    code1.tail = "\n"
    p1 = ET.SubElement(div0, "p")
    p1.text = " Hello >&< "
    p1.tail = "\n"
    br = ET.SubElement(p1, "br")
    br.tail = " world again "
    return div0


def test_indent_html_default(sample_elem: ET.Element):
    expectation = textwrap.dedent("""\
        <div class="container">
          <p> Hello <strong> world </strong> ! </p>
          <div class="&gt;&amp;&quot;">
            <code> should be indented </code>
          </div>
          <pre>
        <code> should not be indented </code>
        </pre>
          <p> Hello &gt;&amp;&lt; <br> world again </p>
        </div>""")

    assert elem_to_string(rico._html.indent_html(sample_elem)) == expectation


def test_indent_html_custom_space(sample_elem: ET.Element):
    expectation = textwrap.dedent("""\
        <div class="container">
            <p> Hello <strong> world </strong> ! </p>
            <div class="&gt;&amp;&quot;">
                <code> should be indented </code>
            </div>
            <pre>
        <code> should not be indented </code>
        </pre>
            <p> Hello &gt;&amp;&lt; <br> world again </p>
        </div>""")

    assert elem_to_string(
        rico._html.indent_html(sample_elem, "    ")) == expectation


def test_strip_html(sample_elem: ET.Element):
    p = ET.Element("p")
    p.text = " Hello world again again "
    sample_elem.append(p)

    expectation = (
        '<div class="container"><p>Hello <strong> world </strong> !</p>'
        '<div class="&gt;&amp;&quot;"><code> should be indented </code></div><pre>\n'
        "<code> should not be indented </code>\n"
        "</pre><p>Hello &gt;&amp;&lt; <br>world again</p>"
        "<p>Hello world again again</p></div>"
    )

    assert elem_to_string(rico._html.strip_html(sample_elem)) == expectation


def test_serialize_html_default(sample_elem: ET.Element):
    expectation = textwrap.dedent("""\
        <div class="container">
        <p> Hello <strong> world </strong> ! </p>
        <div class="&gt;&amp;&quot;">
        <code> should be indented </code>
        </div>
        <pre>
        <code> should not be indented </code>
        </pre>
        <p> Hello &gt;&amp;&lt; <br> world again </p>
        </div>""")

    assert rico._html.serialize_html(sample_elem) == expectation


def test_serialize_html_indent(sample_elem: ET.Element):
    expectation = textwrap.dedent("""\
        <div class="container">
            <p> Hello <strong> world </strong> ! </p>
            <div class="&gt;&amp;&quot;">
                <code> should be indented </code>
            </div>
            <pre>
        <code> should not be indented </code>
        </pre>
            <p> Hello &gt;&amp;&lt; <br> world again </p>
        </div>""")

    assert rico._html.serialize_html(
        sample_elem, indent=True, space="    ") == expectation


def test_serialize_html_strip(sample_elem: ET.Element):
    expectation = (
        '<div class="container"><p>Hello <strong> world </strong> !</p>'
        '<div class="&gt;&amp;&quot;"><code> should be indented </code></div><pre>\n'
        "<code> should not be indented </code>\n"
        "</pre><p>Hello &gt;&amp;&lt; <br>world again</p></div>"
    )

    assert rico._html.serialize_html(sample_elem, strip=True) == expectation


def test_serialize_html_bool_attr(sample_elem: ET.Element):
    sample_elem.set("autofocus", None)  # type: ignore
    expectation = textwrap.dedent("""\
        <div class="container" autofocus>
        <p> Hello <strong> world </strong> ! </p>
        <div class="&gt;&amp;&quot;">
        <code> should be indented </code>
        </div>
        <pre>
        <code> should not be indented </code>
        </pre>
        <p> Hello &gt;&amp;&lt; <br> world again </p>
        </div>""")

    assert rico._html.serialize_html(sample_elem) == expectation
    sample_elem.set("autofocus", True)  # type: ignore
    assert rico._html.serialize_html(sample_elem) == expectation

    sample_elem.set("autofocus", False)  # type: ignore
    expectation = textwrap.dedent("""\
        <div class="container">
        <p> Hello <strong> world </strong> ! </p>
        <div class="&gt;&amp;&quot;">
        <code> should be indented </code>
        </div>
        <pre>
        <code> should not be indented </code>
        </pre>
        <p> Hello &gt;&amp;&lt; <br> world again </p>
        </div>""")
    assert rico._html.serialize_html(sample_elem) == expectation


def test_serialize_html_style():
    elem = ET.Element("style")
    elem.text = ".>&< {border: none;}"
    assert rico._html.serialize_html(elem) == "<style>.>&< {border: none;}</style>"
