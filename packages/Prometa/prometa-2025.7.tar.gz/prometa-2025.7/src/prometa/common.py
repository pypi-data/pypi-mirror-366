#!/usr/bin/env python3
"""
Common constants and functions.
"""

import logging

NAME = "prometa"
LOGGER = logging.getLogger(__name__)


def choose(items, include_none=False):
    """
    Prompt the user to choose an item from an iterable of items.

    Args:
        items:
            The iterable of items.

        include_none:
            If True, allow the user to choose None even if it is not in the
            list.

    Returns:
        The chosen item.
    """
    items = sorted(items)
    if include_none and None not in items:
        items.append(None)
    if not items:
        LOGGER.warning("No items to choose.")
        return None
    n_items = len(items)
    if n_items == 1:
        return items[0]
    while True:
        print("Choose one of the following:")
        for i, item in enumerate(items, start=1):
            print(f"{i:d} {item}")
        choice = input(f"Enter an integer in the range 1-{n_items:d} and press enter. ")
        try:
            choice = int(choice)
        except ValueError:
            LOGGER.error('"%s" is not a valid integer.', choice)
            continue
        if choice < 1 or choice > n_items:
            LOGGER.error("Invalid choice.")
            continue
        return items[choice - 1]
