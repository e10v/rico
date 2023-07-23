"""Document layout."""

# pyright: reportUnknownMemberType=false

import altair as alt
import pandas as pd

import rico


if __name__ == "__main__":
    df = pd.DataFrame({
        "x": [2, 7, 4, 1, 2, 6, 8, 4, 7],
        "y": [1, 9, 2, 8, 3, 7, 4, 6, 5],
    }, index=pd.Index(list("AAABBBCCC"), name="code"))

    doc = rico.Doc(df, title="Fluid container", class_="container-fluid")

    with open(__file__[:-3] + "_fluid.html", "w") as f:
        f.write(doc.serialize(indent=True))

    # Declarative style
    doc = rico.Doc(
        rico.Tag("h2", "Dataframes"),
        rico.Div(
            rico.Obj(rico.Tag("h3", "A"), df.loc["A", :], class_="col"),
            rico.Obj(rico.Tag("h3", "B"), df.loc["B", :], class_="col"),
            rico.Obj(rico.Tag("h3", "C"), df.loc["C", :], class_="col"),
            class_="row row-cols-auto",
        ),
        rico.Tag("h2", "Plots"),
        rico.Div(
            rico.Obj(
                rico.Tag("h3", "A"),
                alt.Chart(df.loc["A", :]).mark_point().encode(x="x", y="y"),
                class_="col",
            ),
            rico.Obj(
                rico.Tag("h3", "B"),
                alt.Chart(df.loc["B", :]).mark_point().encode(x="x", y="y"),
                class_="col",
            ),
            rico.Obj(
                rico.Tag("h3", "C"),
                alt.Chart(df.loc["C", :]).mark_point().encode(x="x", y="y"),
                class_="col",
            ),
            class_="row row-cols-auto",
        ),
        title="Grid system",
    )

    with open(__file__[:-3] + "_grid_decl.html", "w") as f:
        f.write(doc.serialize(indent=True))

    # Imperative style
    doc = rico.Doc(title="Grid system")

    doc.append_tag("h2", "Dataframes")
    div1 = rico.Div(class_="row row-cols-auto")
    doc.append(div1)
    for code, data in df.groupby("code"):
        div1.append(rico.Tag("h3", code), data)  # type: ignore

    doc.append_tag("h2", "Plots")
    div2 = rico.Div(class_="row row-cols-auto")
    doc.append(div2)
    for code, data in df.groupby("code"):
        div2.append(
            rico.Tag("h3", code),  # type: ignore
            alt.Chart(data).mark_point().encode(x="x", y="y"),
        )

    with open(__file__[:-3] + "_grid_imp.html", "w") as f:
        f.write(doc.serialize(indent=True))
