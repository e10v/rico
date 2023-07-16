"""Examplse of different rich content types."""

import pandas as pd

import rico


if __name__ == "__main__":
    df = pd.DataFrame({
        "a": list("CCCDDDEEE"),
        "b": [2, 7, 4, 1, 2, 6, 8, 4, 7],
    })
    plot = df.plot.scatter(x="a", y="b")  # type: ignore

    doc = rico.Doc(
        rico.Text("Hello world!", mono=True),  # The default value is False.
        df,
        rico.Plot(plot, format="png"),  # The default value is "svg".
        title="My doc",
    )

    with open(__file__[:-3] + "1.html", "w") as f:
        f.write(doc.serialize(indent=True))

    doc = rico.Doc(
        rico.Markdown("## Dataframe"),
        df,
        rico.Tag("h2", "Plot"),  # An alternative way to add a header.
        plot,
        rico.HTML("<h2>Code</h2>"),  # Another way to add a header.
        rico.Code("print('Hello world!')"),
        title="My doc",
    )

    with open(__file__[:-3] + "2.html", "w") as f:
        f.write(doc.serialize(indent=True))
