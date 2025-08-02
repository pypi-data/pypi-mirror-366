#!/usr/bin/env python3
"""
Pipeline status badge.
"""

from .base import BadgeManager


class PipelineStatusBadgeManager(BadgeManager):
    """
    A badge to show the current GitLab pipeline status.
    """

    NAME = "Pipeline Status"

    @property
    def enabled(self):
        """
        The GitLab CI configuration file exists.
        """
        return self.project.git_host.gitlab_ci.exists()

    @property
    def urls(self):
        host, _namespace, _name = self.project.git_repo.parsed_origin
        protocol = "https"
        link_url = (
            f"{protocol}://{host}/%{{project_path}}/-/commits/%{{default_branch}}"
        )
        image_url = f"{protocol}://{host}/%{{project_path}}/badges/%{{default_branch}}/pipeline.svg"
        return link_url, image_url


PipelineStatusBadgeManager.register(PipelineStatusBadgeManager.NAME)
