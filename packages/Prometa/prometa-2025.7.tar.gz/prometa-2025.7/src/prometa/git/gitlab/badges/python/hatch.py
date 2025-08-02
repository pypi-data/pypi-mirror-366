#!/usr/bin/env python3
"""
Hatch and Hatchling build system.
"""

import urllib.parse

from ..common import get_badge_url
from .python import PythonBadgeManager


class HatchBadgeManager(PythonBadgeManager):
    """
    A badge to show that the project uses the Hatch build system.
    """

    NAME = "Hatch"

    @property
    def enabled(self):
        """
        The package is configured to use Hatch via pyproject.toml.
        """
        backend = self.package.pyproject_toml_data.get("build-system", {}).get(
            "build-backend"
        )
        return backend == "hatchling.build"

    @property
    def urls(self):
        link_url = "https://github.com/pypa/hatch"
        label = urllib.parse.unquote("%F0%9F%A5%9A")
        image_url = get_badge_url(label, "Hatch", "4051b5")
        return link_url, image_url


HatchBadgeManager.register(HatchBadgeManager.NAME)
