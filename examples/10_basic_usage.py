"""Basic usage examples."""

import pandas as pd

import rico


if __name__ == "__main__":
    df = pd.DataFrame({
        "a": list("CCCDDDEEE"),
        "b": [2, 7, 4, 1, 2, 6, 8, 4, 7],
    })
    plot = df.plot.scatter(x="a", y="b")  # type: ignore

    # Declarative API
    doc = rico.Doc("Hello world!", df, plot, title="My doc")

    with open(__file__[:-3] + "_declarative.html", "w") as f:
        f.write(doc.serialize(indent=True))

    # Imperative API
    doc = rico.Doc(title="My doc")
    doc.append("Hello world!")
    doc.append(df, plot)

    with open(__file__[:-3] + "_imperative.html", "w") as f:
        f.write(doc.serialize(indent=True))
