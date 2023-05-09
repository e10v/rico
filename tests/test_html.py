from __future__ import annotations

import inspect
from typing import TYPE_CHECKING
import xml.etree.ElementTree as ET  # noqa: N817

import pytest

from rico import html


if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    GetAssertsFn = Callable[[ET.Element], list[tuple[Any, Any]]]


simple_text = "<p>Hello world</p>"

def simple_fn(element: ET.Element) -> list[tuple[Any, Any]]:
    p = list(element.iter())[1]

    return [
        (element.tag, "div"),
        (element, ET.Element),
        (len(list(element.iter())), 2),
        (p.tag, "p"),
        (p.text, "Hello world"),
        (ET.tostring(element).decode(), "<div><p>Hello world</p></div>"),
    ]


nested_tags_text = "<div><p>Hello <strong>world</strong>!</p></div>"

def nested_tags_fn(element: ET.Element) -> list[tuple[Any, Any]]:
    div = list(element.iter())[1]
    p = list(div.iter())[1]
    strong = list(p.iter())[1]

    return [
        (element.tag, "div"),
        (element, ET.Element),
        (div.tag, "div"),
        (div.text, None),
        (p.tag, "p"),
        (p.text, "Hello "),
        (strong.tag, "strong"),
        (strong.text, "world"),
        (strong.tail, "!"),
        (
            ET.tostring(element).decode(),
            "<div><div><p>Hello <strong>world</strong>!</p></div></div>",
        ),
    ]


custom_root_text = "<div>Hello world</div>"

def custom_root_fn(element: ET.Element) -> list[tuple[Any, Any]]:
    div = list(element.iter())[1]

    return [
        (element.tag, "body"),
        (element, ET.Element),
        (div.tag, "div"),
        (div.text, "Hello world"),
        (ET.tostring(element).decode(), "<body><div>Hello world</div></body>"),
    ]


script_src = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/js/bootstrap.bundle.min.js"
attributes_text = (
    f"<script defer src='{script_src}' crossorigin='anonymous'></script>")

def attributes_fn(element: ET.Element) -> list[tuple[Any, Any]]:
    script = list(element.iter())[1]

    return [
        (element.tag, "div"),
        (element, ET.Element),
        (script.tag, "script"),
        (script.text, None),
        (script.attrib, {
            "defer": None,
            "src": script_src,
            "crossorigin": "anonymous",
        }),
    ]


parser_data = [
    (simple_text, simple_fn, "div"),
    (nested_tags_text, nested_tags_fn, "div"),
    (custom_root_text, custom_root_fn, "body"),
    (attributes_text, attributes_fn, "div"),
]

parser_ids = ["simple", "nested_tags", "custom_root", "attributes"]


def compare(left: Any, right: Any) -> bool:
    if right is None:
        return left is None
    if inspect.isclass(right):
        return isinstance(left, right)
    return left == right


@pytest.mark.parametrize(("text", "fn", "root"), parser_data, ids=parser_ids)
def test_html_parser(text: str, fn: GetAssertsFn, root: str):
    parser = html.HTMLParser(root=root)
    parser.feed(text)
    element = parser.close()

    for left, right in fn(element):
        assert compare(left, right)


@pytest.mark.parametrize(("text", "fn", "root"), parser_data, ids=parser_ids)
def test_parse_html(text: str, fn: GetAssertsFn, root: str):
    element = html.parse_html(text, root=root)

    for left, right in fn(element):
        assert compare(left, right)
