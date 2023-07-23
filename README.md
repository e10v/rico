# rico: rich content to HTML as easy as Doc(df, plot)

**rico** is a Python package for creating HTML documents from rich content: dataframes, plots, images, markdown etc. It provides a high-level, easy-to-use API with reasonable defaults, as well as low-level access for better control.

Use **rico** if you want to create an HTML document from objects created in a Python script.

With **rico** you can *avoid*:
* Writing data to intermediate files or a database from a script.
* Loading data into a Jupyter notebook from intermediate files or a database.
* Using nbconvert or similar tools for creating HTML files.

More on the topic:
* [Pass pandas dataframe to notebook via nbconvert](https://github.com/jupyter/nbconvert/issues/1070).
* [Could Papermill pass an in-memory dataframe to a notebook?](https://github.com/nteract/papermill/issues/406)

[![CI](https://github.com/e10v/rico/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/e10v/rico/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/github/e10v/rico/coverage.svg?branch=main)](https://codecov.io/gh/e10v/rico)
[![License](https://img.shields.io/github/license/e10v/rico)](https://github.com/e10v/rico/blob/main/LICENSE)
[![Version](https://img.shields.io/pypi/v/rico.svg)](https://pypi.org/project/rico/)
[![Package Status](https://img.shields.io/pypi/status/rico.svg)](https://pypi.org/project/rico/)
[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/rico.svg)](https://pypi.org/project/rico/)

## Installation

```bash
pip install rico
```

**rico** has no dependencies other than the standard Python packages.

For Markdown support:
* install [markdown-it-py](https://github.com/executablebooks/markdown-it-py),
* or install [Python Markdown](https://github.com/Python-Markdown/),
* or set your own Markdown renderer using `rico.set_config`.

### Deprecated

Optional additional dependencies were required to support the following content types:
* Plots (`rico[altair]`, `rico[pyplot]`, `rico[seaborn]`).
* Markdown (`rico[markdown]`).

The `rico[complete]` extra incudes all the dependencies above.

They are no longer needed and will be removed in version 0.4.0.

## User guide

To get started with **rico**, take a look at the self-explanatory [examples](https://github.com/e10v/rico/tree/main/examples) with resulting HTML documents. The user guide contains a slightly more detailed explanation.

### Basic usage

**rico** provides both declarative and imperative style interfaces.

Declarative style:
```python
import pandas as pd
import rico

df = pd.DataFrame(
    {
        "x": [2, 7, 4, 1, 2, 6, 8, 4, 7],
        "y": [1, 9, 2, 8, 3, 7, 4, 6, 5],
    },
    index=pd.Index(list("AAABBBCCC")),
)
plot = df.plot.scatter(x="x", y="y")

doc = rico.Doc("Hello, World!", df, plot, title="My doc")
```

Imperative style:
```python
doc = rico.Doc(title="My doc")
doc.append("Hello, World!", df, plot)
```

Also imperative style:
```python
doc = rico.Doc(title="My doc")
doc.append("Hello, World!")
doc.append(df)
doc.append(plot)
```

Mix-and-match:
```python
doc = rico.Doc("Hello, World!", df, title="My doc")
doc.append(plot)
```

### Serialization

Serialize the document to HTML using `str(doc)`:
```python
with open("doc.html", "w") as f:
    f.write(str(doc))
```

Implicit serialization:
```python
with open("doc.html", "w") as f:
    print(doc, file=f)
```

Internally, `str(doc)` calls `doc.serialize()` with default parameter values. Call `doc.serialize(indent=True)` to indent the HTML element tree visually:
```python
with open("doc.html", "w") as f:
    f.write(doc.serialize(indent=True))
```

Set custom whitespace for indentation using the `space` parameter:
```python
with open("doc.html", "w") as f:
    f.write(doc.serialize(indent=True, space="    "))
```

Remove unnecessary whitespace by setting `strip` to `True`:
```python
with open("doc.html", "w") as f:
    f.write(doc.serialize(strip=True))
```

Control the default behavior of `str(doc)` and `doc.serialize()` using the global options `indent_html`, `indent_space`, and `strip_html`:
```python
with open("doc.html", "w") as f, rico.config_context(indent_html=True):
    f.write(str(doc))
```

The default option values are:
* `indent_html = False`,
* `indent_space = "  "`,
* `strip_html = False`.

### Rich content types

**rico** automatically recognizes the following content types:
* `rico` content classes (subclasses of `rico.ContentBase`).
* Matplotlib Pyplot Plots.
* Dataframes and other types with [IPython rich representation methods](https://ipython.readthedocs.io/en/stable/config/integrating.html).
* Text.

Use specific classes for plots and texts to change the default behavior:
```python
doc = rico.Doc(
    rico.Text("Hello, World!", mono=True),  # The default value is False.
    df,
    rico.Plot(plot, format="png", bbox_inches="tight"),  # The default value is "svg".
    title="My doc",
)
```

The following code gives the same result as the code above:
```python
doc = rico.Doc(title="My doc")
doc.append_text("Hello, World!", mono=True)
doc.append(df)
doc.append_plot(plot, format="png", bbox_inches="tight")
```

Some options can be set in the global configuration:
```python
with rico.config_context(text_mono=True, image_format="png"):
    doc = rico.Doc("Hello, World!", df, plot, title="My doc")
```

Use specific classes and methods for other content types:
* Images: `Image` or `Doc.append_image`.
* Code: `Code` or `Doc.append_code`.
* Markdown*: `Markdown` or `Doc.append_markdown`.
* HTML tag: `Tag` or `Doc.append_tag`.
* Raw HTML: `HTML` or `Doc.append_html`.

*Install [markdown-it-py](https://github.com/executablebooks/markdown-it-py) or [markdown](https://github.com/Python-Markdown/markdown/), or define a custom Markdown renderer with the `markdown_renderer` global option to use `Markdown` or `Doc.append_markdown`.

For example:
```python
doc = rico.Doc(
    rico.Markdown("## Dataframe"),
    df,
    rico.Tag("h2", "Plot"),  # An alternative way to add a header.
    plot,
    rico.HTML("<h2>Code</h2>"),  # Another way to add a header.
    rico.Code("print('Hello, World!')"),
    title="My doc",
)
```

The following code gives the same result as the code above:
```python
doc = rico.Doc(title="My doc")
doc.append_markdown("## Dataframe")
doc.append(df)
doc.append_tag("h2", "Plot")
doc.append(plot)
doc.append_html("<h2>Code</h2>")
doc.append_code("print('Hello, World!')")
```

Check the docstrings for details.

Serialize content to HTML using `str(object)` or `object.serialize()`:
```python
obj = rico.Tag("p", "Hello, World!")

print(obj)
# <div><p>Hello, World!</p></div>

print(obj.serialize(indent=True, space="    "))
# <div>
#     <p>Hello, World!</p>
# </div>
```

### Bootstrap, HTML classes and document layout

By default, [Bootstrap](https://getbootstrap.com/) styles are included in the document. Change the default behavior using the `bootstrap` parameter:
```python
doc = rico.Doc("Hello, World!", bootstrap="full")
```

* Set `bootstrap` to `"css"` (default) to include only CSS.
* Set `bootstrap` to `"full"` to include both the CSS and JS.
* Set `bootstrap` to `"none"` to not include Bootstrap*.

*Keep in mind that **rico** relies on Bootstrap classes and styles. For example:
* The `mono` and `wrap` parameters of the `Text` class use Bootstrap's `font-monospace` and `font-monospace` classes.
* **rico**'s dataframe style definition uses Bootstrap variables.

Each content element is wrapped in a `<div>` container. Specify the element's container class using the `class_` parameter:
```python
print(rico.Tag("p", "Hello, World!", class_="col"))
# <div class="col"><p>Hello, World!</p></div>
```

All elements' containers in the document are also wrapped in a `<div>` container. Specify the document's container class using the `class_` parameter:
```python
doc = rico.Doc("Hello, World!", class_="container-fluid")
```

Define the document layout using Bootstrap and `Div` class:
```python
doc = rico.Doc(rico.Div(
    rico.Obj(df, class_="col"),
    rico.Obj(plot, class_="col"),
    class_="row row-cols-auto",
))
```

The code above creates a document with two columns, one with a dataframe and another with a plot. The `Obj` is a magic class which automatically determines the content type in the same way that `Doc` and `Doc.append` do.

Another example:
```python
import altair as alt

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
```

The following code gives the same result as the code above:
```python
doc = rico.Doc(title="Grid system")

doc.append_tag("h2", "Dataframes")
div1 = rico.Div(class_="row row-cols-auto")
doc.append(div1)
for name, data in df.groupby(df.index):
    div1.append(rico.Tag("h3", name), data, class_="col")

doc.append_tag("h2", "Plots")
div2 = rico.Div(class_="row row-cols-auto")
doc.append(div2)
for name, data in df.groupby(df.index):
    div2.append(
        rico.Tag("h3", name),
        alt.Chart(data).mark_point().encode(x="x", y="y"),
        class_="col",
    )
```

More on Bootstrap layout and grid system:
* [Breakpoints](https://getbootstrap.com/docs/5.3/layout/breakpoints/)
* [Containers](https://getbootstrap.com/docs/5.3/layout/containers/)
* [Grid system](https://getbootstrap.com/docs/5.3/layout/grid/)
* [Columns](https://getbootstrap.com/docs/5.3/layout/columns/)

### Styles and scripts

By default, **rico** includes the following styles in the document:
* Bootstrap CSS. Change the default behavior using the `bootstrap` parameter of the `Doc` class.
* Dataframe style. Change it by setting the `dataframe_style` global option.

Exclude dataframe style from the document by setting `dataframe_style` to `""`:
```python
with rico.config_context(dataframe_style=""):
    doc = rico.Doc(df)
```

Include custom styles and scripts using the `Style` and `Script` classes:
```python
dark_theme = "https://cdn.jsdelivr.net/npm/bootswatch@5/dist/darkly/bootstrap.min.css"
jquery = "https://cdn.jsdelivr.net/npm/jquery@3/dist/jquery.min.js"

doc = rico.Doc(
    rico.Text("Click me", class_="click"),
    extra_styles=(
        rico.Style(src=dark_theme),
        rico.Style(".click {color: yellow;}"),
    ),
    extra_scripts=(
        rico.Script(src=jquery),
        rico.Script(
            "$('p').on('click', function() {alert('Hello, World!');})",
            defer=True,
        ),
    ),
)
```

The `defer` parameter adds the `defer` attribute to the `<script>` tag if the `src` parameter is used. Otherwise, if the `text` parameter is used, the script is placed in the footer of the document.

By default, external styles and scripts are included as file links. This means that these files must be available when someone opens the document. Include the contents of these files in the document using the `inline` parameter:
```python
doc = rico.Doc(
    rico.Text("Click me", class_="click"),
    extra_styles=(
        rico.Style(src=dark_theme, inline=True),
        rico.Style(".click {color: yellow;}"),
    ),
    extra_scripts=(
        rico.Script(src=jquery, inline=True),
        rico.Script(
            "$('p').on('click', function() {alert('Hello, World!');})",
            defer=True,
        ),
    ),
)
```

In the example above, the Bootstrap styles are still included as a link. Use the global options `inline_styles` and `inline_scripts` to include the contents of the style and script files in the document:
```python
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
                "$('p').on('click', function() {alert('Hello, World!');})",
                defer=True,
            ),
        ),
    )
```

Keep in mind that style and script files can contain links to other external resources. **rico** doesn't parse or change them, even if the `inline` parameter or the `inline_styles` and `inline_scripts` global options are set to `True`. As a result:
* These resurces should be availble when someone opens an HTML document created by **rico**.
* Links with relative paths to external resources will not work.

For example, [Bootstrap Icons CSS](https://cdn.jsdelivr.net/npm/bootstrap-icons@1/font/bootstrap-icons.css) contains linkes to fonts with relative paths: `url("./fonts/bootstrap-icons.woff2?1fa40e8900654d2863d011707b9fb6f2")`. Including this CSS file with the `inline` parameter set to `True` will make these links invalid.

### Global configuration

Use global configuration to:
* Get or set default parameter values.
* Get or set document properties.
* Get or set a markdown renderer method.

The following global options define the default parameter values:

| Global option    | Parameter | Classes, methods, functions       |
|:-----------------|:----------|:----------------------------------|
| `indent_html`    | `indent`  | `obj.serialize`, `serialize_html` |
| `indent_space`   | `space`   | `obj.serialize`, `serialize_html` |
| `strip_html`     | `strip`   | `obj.serialize`, `serialize_html` |
| `text_mono`      | `mono`    | `Text`, `obj.append_text`         |
| `text_wrap`      | `wrap`    | `Text`, `obj.append_text`         |
| `image_format`   | `format`  | `Plot`, `obj.append_plot`         |
| `inline_styles`  | `inline`  | `Style`                           |
| `inline_scripts` | `inline`  | `Script`                          |

The following global options define document properties:
* `meta_charset` defines a document [charset](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta#charset) metadata. Set it to `""` to disable.
* `meta_viewport` defines a document [viewport](https://developer.mozilla.org/en-US/docs/Web/HTML/Viewport_meta_tag) metadata. Set it to `""` to disable.
* `bootstrap_css` defines a link to the Bootstrap CSS file.
* `bootstrap_js` defines a link to the Bootstrap JS file.
* `dataframe_style` defines a dataframe style. Set it to `""` to disable.

The `markdown_renderer` global option defines a callable that converts Markdown to HTML. It should accept a Markdown string as the first argument and return HTML as a string. The default value is defined as follows:
* If the `markdown_it` module can be imported, then the default value is `markdown_it.MarkdownIt().render`.
* Otherwise, if the `markdown` module can be imported, then the default value is `markdown.markdown`.
* Otherwise, the default value is `None`. In this case, calling `rico.Markdown` or `obj.append_markdown` will throw an error.

Get a dictionary with global options using `get_config` without parameters:
```python
global_config = rico.get_config()
print(global_config["indent_html"])
# False
```

Get a global option value using `get_config` with the option name as a parameter:
```python
print(rico.get_config("indent_html"))
# False
```

Set a global option value using `set_config`:
```python
rico.set_config(indent_html=True)
print(rico.get_config("indent_html"))
# True
rico.set_config(indent_html=False)
```

Set a global option value within a context using `config_context`:
```python
with rico.config_context(indent_html=True):
    print(rico.get_config("indent_html"))
    # True

print(rico.get_config("indent_html"))
# False
```

### Low-level control

Internally, **rico** uses the standard [xml.etree.ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html) module:
* Every content object (`Tag`, `Text`, `Div` etc.) has a `container` attribute of type `xml.etree.ElementTree.Element`. The value is a `<div>` container element.
* `Doc` objects has additional attributes `html`, `head`, and `body` of type `xml.etree.ElementTree.Element`. They represent the `<html>`, `<head>`, and `<body>` elements, respectively.

Access these attributes and use `xml.etree.ElementTree` API to gain low-level control over the document and its elements.

Also, **rico** provides the following functions for working with `xml.etree.ElementTree.Element` objects:
* `parse_html` parses HTML from a string.
* `indent_html` indents an HTML element tree visually.
* `strip_html` removes unnecessary whitespace.
* `serialize_html` serializes `xml.etree.ElementTree.Element` object.

Check the docstrings for details.

## Alternatives

* Use [Jupyter Notebook](https://jupyter.org/) for interactive computing.
* Use [nbconvert](https://nbconvert.readthedocs.io/) or [papermill](https://papermill.readthedocs.io/) if you're processing data and creating objects for a document in a Jupyter notebook.
* Use [Quarto](https://quarto.org/) if you prefer R Markdown style notebooks and a variety of output formats.
* Use [xml.etree.ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html), [lxml](https://lxml.de/), [Yattag](https://www.yattag.org/), or [Airium](https://gitlab.com/kamichal/airium) if you need low-level control.

## Roadmap

* Support math equations with [MathJax](https://www.mathjax.org/) and/or [KaTeX](https://katex.org/).
* Support PDF content.
* Create docs with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).
