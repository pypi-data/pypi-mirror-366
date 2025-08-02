#!/usr/bin/env python3
"""\
Print documentation of all recognized badges.\
"""

import logging
import textwrap

# Import it from badges instead of badges.base to ensure that all subclasses are
# registered.
from ..git.gitlab.badges import BadgeManager

LOGGER = logging.getLogger(__name__)


def document_badges():
    """
    Document all recognized badges in a table using their corresponding manager
    class docstrings.
    """
    badges = dict(BadgeManager.list_registered_with_classes())
    print("|Name|Description|Condition|")
    print("|:- |:- |:- |")
    for name, cls in sorted(badges.items()):
        desc = textwrap.dedent(cls.__doc__.strip("\n"))
        cond = textwrap.dedent(cls.enabled.__doc__.strip("\n"))
        print(f"|{name}|{desc}|{cond}|")
