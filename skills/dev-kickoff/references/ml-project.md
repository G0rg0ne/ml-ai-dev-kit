# ML and data science project

Notebooks to explore, scripts to run the pipeline, and an installable package in a `src/` layout that holds every piece of logic both of them use. Data and trained models stay out of git.

## Tree

```
<project>/
├── data/
│   ├── raw/.gitkeep            # original data, never modified
│   ├── interim/.gitkeep        # intermediate transformations
│   ├── processed/.gitkeep      # final datasets for modeling
│   └── external/.gitkeep       # third-party data
├── notebooks/
│   └── 01-exploration.ipynb    # numbered: <NN>-<topic>.ipynb
├── scripts/
│   ├── train.py                # CLI: parse args, setup_logging(), call the package
│   └── evaluate.py
├── configs/
│   └── default.yaml            # paths, hyperparameters, seeds
├── models/.gitkeep             # trained artifacts
├── reports/figures/.gitkeep
├── src/<package>/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # settings from env and configs/*.yaml
│   │   └── logging_config.py
│   ├── data/__init__.py        # loading and cleaning
│   ├── features/__init__.py    # feature engineering
│   ├── models/__init__.py      # training and prediction
│   ├── evaluation/__init__.py  # metrics
│   └── visualization/__init__.py
├── tests/
│   ├── conftest.py
│   └── core/test_config.py
├── pyproject.toml
├── README.md
├── DEVELOPMENT.md
├── .env.example                # LOG_LEVEL, DATA_DIR, MODELS_DIR
└── .gitignore
```

## Notebooks

- Exploration only: a notebook imports from `<package>` and never defines a function another notebook or script needs.
- The first cell is `%load_ext autoreload` then `%autoreload 2`, so package edits apply without restarting the kernel.
- Notebooks are formatted by ruff like the rest of the code.

## .gitignore additions

```
data/**
!data/**/
!data/**/.gitkeep
models/*
!models/.gitkeep
.ipynb_checkpoints/
```

## pyproject.toml

```toml
[project]
name = "<project>"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["loguru", "pydantic-settings", "python-dotenv", "pyyaml", "numpy", "pandas", "scikit-learn", "matplotlib"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[dependency-groups]
dev = ["ruff", "pytest"]
notebook = ["jupyterlab", "ipykernel"]

[tool.uv]
default-groups = "all"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--import-mode=importlib"
```

Adjust the scientific dependencies to the project (for example torch instead of scikit-learn) when the request names them.

## Commands (uv)

```
uv sync
uv run jupyter lab
uv run python scripts/train.py --config configs/default.yaml
uv run pytest
```
