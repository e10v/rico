from __future__ import annotations

import xml.etree.ElementTree as ET

import rico._container
import rico._content


def test_div():
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
