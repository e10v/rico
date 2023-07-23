"""Styles and scripts."""

import rico


if __name__ == "__main__":
    dark_theme = "https://cdn.jsdelivr.net/npm/bootswatch@5/dist/darkly/bootstrap.min.css"
    jquery = "https://cdn.jsdelivr.net/npm/jquery@3/dist/jquery.min.js"

    # Extra styles and scripts
    doc = rico.Doc(
        rico.Text("Click me", class_="click"),
        extra_styles=(
            rico.Style(src=dark_theme),
            rico.Style(".click {color: yellow;}"),
        ),
        extra_scripts=(
            rico.Script(src=jquery),
            rico.Script(
                "$('p').on('click', function() {alert('Hello world!');})",
                defer=True,
            ),
        ),
    )

    with open(__file__[:-3] + "_extra.html", "w") as f:
        f.write(doc.serialize(indent=True))

    # Extra styles and scripts inline
    doc = rico.Doc(
        rico.Text("Click me", class_="click"),
        extra_styles=(
            rico.Style(src=dark_theme, inline=True),
            rico.Style(".click {color: yellow;}"),
        ),
        extra_scripts=(
            rico.Script(src=jquery, inline=True),
            rico.Script(
                "$('p').on('click', function() {alert('Hello world!');})",
                defer=True,
            ),
        ),
    )

    with open(__file__[:-3] + "_inline.html", "w") as f:
        f.write(doc.serialize(indent=True))

    # All extra styles and scripts inline
    with rico.config_context(inline_styles=True, inline_scripts=True):
        doc = rico.Doc(
            rico.Text("Click me", class_="click"),
            extra_styles=(
                rico.Style(src=dark_theme),
                rico.Style(".click {color: yellow;}"),
            ),
            extra_scripts=(
                rico.Script(src=jquery),
                rico.Script(
                    "$('p').on('click', function() {alert('Hello world!');})",
                    defer=True,
                ),
            ),
        )

    with open(__file__[:-3] + "_inline_all.html", "w") as f:
        f.write(doc.serialize(indent=True))
