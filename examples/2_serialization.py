"""Serialization."""

import pandas as pd

import rico


if __name__ == "__main__":
    df = pd.DataFrame(
        {
            "x": [2, 7, 4, 1, 2, 6, 8, 4, 7],
            "y": [1, 9, 2, 8, 3, 7, 4, 6, 5],
        },
        index=pd.Index(list("AAABBBCCC")),
    )
    plot = df.plot.scatter(x="x", y="y")  # type: ignore

    doc = rico.Doc("Hello, World!", df, plot, title="Serialization")

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
