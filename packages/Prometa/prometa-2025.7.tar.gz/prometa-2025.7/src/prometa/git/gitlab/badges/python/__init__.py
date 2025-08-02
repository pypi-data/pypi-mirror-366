#!/usr/bin/env python
"""Package stub."""

import importlib

# Import modules to ensure that subclasses are registered.
for pkg in ("black", "hatch", "isort", "pypi", "pypi_downloads"):
    importlib.import_module(f".{pkg}", __name__)
