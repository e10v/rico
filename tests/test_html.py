import xml.etree.ElementTree as ET  # noqa: N817

from rico import html


def test_html_parser_simple_html():
    parser = html.HTMLParser()
    parser.feed("<p>Hello world</p>")
    root = parser.close()

    assert root.tag == "div"
    assert isinstance(root, ET.Element)

    elements = list(root.iter())
    p = elements[1]
    assert len(elements) == 2
    assert p.tag == "p"
    assert p.text == "Hello world"

    assert ET.tostring(root).decode() == "<div><p>Hello world</p></div>"


def test_html_parser_nested_tags():
    parser = html.HTMLParser()
    parser.feed("<div><p>Hello <strong>world</strong>!</p></div>")
    root = parser.close()

    assert root.tag == "div"
    assert isinstance(root, ET.Element)

    div = list(root.iter())[1]
    assert div.tag == "div"
    assert div.text is None

    p = list(div.iter())[1]
    assert p.tag == "p"
    assert p.text == "Hello "

    strong = list(p.iter())[1]
    assert strong.tag == "strong"
    assert strong.text == "world"
    assert strong.tail == "!"

    assert ET.tostring(root).decode() == (
        "<div><div><p>Hello <strong>world</strong>!</p></div></div>")


def test_html_parser_custom_root():
    parser = html.HTMLParser(root="body")
    parser.feed("<div>Hello world</div>")
    root = parser.close()

    assert root.tag == "body"
    assert isinstance(root, ET.Element)

    div = list(root.iter())[1]
    assert div.tag == "div"
    assert div.text == "Hello world"

    assert ET.tostring(root).decode() == "<body><div>Hello world</div></body>"
