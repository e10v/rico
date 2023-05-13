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
        (p0.text, "Hello"),
        (p0.tail, None),
        (p0.attrib, {}),
        (p1, ET.Element),
        (p1.tag, "p"),
        (p1.text, "world"),
        (p1.tail, None),
        (p1.attrib, {}),
        (elem_to_string(elements), two_elements_text),
    ]


nested_tags_text = "<div><p>Hello <strong>world</strong>!</p></div>"

def get_nested_tags_asserts(elements: list[ET.Element]) -> list[tuple[Any, Any]]:
    div = elements[0]
    p = list(div.iter())[1]
    strong = list(p.iter())[1]

    return [
        (elements, list),
        (len(elements), 1),
        (div, ET.Element),
        (div.tag, "div"),
        (div.text, None),
        (div.tail, None),
        (div.attrib, {}),
        (p, ET.Element),
        (p.tag, "p"),
        (p.text, "Hello "),
        (p.tail, None),
        (p.attrib, {}),
        (strong, ET.Element),
        (strong.tag, "strong"),
        (strong.text, "world"),
        (strong.tail, "!"),
        (strong.attrib, {}),
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
        (script.text, None),
        (script.tail, None),
        (script.attrib, {
            "defer": None,
            "src": script_src,
            "crossorigin": "anonymous",
        }),
    ]


parser_args = [
    (two_elements_text, get_two_elements_asserts),
    (nested_tags_text, get_nested_tags_asserts),
    (attributes_text, get_attributes_asserts),
]

parser_ids = ["two_elements", "nested_tags", "attributes"]


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
def sample_html_indent():
    root = ET.Element("div")
    p1 = ET.SubElement(root, "p")
    p1.text = "Hello "
    strong = ET.SubElement(p1, "strong")
    strong.text = "world"
    strong.tail = "!"
    div = ET.SubElement(root, "div")
    code1 = ET.SubElement(div, "code")
    code1.text = "should be indented"
    pre = ET.SubElement(root, "pre")
    code2 = ET.SubElement(pre, "code")
    code2.text = "should not be indented"
    p2 = ET.SubElement(root, "p2")
    p2.text = "Hello"
    br = ET.SubElement(p2, "br")
    br.tail = "world again"

    return root


def test_indent_html_default(sample_html_indent: ET.Element):
    expected_output = textwrap.dedent("""\
        <div>
          <p>Hello <strong>world</strong>!</p>
          <div>
            <code>should be indented</code>
          </div>
          <pre><code>should not be indented</code></pre>
          <p2>Hello<br>world again</p2>
        </div>""")

    assert elem_to_string(html.indent_html(sample_html_indent)) == expected_output


def test_indent_html_custom_space(sample_html_indent: ET.Element):
    expected_output = textwrap.dedent("""\
        <div>
            <p>Hello <strong>world</strong>!</p>
            <div>
                <code>should be indented</code>
            </div>
            <pre><code>should not be indented</code></pre>
            <p2>Hello<br>world again</p2>
        </div>""")

    assert elem_to_string(
        html.indent_html(sample_html_indent, "    ")) == expected_output
