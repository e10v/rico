from __future__ import annotations

import textwrap
import xml.etree.ElementTree as ET  # noqa: N817

import pytest

from rico import html


def elem_to_string(elem: ET.Element | list[ET.Element], sep: str = "") -> str:
    if isinstance(elem, list):
        return sep.join(elem_to_string(e) for e in elem)
    return ET.tostring(elem, encoding="unicode", method="html")


def test_html_parser_two_elements():
    text = "<p>Hello</p><p>world</p>"
    parser = html.HTMLParser()
    parser.feed(text)
    elements = parser.close()

    assert elem_to_string(elements) == text
    assert isinstance(elements, list)
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


def test_html_parser_nested_tags():
    text = "<div><p>Hello <strong>world</strong>!</p></div>"
    parser = html.HTMLParser()
    parser.feed(text)
    elements = parser.close()

    assert elem_to_string(elements) == text
    assert isinstance(elements, list)
    assert len(elements) == 1

    div = elements[0]
    assert isinstance(div, ET.Element)
    assert div.tag == "div"
    assert div.attrib == {}
    assert div.text is None
    assert div.tail is None
    assert len(div) == 1

    p = list(div)[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {}
    assert p.text == "Hello "
    assert p.tail is None
    assert len(p) == 1

    strong = list(p)[0]
    assert isinstance(strong, ET.Element)
    assert strong.tag == "strong"
    assert strong.attrib == {}
    assert strong.text == "world"
    assert strong.tail == "!"
    assert len(strong) == 0


def test_html_parser_attributes():
    script_src = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"
    text = f"<script defer src='{script_src}' crossorigin='anonymous'></script>"
    parser = html.HTMLParser()
    parser.feed(text)
    elements = parser.close()

    assert isinstance(elements, list)
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


def test_html_parser_svg():
    text = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'width="16" height="16" fill="currentColor" class="bi bi-dash">'
        '<path d="M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z"/>'
        "</svg>"
    )
    parser = html.HTMLParser()
    parser.feed(text)
    elements = parser.close()

    assert isinstance(elements, list)
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

    path = list(svg)[0]
    assert isinstance(path, ET.Element)
    assert path.tag == "path"
    assert path.attrib == {
        "d": "M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z",
    }
    assert path.text is None
    assert path.tail is None
    assert len(path) == 0


def test_parse_html():
    text = "<p>Hello world</p>"
    elements = html.parse_html(text)

    assert elem_to_string(elements) == text
    assert isinstance(elements, list)
    assert len(elements) == 1

    p = elements[0]
    assert isinstance(p, ET.Element)
    assert p.tag == "p"
    assert p.attrib == {}
    assert p.text == "Hello world"
    assert p.tail is None
    assert len(p) == 0


@pytest.fixture
def sample_elem():
    root = ET.Element("div", {"class": "container"})
    p1 = ET.SubElement(root, "p")
    p1.text = "Hello "
    strong = ET.SubElement(p1, "strong")
    strong.text = "world"
    strong.tail = "!"
    div = ET.SubElement(root, "div", {"class": '>&"'})
    code1 = ET.SubElement(div, "code")
    code1.text = "should be indented"
    pre = ET.SubElement(root, "pre")
    code2 = ET.SubElement(pre, "code")
    code2.text = "should not be indented"
    p2 = ET.SubElement(root, "p2")
    p2.text = "Hello >&<"
    br = ET.SubElement(p2, "br")
    br.tail = "world again"
    return root


def test_indent_html_default(sample_elem: ET.Element):
    expected_output = textwrap.dedent("""\
        <div class="container">
          <p>Hello <strong>world</strong>!</p>
          <div class="&gt;&amp;&quot;">
            <code>should be indented</code>
          </div>
          <pre><code>should not be indented</code></pre>
          <p2>Hello &gt;&amp;&lt;<br>world again</p2>
        </div>""")

    assert elem_to_string(html.indent_html(sample_elem)) == expected_output


def test_indent_html_custom_space(sample_elem: ET.Element):
    expected_output = textwrap.dedent("""\
        <div class="container">
            <p>Hello <strong>world</strong>!</p>
            <div class="&gt;&amp;&quot;">
                <code>should be indented</code>
            </div>
            <pre><code>should not be indented</code></pre>
            <p2>Hello &gt;&amp;&lt;<br>world again</p2>
        </div>""")

    assert elem_to_string(
        html.indent_html(sample_elem, "    ")) == expected_output


def test_serialize_html_default(sample_elem: ET.Element):
    expected_output = (
        '<div class="container">'
        "<p>Hello <strong>world</strong>!</p>"
        '<div class="&gt;&amp;&quot;">'
        "<code>should be indented</code>"
        "</div>"
        "<pre><code>should not be indented</code></pre>"
        "<p2>Hello &gt;&amp;&lt;<br>world again</p2>"
        "</div>"
    )

    assert html.serialize_html(sample_elem) == expected_output


def test_serialize_html_indent(sample_elem: ET.Element):
    expected_output = textwrap.dedent("""\
        <div class="container">
            <p>Hello <strong>world</strong>!</p>
            <div class="&gt;&amp;&quot;">
                <code>should be indented</code>
            </div>
            <pre><code>should not be indented</code></pre>
            <p2>Hello &gt;&amp;&lt;<br>world again</p2>
        </div>""")

    assert html.serialize_html(sample_elem, "    ") == expected_output


def test_serialize_html_bool_attr(sample_elem: ET.Element):
    sample_elem.set("autofocus", None)  # pyright: ignore [reportGeneralTypeIssues]
    expected_output = (
        '<div class="container" autofocus>'
        "<p>Hello <strong>world</strong>!</p>"
        '<div class="&gt;&amp;&quot;">'
        "<code>should be indented</code>"
        "</div>"
        "<pre><code>should not be indented</code></pre>"
        "<p2>Hello &gt;&amp;&lt;<br>world again</p2>"
        "</div>"
    )

    assert html.serialize_html(sample_elem) == expected_output


def test_serialize_html_style():
    elem = ET.Element("style")
    elem.text = ".>&< {border: none;}"
    assert html.serialize_html(elem) == "<style>.>&< {border: none;}</style>"
