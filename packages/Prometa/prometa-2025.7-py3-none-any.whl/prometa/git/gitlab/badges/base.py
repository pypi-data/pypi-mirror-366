#!/usr/bin/env python
"""
Base class for each badge manager.
"""

import logging

from jrai_common_mixins.registrable import Registrable

from .common import get_badge_url

LOGGER = logging.getLogger(__name__)


class BadgeManager(Registrable):
    """
    Badge manager base class.
    """

    def __init__(self, api):
        """
        Args:
            api:
                A GitLabApi instance.
        """
        self.api = api

    @property
    def project(self):
        """
        The Project instance.
        """
        return self.api.project

    @property
    def gitlab_project(self):
        """
        The python-gitlab Project instance.
        """
        return self.api.gitlab_project

    def is_enabled_in_conf(self, name):
        """
        Check if a given badge is enabled in the project's configuration file.

        Returns:
            True if the badge is enabled, else False
        """
        LOGGER.debug("Check if badge is enabled: %s", name)
        enabled = self.project.config.get("gitlab", "enabled_badges")
        is_enabled = enabled and name in enabled
        if is_enabled:
            LOGGER.debug("Managing badge: %s", name)
        return is_enabled

    def get_badge_by_name(self, name):
        """
        Get a badge by name.

        Args:
            name:
                The name of the badge.

        Returns:
            The Badge instance, or None of not badge of the given name was
            found.
        """
        for badge in self.gitlab_project.badges.list(get_all=True):
            if badge.name == name:
                return badge
        return None

    def create_badge(self, name, link_url, image_url):
        """
        Create a new badge.

        Args:
            name:
                The badge name.

            link_url:
                The badge link URL.

            image_url:
                The badge image URL.
        """
        LOGGER.info("Creating badge: %s", name)
        self.gitlab_project.badges.create(
            {"name": name, "link_url": link_url, "image_url": image_url}
        )

    @staticmethod
    def update_badge(badge, link_url, image_url):
        """
        Update a badge if necessary.

        Args:
            badge:
                A Badge instance.

            link_url:
                The badge link URL.

            image_url:
                The badge image URL.
        """
        if badge.link_url != link_url or badge.image_url != image_url:
            LOGGER.info("Updating badge: %s", badge.name)
            badge.link_url = link_url
            badge.image_url = image_url
            badge.save()

    @staticmethod
    def delete_badge(badge):
        """
        Delete a badge.

        Args:
            badge:
                A Badge instance.
        """
        if badge is not None:
            LOGGER.info("Deleting badge: %s", badge.name)
            badge.delete()

    @property
    def enabled(self):
        """
        True if the condition for enabling this badge is met, else False.
        """
        return False

    @property
    def urls(self):
        """
        The link and image URLs for the badge.
        """
        return "https://example.com", get_badge_url("badge", "example", "ff0000")

    def manage(self):
        """
        Manage the badge.
        """
        name = self.NAME
        LOGGER.info("Checking GitLab badge: %s", name)
        return
        if not self.is_enabled_in_conf(name):
            LOGGER.warning(
                'Found badge "%s" but it is not enabled in the configuration file.',
                name,
            )
            return
        link_url, image_url = self.urls
        badge = self.get_badge_by_name(name)
        if self.enabled:
            if badge is None:
                self.create_badge(name, link_url, image_url)
            else:
                self.update_badge(badge, link_url, image_url)
        else:
            if badge is not None:
                self.delete_badge(badge)
