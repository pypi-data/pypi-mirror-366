# Overview

Based on [Crafting Interpreters](https://timothya.com/pdfs/crafting-interpreters.pdf). Library provides lexers, parsers, and formatters for DAX and Power Query (M) languages. Designed to support code introspection and analysis, not execution. This enables developement of [ruff](https://github.com/astral-sh/ruff)-equivalent tools for DAX and Power Query. It also enables extracting metadata from DAX and Power Query code, such PQ source types (Excel, SQL, etc.) and DAX lineage dependencies.

For more information, see the [docs](https://douglassimonsen.github.io/pbi_parsers/)

# Installation

```shell
python -m pip install pbi_parsers
```

# Dev Instructions


## Set Up

```shell
python -m venv venv
venv\Scripts\activate
python -m pip install .
pre-commit install
```


# Running the Documentation Server

```shell
python -m pip install .[docs]
mkdocs serve -f docs/mkdocs.yml
```

## Deploy docs to Github Pages

```shell
mkdocs  gh-deploy --clean -f docs/mkdocs.yml
```

## Testing

```shell

pip install -e .
```

# Build Wheel

```shell
python -m build .
```