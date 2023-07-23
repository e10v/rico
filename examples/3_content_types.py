"""Rich content types."""

import pandas as pd

import rico


if __name__ == "__main__":
    df = pd.DataFrame({
        "a": list("CCCDDDEEE"),
        "b": [2, 7, 4, 1, 2, 6, 8, 4, 7],
    })
    plot = df.plot.scatter(x="a", y="b")  # type: ignore

    # Change the default behavior
    doc = rico.Doc(
        rico.Text("Hello world!", mono=True),  # The default value is False.
        df,
        rico.Plot(plot, format="png"),  # The default value is "svg".
        title="Content classes parameters",
    )

    with open(__file__[:-3] + "_params_classes.html", "w") as f:
        f.write(doc.serialize(indent=True))

    # Change the default behavior
    doc = rico.Doc(title="Content methods parameters")
    doc.append_text("Hello world!", mono=True)
    doc.append(df)
    doc.append_plot(plot, format="png")

    with open(__file__[:-3] + "_params_methods.html", "w") as f:
        f.write(doc.serialize(indent=True))

    # Content specific classes
    doc = rico.Doc(
        rico.Markdown("## Dataframe"),
        df,
        rico.Tag("h2", "Plot"),  # An alternative way to add a header.
        plot,
        rico.HTML("<h2>Code</h2>"),  # Another way to add a header.
        rico.Code("print('Hello world!')"),
        title="Content types",
    )

    with open(__file__[:-3] + "_specific_classes.html", "w") as f:
        f.write(doc.serialize(indent=True))

    doc = rico.Doc(title="Content types")
    doc.append_markdown("## Dataframe")
    doc.append(df)
    doc.append_tag("h2", "Plot")
    doc.append(plot)
    doc.append_html("<h2>Code</h2>")
    doc.append_code("print('Hello world!')")

    with open(__file__[:-3] + "_specific_methods.html", "w") as f:
        f.write(doc.serialize(indent=True))
