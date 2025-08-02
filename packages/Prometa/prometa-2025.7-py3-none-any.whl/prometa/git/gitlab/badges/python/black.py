#!/usr/bin/env python3
"""
Black code-style badge.
"""

from ..common import get_badge_url
from .python import PythonBadgeManager


class ToolBadgeManager(PythonBadgeManager):
    """
    Base class for tool badges that depend on tool sections in pyproject.toml.
    """


class BlackBadgeManager(PythonBadgeManager):
    """
    Black badge to indicate the the Python code is formatted with black.
    """

    NAME = "black"

    @property
    def enabled(self):
        """
        There is a tool.black section in the pyproject.toml file. The section may be empty.
        """
        if not super().enabled:
            return False
        conf = self.package.get_tool_configuration(self.NAME)
        return conf is not None

    @property
    def urls(self):
        link_url = "https://pypi.org/project/black/"
        image_url = get_badge_url("code style", "black", "000000")
        return link_url, image_url


BlackBadgeManager.register(BlackBadgeManager.NAME)
