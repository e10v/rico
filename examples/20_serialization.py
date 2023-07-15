"""Serialization examples."""

import pandas as pd

import rico


if __name__ == "__main__":
    df = pd.DataFrame({
        "a": list("CCCDDDEEE"),
        "b": [2, 7, 4, 1, 2, 6, 8, 4, 7],
    })
    plot = df.plot.scatter(x="a", y="b")  # type: ignore

    doc = rico.Doc("Hello world!", df, plot, title="My doc")

    # Default
    with open(__file__[:-3] + "_default.html", "w") as f:
        f.write(str(doc))

    # Indent
    with open(__file__[:-3] + "_indent.html", "w") as f:
        f.write(doc.serialize(indent=True))

    # Indent with custom space
    with open(__file__[:-3] + "_indent_space.html", "w") as f:
        f.write(doc.serialize(indent=True, space="    "))

    # Remove unnecessary whitespace
    with open(__file__[:-3] + "_strip.html", "w") as f:
        f.write(doc.serialize(strip=True))
