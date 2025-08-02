#!/usr/bin/env python3
"""
PyPI package.
"""

from ..common import get_badge_url
from .python import PythonBadgeManager


class PyPIBadgeManager(PythonBadgeManager):
    """
    A badge to show that the project is hosted on the Python Packaging Index (PyPI).
    """

    NAME = "PyPI"

    @property
    def enabled(self):
        """
        The package exists on PyPI.
        """
        return super().enabled and self.package.pypi_url

    @property
    def urls(self):
        link_url = self.package.pypi_url
        image_url = get_badge_url("PyPI", self.package.name, "006dad")
        return link_url, image_url


PyPIBadgeManager.register(PyPIBadgeManager.NAME)
