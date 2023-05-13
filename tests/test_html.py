from __future__ import annotations

import inspect
import textwrap
from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET  # noqa: N817

import pytest

from rico import html


if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    ParserAssertsFn = Callable[[list[ET.Element]], list[tuple[Any, Any]]]


def elem_to_string(elem: ET.Element | list[ET.Element], sep: str = "") -> str:
    if isinstance(elem, list):
        return sep.join(elem_to_string(e) for e in elem)
    return ET.tostring(elem, encoding="unicode", method="html")


two_elements_text = "<p>Hello</p><p>world</p>"

def get_two_elements_asserts(elements: list[ET.Element]) -> list[tuple[Any, Any]]:
    p0 = elements[0]
    p1 = elements[1]

    return [
        (elements, list),
        (len(elements), 2),
        (p0, ET.Element),
        (p0.tag, "p"),
        (p0.attrib, {}),
        (p0.text, "Hello"),
        (p0.tail, None),
        (p1, ET.Element),
        (p1.tag, "p"),
        (p1.attrib, {}),
        (p1.text, "world"),
        (p1.tail, None),
        (elem_to_string(elements), two_elements_text),
    ]


nested_tags_text = "<div><p>Hello <strong>world</strong>!</p></div>"

def get_nested_tags_asserts(elements: list[ET.Element]) -> list[tuple[Any, Any]]:
    div = elements[0]
    p = list(div)[0]
    strong = list(p)[0]

    return [
        (elements, list),
        (len(elements), 1),
        (div, ET.Element),
        (div.tag, "div"),
        (div.attrib, {}),
        (div.text, None),
        (div.tail, None),
        (p, ET.Element),
        (p.tag, "p"),
        (p.attrib, {}),
        (p.text, "Hello "),
        (p.tail, None),
        (strong, ET.Element),
        (strong.tag, "strong"),
        (strong.attrib, {}),
        (strong.text, "world"),
        (strong.tail, "!"),
        (elem_to_string(elements), nested_tags_text),
    ]


script_src = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"
attributes_text = (
    f"<script defer src='{script_src}' crossorigin='anonymous'></script>")

def get_attributes_asserts(elements: list[ET.Element]) -> list[tuple[Any, Any]]:
    script = elements[0]

    return [
        (elements, list),
        (len(elements), 1),
        (script, ET.Element),
        (script.tag, "script"),
        (script.attrib, {
            "defer": None,
            "src": script_src,
            "crossorigin": "anonymous",
        }),
        (script.text, None),
        (script.tail, None),
    ]

svg_text = (
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'xmlns:xlink="http://www.w3.org/1999/xlink" '
    'width="16" height="16" fill="currentColor" class="bi bi-dash">'
    '<path d="M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z"/>'
    "</svg>"
)

def get_svg_asserts(elements: list[ET.Element]) -> list[tuple[Any, Any]]:
    svg = elements[0]
    path = list(svg)[0]

    return [
        (elements, list),
        (len(elements), 1),
        (svg, ET.Element),
        (svg.tag, "svg"),
        (svg.attrib, {
            "xmlns": "http://www.w3.org/2000/svg",
            "xmlns:xlink": "http://www.w3.org/1999/xlink",
            "width": "16",
            "height": "16",
            "fill": "currentColor",
            "class": "bi bi-dash",
        }),
        (svg.text, None),
        (svg.tail, None),
        (path.tag, "path"),
        (path.attrib, {
            "d": "M4 8a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7A.5.5 0 0 1 4 8z",
        }),
        (path.text, None),
        (path.tail, None),
    ]


parser_args = [
    (two_elements_text, get_two_elements_asserts),
    (nested_tags_text, get_nested_tags_asserts),
    (attributes_text, get_attributes_asserts),
    (svg_text, get_svg_asserts),
]

parser_ids = ["two_elements", "nested_tags", "attributes", "svg"]


def compare(left: Any, right: Any) -> bool:
    if right is None:
        return left is None
    if inspect.isclass(right):
        return isinstance(left, right)
    return left == right


@pytest.mark.parametrize(("text", "fn"), parser_args, ids=parser_ids)
def test_html_parser(text: str, fn: ParserAssertsFn):
    parser = html.HTMLParser()
    parser.feed(text)
    elements = parser.close()

    for left, right in fn(elements):
        assert compare(left, right)


@pytest.mark.parametrize(("text", "fn"), parser_args, ids=parser_ids)
def test_parse_html(text: str, fn: ParserAssertsFn):
    elements = html.parse_html(text)

    for left, right in fn(elements):
        assert compare(left, right)


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
