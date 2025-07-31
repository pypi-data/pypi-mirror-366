#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
from typing import Any, cast

from slpkg.repositories import Repositories
from slpkg.utilities import Utilities

logger = logging.getLogger(__name__)


class Required:
    """Create a tuple of dependencies with the right order to install."""

    __slots__ = ('data', 'name', 'flags', 'repos', 'utils',
                 'full_requires', 'repository_packages',
                 'option_for_resolve_off')

    def __init__(self, data: dict[str, dict[str, str]], name: str, options: dict[str, bool]) -> None:
        logger.debug("Initializing Required module for package: '%s', with options: %s", name, options)
        self.data = data
        self.name = name
        self.utils = Utilities()
        self.repos = Repositories()

        # Reads about how requires are listed, full listed is True
        # and normal listed is false.
        self.full_requires: bool = False
        if self.repos.repos_information.is_file():
            try:
                info = cast(dict[str, dict[str, Any]], self.utils.read_json_file(self.repos.repos_information))
                repo_name: str = data[name]['repo']
                if info.get(repo_name):
                    self.full_requires = info[repo_name].get('full_requires', False)
                    logger.debug("Full requires status for repo '%s': %s", repo_name, self.full_requires)
                else:
                    logger.debug("Repository info not found for '%s'. full_requires remains False.", repo_name)
            except KeyError as e:
                logger.warning("KeyError when accessing repo info for package '%s': %s. full_requires remains False.", name, e)
            except Exception as e:  # pylint: disable=[W0718]
                logger.error("Unexpected error reading repo information for '%s': %s", name, e, exc_info=True)
        else:
            logger.debug("Repository information file not found: %s. full_requires remains False.", self.repos.repos_information)

        self.option_for_resolve_off: bool = options.get('option_resolve_off', False)
        logger.debug("Option 'resolve_off' set to: %s", self.option_for_resolve_off)

    def resolve(self) -> tuple[str, ...]:
        """Resolve the dependencies.

        Return package dependencies in the right order.
        """
        logger.info("Resolving dependencies for package: '%s'. Resolve off option: %s", self.name, self.option_for_resolve_off)
        dependencies: tuple[str, ...] = ()
        if not self.option_for_resolve_off:
            requires: list[str] = self.remove_deps(cast(list[str], self.data[self.name]['requires']))
            logger.debug("Initial dependencies for '%s' after removing non-existent: %s", self.name, requires)

            # Resolve dependencies for some special repos.
            if not self.full_requires:
                logger.debug("Full requires is False. Performing transitive dependency resolution.")
                for require in requires:
                    sub_requires: list[str] = self.remove_deps(cast(list[str], self.data[require]['requires']))
                    for sub in sub_requires:
                        if sub not in requires:
                            requires.append(sub)
                            logger.debug("Added transitive dependency '%s' for '%s'.", sub, require)
            else:
                logger.debug("Full requires is True. Skipping transitive dependency resolution.")

            requires.reverse()
            dependencies = tuple(dict.fromkeys(requires))  # Remove duplicates while preserving order.
            logger.info("Resolved dependencies for '%s': %s", self.name, dependencies)
        else:
            logger.info("Dependency resolution is off. Returning empty dependencies tuple.")

        return dependencies

    def remove_deps(self, requires: list[str]) -> list[str]:
        """Remove requirements that not in the repository.

        Args:
            requires (list[str]): List of requires.

        Returns:
            list: List of packages name.
        """
        initial_len = len(requires)
        filtered_requires = [req for req in requires if req in self.data]
        if len(filtered_requires) < initial_len:
            removed_deps = set(requires) - set(filtered_requires)
            logger.debug("Removed %d dependencies not found in repository data: %s", len(removed_deps), list(removed_deps))
        else:
            logger.debug("No dependencies removed (all found in repository data).")
        return filtered_requires
