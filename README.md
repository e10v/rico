# rico: rich content to HTML as easy as Doc(df, plot)

**rico** is a Python package for creating HTML documents from rich content: dataframes, plots, images, markdown etc. It provides a high-level, easy-to-use API with reasonable defaults, as well as low-level access for better control.

[![CI](https://github.com/e10v/rico/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/e10v/rico/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/github/e10v/rico/coverage.svg?branch=main)](https://codecov.io/gh/e10v/rico)
[![License](https://img.shields.io/github/license/e10v/rico)](https://github.com/e10v/rico/blob/main/LICENSE)
[![Version](https://img.shields.io/pypi/v/rico.svg)](https://pypi.org/project/rico/)
[![Package Status](https://img.shields.io/pypi/status/rico.svg)](https://pypi.org/project/rico/)
[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/rico.svg)](https://pypi.org/project/rico/)

## Installation

Install the core functionality:
```bash
pip install rico
```

The core functionality has no dependencies other than the standard Python packages. Optional additional dependencies are required to support the following content types:
* Plots. Altair, Matplotlib Pyplot and Seaborn are currently supported.
* Markdown.

Install one or several extras to use plots or Markdown in HTML documents.

[Altair](https://altair-viz.github.io/):
```bash
pip install rico[altair]
```

[Markdown](https://python-markdown.github.io/):
```bash
pip install rico[markdown]
```

[Matplotlib Pyplot](https://matplotlib.org/):
```bash
pip install rico[pyplot]
```

[Seaborn](https://seaborn.pydata.org/):
```bash
pip install rico[seaborn]
```

Install `rico[seaborn]` extra only to use the [seaborn.objects](https://seaborn.pydata.org/tutorial/objects_interface.html) interface. Otherwise install `rico[pyplot]` as the old plotting functions return Matplotlib Pyplot Axes objects.

All extras:
```bash
pip install rico[complete]
```

## User guide

### Basic usage

**rico** provides both declarative and imperative style interfaces.

Declarative style:
```python
import pandas as pd
import rico

df = pd.DataFrame({
    "a": list("CCCDDDEEE"),
    "b": [2, 7, 4, 1, 2, 6, 8, 4, 7],
})
plot = df.plot.scatter(x="a", y="b")

doc = rico.Doc("Hello world!", df, plot, title="My doc")
```

Imperative style:
```python
doc = rico.Doc(title="My doc")
doc.append("Hello world!", df, plot)
```

Also imperative style:
```python
doc = rico.Doc(title="My doc")
doc.append("Hello world!")
doc.append(df)
doc.append(plot)
```

Mix-and-match:
```python
doc = rico.Doc("Hello world!", df, title="My doc")
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

Internally, `str(doc)` calls `doc.serialize()` with default parameter values. Call `doc.serialize()` to indent the HTML element tree visually:
```python
with open("doc.html", "w") as f:
    f.write(doc.serialize(indent=True))
```

Set custom whitespace for indentation using the `space` parameter:
```python
with open("doc.html", "w") as f:
    f.write(doc.serialize(indent=True, space="    "))
```

Remove unnecessary whitespace between tags by setting `strip` to `True`:
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
* Plots (Altair, Matplotlib Pyplot, Seaborn).
* Dataframes and other types with `_repr_html_` method.
* Text.

Use specific classes for plots and texts to change the default behavior:
```python
doc = rico.Doc(
    rico.Text("Hello world!", mono=True),  # The default value is False.
    df,
    rico.Plot(plot, format="png"),  # The default value is "svg".
    title="My doc",
)
```

Or:
```python
doc = rico.Doc(title="My doc")
doc.append_text("Hello world!", mono=True)
doc.append(df)
doc.append_plot(plot, format="png")
```

Some options can be set in the global configuration:
```python
with rico.config_context(text_mono=True, image_format="png"):
    doc = rico.Doc("Hello world!", df, plot, title="My doc")
```

Use specific classes and methods for other content types:
* Images: `Image` or `Doc.append_image`.
* Code: `Code` or `Doc.append_code`.
* Markdown: `Markdown` or `Doc.append_markdown`.
* HTML tag: `Tag` or `Doc.append_tag`.
* Raw HTML: `HTML` or `Doc.append_html`.

Example:
```python
doc = rico.Doc(
    rico.Markdown("## Dataframe"),
    df,
    rico.Tag("h2", "Plot"),  # An alternative way to add a header.
    plot,
    rico.HTML("<h2>Code</h2>"),  # Another way to add a header.
    rico.Code("print('Hello world!')"),
    title="My doc",
)
```

Or:
```python
doc = rico.Doc(title="My doc")
doc.append_markdown("## Dataframe")
doc.append(df)
doc.append_tag("h2", "Plot")
doc.append(plot)
doc.append_html("<h2>Code</h2>")
doc.append_code("print('Hello world!')")
```

Check the docstrings for additional parameters.

Serialize content to HTML using `str()` or `object.serialize()`:
```python
obj = rico.Tag("p", "Hello world!")

print(obj)
# <div><p>Hello world!</p></div>

print(obj.serialize(indent=True, space="    "))
# <div>
#     <p>Hello world!</p>
# </div>
```

### Bootstrap, HTML classes and document layout

By default, [Bootstrap](https://getbootstrap.com/) styles are included in the document. Change the default behavior using the `bootstrap` parameter:
```python
doc = rico.Doc("Hello world!", bootstrap="full")
```

The possible values are:
* `"css"` (default) -- include only CSS.
* `"full"` -- include both the CSS and JS.
* `"none"` -- don't include Bootstrap*.

*Keep in mind that **rico** relies on Bootstrap classes and styles. For example:
* The `mono` and `wrap` parameters of the `Text` class use Bootstrap's `font-monospace` and `font-monospace` classes.
* **rico**'s dataframe style definition uses Bootstrap variables.

Each content element is wrapped in a `<div>` container. Specify the element's container class using the `class_` parameter:
```python
print(rico.Tag("p", "Hello world!", class_="col"))
# <div class="col"><p>Hello world!</p></div>
```

All elements' containers in the document are also wrapped in a `<div>` container. Specify the document's container class using the `class_` parameter:
```python
doc = rico.Doc("Hello world!", class_="container-fluid")
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
doc = rico.Doc(
    rico.Tag("h1", "My doc"),
    rico.Tag("h2", "Description"),
    "This is an example of custom document layout using Bootstrap classes.",
    rico.Tag("h2", "Data"),
    rico.Div(
        rico.Obj("Dataframe", df, class_="col"),
        rico.Obj("Plot", plot, class_="col"),
        class_="row row-cols-auto",
    ),
    title="My doc",
)
```

Or:
```python
doc = rico.Doc(title="My doc")
doc.append_tag("h1", "My doc")
doc.append_tag("h2", "Description")
doc.append("This is an example of custom document layout using Bootstrap classes.")
doc.append_tag("h2", "Data")
div = rico.Div(class_="row row-cols-auto")
doc.append(div)
div.append("Dataframe", df, class_="col")
div.append("Plot", plot, class_="col")
```

Keep in mind that `obj.append(x, y)` works differently than
```python
obj.append(x)
obj.append(y)
```
The first one wraps both elements in a single `<div>` container. The second one creates a separate `<div>` container for each element.

`Obj(x, y, class_="z")` wraps both `x` and `y` elements in a single `<div>` container with `class` attribute set to `"z"`.

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
css = "https://cdn.jsdelivr.net/npm/bootstrap-icons@1/font/bootstrap-icons.css"
js = "https://cdn.jsdelivr.net/npm/jquery@3.7.0/dist/jquery.min.js"

doc = rico.Doc(
    "Hello world",
    extra_styles=(
        rico.Style("p {color: red;}"),
        rico.Style(src=css),
    ),
    extra_scripts=(
        rico.Script("alert('Hello World!');"),
        rico.Script(src=js),
    ),
)
```

By default, external styles and scripts are included as file links. This means that these files must be available when someone opens the document. Include the contents of these files in the document using the `inline` parameter:
```python
doc = rico.Doc(
    "Hello world",
    extra_styles=(
        rico.Style("p {color: red;}"),
        rico.Style(src=css, inline=True),
    ),
    extra_scripts=(
        rico.Script("alert('Hello World!');"),
        rico.Script(src=js, inline=True),
    ),
)
```

In the example above, the Bootstrap styles are still included as a link. Use the global options `inline_styles` and `inline_scripts` to include the contents of the style and script files in the document:
```python
with rico.config_context(inline_styles=True, inline_scripts=True):
    doc = rico.Doc(
        "Hello world",
        extra_styles=(
            rico.Style("p {color: red;}"),
            rico.Style(src=css),
        ),
        extra_scripts=(
            rico.Script("alert('Hello World!');"),
            rico.Script(src=js),
        ),
    )
```

### Global configuration

Use global configuration to:
* Get or set default parameter values.
* Get or set document properties.

The following globals options define the default parameter values:

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

The following globals options define document properties:
* `meta_charset` defines a document [charset](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta#charset) metadata.
* `meta_viewport` defines a document [viewport](https://developer.mozilla.org/en-US/docs/Web/HTML/Viewport_meta_tag) metadata.
* `bootstrap_css` defines a link to the Bootstrap CSS file.
* `bootstrap_js` defines a link to the Bootstrap JS file.
* `dataframe_style` defines a dataframe style.

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

## Use case and alternatives

Use **rico** if you want to create an HTML document from objects created in a Python script.

With **rico** you can avoid:
* Writing data to intermediate files or a database from a script.
* Loading data into a Jupyter notebook.
* Using [nbconvert](https://nbconvert.readthedocs.io/) or similar tools.

Alternatives:
* Use [Jupyter Notebook](https://jupyter.org/) for interactive computing.
* Use [nbconvert](https://nbconvert.readthedocs.io/) or [papermill](https://papermill.readthedocs.io/) if you're processing data and creating objects for a document in a Jupyter notebook.
* Use [Quarto](https://quarto.org/) if you prefer R Markdown style notebooks and a variety of output formats.
* Use [xml.etree.ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html), [lxml](https://lxml.de/), [Yattag](https://www.yattag.org/), or [Airium](https://gitlab.com/kamichal/airium) if you need low-level control.

More on the topic:
* [Pass pandas dataframe to notebook via nbconvert](https://github.com/jupyter/nbconvert/issues/1070).
* [Could Papermill pass an in-memory dataframe to a notebook?](https://github.com/nteract/papermill/issues/406)
* "I Don’t Like Notebooks": [video](https://www.youtube.com/watch?v=7jiPeIFXb6U), [slides](https://docs.google.com/presentation/d/1n2RlMdmv1p25Xy5thJUhkKGvjtV-dkAIsUXP-AL4ffI/edit#slide=id.g362da58057_0_1).
* [The First Notebook War](https://yihui.org/en/2018/09/notebook-war/).

## Roadmap

* Create docs with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).
* Support math with [KaTeX](https://katex.org/).
* Save Altair Charts in [Vega-Lite](https://vega.github.io/vega-lite/) format.
* Save SVG images in XML format.
* Support diagrams with [Mermaid.js](https://mermaid.js.org/).
* Support other plot types: [Plotly](https://plotly.com/python/), [Bokeh](https://bokeh.org/).
