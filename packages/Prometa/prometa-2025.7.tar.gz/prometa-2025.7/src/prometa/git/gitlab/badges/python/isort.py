#!/usr/bin/env python3
"""
isort import sorting badge.
"""

from ..common import get_badge_url
from .python import PythonBadgeManager


class IsortBadgeManager(PythonBadgeManager):
    """
    A badge to indicate the Python imports are sorted with isort.
    """

    NAME = "isort"

    @property
    def enabled(self):
        """
        There is a tool.isort section in the pyproject.toml file. The section may be empty.
        """
        if not super().enabled:
            return False
        conf = self.package.get_tool_configuration(self.NAME)
        return conf is not None

    @property
    def urls(self):
        link_url = "https://pypi.org/project/isort/"
        image_url = get_badge_url("imports", "isort", "1674b1", labelColor="ef8336")
        return link_url, image_url


IsortBadgeManager.register(IsortBadgeManager.NAME)
