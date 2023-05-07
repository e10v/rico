import xml.etree.ElementTree as ET  # noqa: N817

from rico import core


def test_create_element():
    element1 = core.create_element(
        tag="div",
        attrib={"class": "container"},
        id="div1",
    )

    assert isinstance(element1, ET.Element)
    assert element1.tag == "div"
    assert element1.attrib == {"class": "container", "id": "div1"}

    element2 = core.create_element(
        tag="p",
        parent=element1,
        text="Some text",
        tail="Tail",
    )

    assert isinstance(element2, ET.Element)
    assert element2.tag == "p"
    assert element2.text == "Some text"
    assert element2.tail == "Tail"

    elements = list(element1.iter())
    assert len(elements) == 2
    assert elements[1] == element2
