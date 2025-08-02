#!/usr/bin/env python3
"""
Base class for Python badges.
"""

from ..base import BadgeManager


class PythonBadgeManager(BadgeManager):
    """
    Base class for Python badges.
    """

    @property
    def package(self):
        """
        The Python Package instance, or None if the project does not contain a
        Python package.
        """
        return self.project.packages.get("python")

    @property
    def enabled(self):
        """
        The project includes a Python package.
        """
        return bool(self.package)
