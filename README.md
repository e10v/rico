# rico: rich content to HTML as easy as Doc(df, plot)

**rico** is a Python package for creating HTML documents from rich content: dataframes, plots, images, markdown etc. It provides a high-level, easy-to-use API with reasonable defaults as well as low-level access for better control.

[![CI](https://github.com/e10v/rico/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/e10v/rico/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/github/e10v/rico/coverage.svg?branch=main)](https://codecov.io/gh/e10v/rico)
[![License](https://img.shields.io/github/license/e10v/rico)](https://github.com/e10v/rico/blob/main/LICENSE)
[![Version](https://img.shields.io/pypi/v/rico.svg)](https://pypi.org/project/rico/)
[![Package Status](https://img.shields.io/pypi/status/rico.svg)](https://pypi.org/project/rico/)
[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/rico.svg)](https://pypi.org/project/rico/)

## Installation

Main functionality:
```bash
pip install rico
```

Main functionality don't have any dependencies except the standard Python packages. Optional additional dependencies are required for support of the following content types:
* Plots. Altair, Matplotlib Pyplot and Seaborn are currently supported.
* Markdown.

Install one or several extras if you are going to use plots or markdown in HTML documents.

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

Install `rico[seaborn]` extra only if you are using the [seaborn.objects](https://seaborn.pydata.org/tutorial/objects_interface.html) interface. Otherwise install `rico[pyplot]` since old plotting functions return Matplotlib Pyplot Axes objects.

All extras:
```bash
pip install rico[complete]
```

## User Guide

### Basic Usage

**rico** provides both declarative and imperative style API.

Declarative style:
```python
import pandas as pd
import rico


df = pd.DataFrame({
    'a': list('CCCDDDEEE'),
    'b': [2, 7, 4, 1, 2, 6, 8, 4, 7],
})
plot = df.plot.scatter(x='a', y='b')

doc = rico.Doc(df, plot)
```

Imperative style:
```python
doc = rico.Doc()
doc.append(df, plot)
```

Also imperative style:
```python
doc = rico.Doc()
doc.append(df)
doc.append(plot)
```

Mix-and-match:
```python
doc = rico.Doc(df)
doc.append(plot)
```

### Serialization

Serialize document to HTML using `str(doc)`:
```python
with open("doc.html", "w") as f:
    f.write(str(doc))
```

Implicit serialization:
```python
with open("doc.html", "w") as f:
    print(doc, file=f)
```

Internally `str(doc)` calls `doc.serialize()` with default parameters' values. Call `doc.serialize()` if you want to indent the HTML element tree visually:
```python
with open("doc.html", "w") as f:
    f.write(doc.serialize(indent=True))
```

You can also set the whitespace for indentation:
```python
with open("doc.html", "w") as f:
    f.write(doc.serialize(indent=True, space="    "))
```

You can strip unnecessary whitespace between tags:
```python
with open("doc.html", "w") as f:
    f.write(doc.serialize(strip=True))
```

Control the default behavoir of `str(doc)` and `doc.serialize()` using global options `indent_html`, `indent_space` and `strip_html`:
```python
with open("doc.html", "w") as f, rico.config_context(indent_html=True):
    f.write(str(doc))
```

The default options' values are:
* `indent_html = False`,
* `indent_space = "  "`,
* `strip_html = False`.

### Other Content Types

### HTML Classes, Layout Control and Bootstrap

### Styles and Scripts

Custom.
Inline.
Global config.

### Global Configuration

### Low-level Control

## Use Case and Alternatives

## Roadmap

* Create docs with [MkDocs](https://www.mkdocs.org/) and [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).
* Support math with [KaTeX](https://katex.org/).
* Save Altair Charts in [Vega-Lite](https://vega.github.io/vega-lite/) format.
* Save SVG images in XML format.
* Support diagrams with [Mermaid.js](https://mermaid.js.org/).
* Support other plot types: [Plotly](https://plotly.com/python/), [Bokeh](https://bokeh.org/).
