"""Basic usage."""

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

    # Declarative API
    doc = rico.Doc("Hello, World!", df, plot, title="Basic usage")

    with open(__file__[:-3] + "_decl.html", "w") as f:
        f.write(doc.serialize(indent=True))

    # Imperative API
    doc = rico.Doc(title="Basic usage")
    doc.append("Hello, World!")
    doc.append(df, plot)

    with open(__file__[:-3] + "_imp.html", "w") as f:
        f.write(doc.serialize(indent=True))
