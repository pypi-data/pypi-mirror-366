#!/usr/bin/env python
"""
Update the CI file.
"""

import logging
import re

import yaml

from ...file import update_content

LOGGER = logging.getLogger(__name__)


class GitLabCI:
    """
    Wrapper around the gitlab-ci file.
    """

    def __init__(self, project, path=".gitlab-ci.yml"):
        """
        Args:
            project:
                A Project instance.

            path:
                The path to the gitlab-ci file, relative to the repository root
                directory.
        """
        self.project = project
        self.path = project.git_repo.path / path
        self._data = None

    @property
    def data(self):
        """
        The CI configuration data.
        """
        if self._data is None:
            self._data = self.load()
        return self._data

    def load(self):
        """
        Load the file data.

        Returns:
            The loaded data, or an empty dict if the file does not exist.
        """
        try:
            with self.path.open("rb") as handle:
                return yaml.safe_load(handle)
        except FileNotFoundError:
            return {}

    def update_pages(self):
        """
        Update the pages job.
        """
        pages = self.data.get("pages")
        if not pages:
            return
        pages["artifacts"] = {"paths": ["public"]}
        pages["only"] = ["main"]
        pages["stage"] = "deploy"

    def add_register_pip_pkg(self):
        """
        Add a job to register a pip package.
        """
        key = "register_pip_pkg"
        if self.project.packages.get("python"):
            self.data[key] = {
                "image": "python:latest",
                "only": ["main"],
                "script": [
                    "pip install build twine",
                    "python -m build",
                    "TWINE_PASSWORD=${CI_JOB_TOKEN} TWINE_USERNAME=gitlab-ci-token "
                    "python -m twine upload --repository-url "
                    "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/pypi "
                    "dist/*",
                ],
                "stage": "deploy",
            }
        else:
            try:
                self.data.pop(key)
            except KeyError:
                pass

    def add_release_job(self):
        """
        Add a release job that triggers when Git tags are pushed.
        """
        key = "release_job"
        regex = self.project.config.get("gitlab", "release_tag_regex")
        if regex:
            self.data[key] = {
                "image": "registry.gitlab.com/gitlab-org/release-cli:latest",
                "release": {
                    "description": "Release $CI_COMMIT_TAG",
                    "tag_name": "$CI_COMMIT_TAG",
                },
                "rules": [{"if": f"$CI_COMMIT_TAG =~ /{regex}/"}],
                "script": [f'echo "Running {key}"'],
                "stage": "release",
            }
        else:
            self.data.pop(key, None)

    def add_stages(self):
        """
        Add the list of stages for all added jobs.
        """
        recognized_stages = [".pre", "build", "test", "release", "deploy", ".post"]
        stages = set()
        for key, value in self.data.items():
            if not isinstance(value, dict):
                continue
            stage = value.get("stage")
            if stage is None:
                LOGGER.error("No stage specified for job %s in %s", key, self.path)
                continue
            stages.add(stage)
        self.data["stages"] = [stage for stage in recognized_stages if stage in stages]

    def add_tags(self):
        """
        Add runner tags. This will deduplicate tags and also ensure that jobs
        using the same tags reference each other in the YAML output.
        """
        tag_map = self.project.config.get("gitlab", "ci_tags")
        if tag_map:
            tag_map = tuple(
                (re.compile(regex), tags) for regex, tags in tag_map.items()
            )
            previous_sets = []
            for name, data in self.data.items():
                if not isinstance(data, dict):
                    continue
                collected_tags = set()
                for regex, new_tags in tag_map:
                    if regex.search(name):
                        collected_tags.update(new_tags)
                collected_tags = sorted(collected_tags)
                # PyYAML seems to only emit references when nested items refer
                # to the same instance so ensure that identical lists do.
                for prev in previous_sets:
                    if collected_tags == prev:
                        collected_tags = prev
                        break
                else:
                    previous_sets.append(collected_tags)
                self.data[name]["tags"] = collected_tags

    def update(self):
        """
        Update the CI file by detecting which jobs should be added.
        """
        self.update_pages()
        self.add_register_pip_pkg()
        self.add_release_job()
        self.add_stages()
        self.add_tags()
        update_content(yaml.dump(self.data), self.path)
