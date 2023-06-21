# rico: rich content to HTML as easy as Doc(df, plot)

**rico** is a Python package for creating HTML documents from rich content: dataframes, plots, images, markdown etc. It provides a high-level, easy-to-use API with reasonable defaults as well as low-level access for better control.

[![CI](https://github.com/e10v/rico/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/e10v/rico/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/github/e10v/rico/coverage.svg?branch=main)](https://codecov.io/gh/e10v/rico)
[![License](https://img.shields.io/github/license/e10v/rico)](https://github.com/e10v/rico/blob/main/LICENSE)
[![Version](https://img.shields.io/pypi/v/rico.svg)](https://pypi.org/project/rico/)
[![Package Status](https://img.shields.io/pypi/status/rico.svg)](https://pypi.org/project/rico/)
[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/rico.svg)](https://pypi.org/project/rico/)

## Installation

Core features:
```
pip install rico
```

Core features don't have any dependencies except the standard Python packages. Optional additional dependencies are required for support of the following content types:
* Plots. Altair, Matplotlib Pyplot and Seaborn are currently supported.
* Markdown.

Install one or several extras if you are going to use plots or markdown in HTML documents.

Altair Charts:
```
pip install rico[altair]
```

Markdown:
```
pip install rico[markdown]
```

Matplotlib Pyplot:
```
pip install rico[pyplot]
```

Seaborn:
```
pip install rico[seaborn]
```

You need `rico[seaborn]` extra only if you are using the [seaborn.objects](https://seaborn.pydata.org/tutorial/objects_interface.html) interface. Otherwise you need `rico[pyplot]` since old plotting functions return Matplotlib Pyplot Axes objects.

All extras:
```
pip install rico[complete]
```

## Quick Start

## Use case and alternatives

## Internals

## Roadmap

* Create docs with MkDocs.
* Support diagrams with Mermaid.js.
* Save SVG images in XML format.
* Save Altair Charts in Vega-Lite format.
* Support math with KaTeX.
