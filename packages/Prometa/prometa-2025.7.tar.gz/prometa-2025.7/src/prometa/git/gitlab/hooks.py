#!/usr/bin/env python
"""
Manage project hooks on GitLab.
"""

import logging

LOGGER = logging.getLogger(__name__)


class GitLabHooksMixin:
    """
    Mixin to handle hooks in GitLabApi class.
    """

    def manage_hooks(self):
        """
        Manage hooks if configured to do so.
        """
        if not self.project.config.get("gitlab", "manage_hooks", default=False):
            return
        self.manage_swh_hook()

    def manage_swh_hook(self):
        """
        Manage the SWH webhooks.

        Args:
            gproj:
                The python-gitlab Project instance.
        """
        # Reset to releases_events when SoftwareHeritage updates their API.
        #  events_key = 'releases_events'
        events_key = "tag_push_events"
        url = "https://archive.softwareheritage.org/api/1/origin/save/webhook/gitlab/"

        swh_hook = None
        add = self.project.codemeta_json_path.exists()
        gproj = self.gitlab_project

        for hook in gproj.hooks.list(iterator=True):
            if hook.attributes["url"] == url:
                if add and swh_hook is None:
                    swh_hook = hook
                else:
                    LOGGER.info("Deleting SWH hook for %s.", gproj.name)
                    hook.delete()

        if add and swh_hook is None:
            LOGGER.info("Creating SWH webhook for %s", gproj.name)
            swh_hook = gproj.hooks.create({"url": url, events_key: True})

        if swh_hook:
            changed = False
            for key, value in swh_hook.attributes.items():
                if key.endswith("_events"):
                    expected_value = key == events_key
                    if value != expected_value:
                        changed = True
                        setattr(swh_hook, key, expected_value)
            if changed:
                LOGGER.info("Updating SWH hook for %s.", gproj.name)
                swh_hook.save()
