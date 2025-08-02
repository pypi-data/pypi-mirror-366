#!/usr/bin/env python3
"""
PyPI downloads.
"""

from .python import PythonBadgeManager


class PyPIDownloadsBadgeManager(PythonBadgeManager):
    """
    A badge to show the number of downloads from the Python Packaging Index (PyPI)
    """

    NAME = "PyPI Downloads"

    @property
    def enabled(self):
        """
        The package exists on PyPI.
        """
        return super().enabled and self.package.pypi_url

    @property
    def urls(self):
        pypi_name = self.package.name
        link_url = f"https://pepy.tech/projects/{pypi_name}"
        image_url = f"https://static.pepy.tech/badge/{pypi_name}"
        return link_url, image_url


PyPIDownloadsBadgeManager.register(PyPIDownloadsBadgeManager.NAME)
