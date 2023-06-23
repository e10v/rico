# rico: rich content to HTML as easy as Doc(df, plot)

**rico** is a Python package for creating HTML documents from rich content: dataframes, plots, images, markdown etc. It provides a high-level, easy-to-use API with reasonable defaults, as well as low-level access for better control.

[![CI](https://github.com/e10v/rico/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/e10v/rico/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/github/e10v/rico/coverage.svg?branch=main)](https://codecov.io/gh/e10v/rico)
[![License](https://img.shields.io/github/license/e10v/rico)](https://github.com/e10v/rico/blob/main/LICENSE)
[![Version](https://img.shields.io/pypi/v/rico.svg)](https://pypi.org/project/rico/)
[![Package Status](https://img.shields.io/pypi/status/rico.svg)](https://pypi.org/project/rico/)
[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/rico.svg)](https://pypi.org/project/rico/)

## Installation

The core functionality:
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

doc = rico.Doc("Hello world!", df, plot)
```

Imperative style:
```python
doc = rico.Doc()
doc.append("Hello world!", df, plot)
```

Also imperative style:
```python
doc = rico.Doc()
doc.append("Hello world!")
doc.append(df)
doc.append(plot)
```

Mix-and-match:
```python
doc = rico.Doc("Hello world!", df)
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

Control the default behavior of `str(doc)` and `doc.serialize()` using the global options `indent_html`, `indent_space` and `strip_html`:
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
* All other types are processes as text.

Use specific classes for plots and texts to change the default behavior:
```python
doc = rico.Doc(
    rico.Text("Hello world!", mono=True),  # The default value is False.
    df,
    rico.Plot(plot, format="png"),  # The default value is "svg".
)
```

Or:
```python
doc = rico.Doc()
doc.append_text("Hello world!", mono=True)
doc.append(df)
doc.append_plot(plot, format="png")
```

Some options can be set in the global configuration:
```python
with rico.config_context(text_mono=True, image_format="png"):
    doc = rico.Doc("Hello world!", df, plot)
```

Use specific classes and methods for other content types:
* Images: `Image` and `Doc.append_image`.
* Code: `Code` and `Doc.append_code`.
* Markdown: `Markdown` and `Doc.append_markdown`.
* HTML tag: `Tag` and `Doc.append_tag`.
* Raw HTML: `HTML` and `Doc.append_html`.

Example:
```python
doc = rico.Doc(
    rico.Markdown("## Dataframe"),
    df,
    rico.Tag("h2", "Plot"),  # An alternative way to add a header.
    plot,
    rico.HTML("<h2>Code</h2>"),  # Another way to add a header.
    rico.Code("print('Hello world!')"),
)
```

Or:
```python
doc = rico.Doc()
doc.append_markdown("## Dataframe")
doc.append(df)
doc.append_tag("h2", "Plot")
doc.append(plot)
doc.append_html("<h2>Code</h2>")
doc.append_code("print('Hello world!')")
```

Check the docstrings for additional parameters.

### HTML classes, layout control and Bootstrap

### Styles and scripts

Custom.
Inline.
Global config.

### Global configuration

### Low-level control

## Use case and alternatives

## Roadmap

* Create docs with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).
* Support math with [KaTeX](https://katex.org/).
* Save Altair Charts in [Vega-Lite](https://vega.github.io/vega-lite/) format.
* Save SVG images in XML format.
* Support diagrams with [Mermaid.js](https://mermaid.js.org/).
* Support other plot types: [Plotly](https://plotly.com/python/), [Bokeh](https://bokeh.org/).
