#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
from typing import cast

logger = logging.getLogger(__name__)


class Requires:
    """Create a tuple with package dependencies."""

    __slots__ = (
        'data', 'name', 'options', 'option_for_resolve_off'
    )

    def __init__(self, data: dict[str, dict[str, str]], name: str, options: dict[str, bool]) -> None:
        logger.debug("Initializing Requires module for package: '%s', options: %s", name, options)
        self.data = data
        self.name = name

        self.option_for_resolve_off: bool = options.get('option_resolve_off', False)
        logger.debug("Requires module initialized. Resolve off option: %s", self.option_for_resolve_off)

    def resolve(self) -> tuple[str, ...]:
        """Resolve the dependencies.

        Return package dependencies in the right order.
        """
        logger.info("Attempting to resolve dependencies for package: '%s'", self.name)
        dependencies: tuple[str, ...] = ()

        if not self.option_for_resolve_off:
            # Ensure 'requires' key exists and is a list, cast for mypy.
            raw_requires: list[str] = cast(list[str], self.data.get(self.name, {}).get('requires', []))
            requires: list[str] = self.remove_deps(raw_requires)
            logger.debug("Initial direct dependencies for '%s' after removing non-existent: %s", self.name, requires)

            # Iterate through direct requirements to find their sub-requirements
            # This loop structure might lead to duplicates if not careful,
            # but dict.fromkeys() at the end handles uniqueness.
            for require in list(requires):  # Iterate over a copy to allow modification of 'requires'.
                # Ensure 'requires' key exists for sub-dependencies
                sub_raw_requires: list[str] = cast(list[str], self.data.get(require, {}).get('requires', []))
                sub_requires: list[str] = self.remove_deps(sub_raw_requires)
                logger.debug("Sub-dependencies for '%s': %s", require, sub_requires)

                for sub in sub_requires:
                    if sub not in requires:  # Avoid adding immediate duplicates in this loop iteration.
                        requires.append(sub)
                        logger.debug("Added sub-dependency '%s' from '%s' to main list.", sub, require)

            requires.reverse()  # Reverse the list to get the correct order (leaf dependencies first).
            dependencies = tuple(dict.fromkeys(requires))  # Remove duplicates while preserving order.
            logger.info("Dependencies resolved for '%s': %s", self.name, dependencies)
        else:
            logger.info("Dependency resolution is off. Returning empty tuple.")

        return dependencies

    def remove_deps(self, requires: list[str]) -> list[str]:
        """Remove requirements that not in the repository.

        Args:
            requires (list[str]): list of requirements.

        Returns:
            list[str]: list of package names that exist in the repository data.
        """
        logger.debug("Filtering requirements: %s (checking against %d packages in data)", requires, len(self.data))
        filtered_requires = [req for req in requires if req in self.data]
        if len(filtered_requires) < len(requires):
            removed_count = len(requires) - len(filtered_requires)
            logger.info("Removed %d requirements that are not in repository data.", removed_count)
            logger.debug("Original requirements: %s, Filtered requirements: %s", requires, filtered_requires)
        else:
            logger.debug("All requirements found in repository data. No filtering applied.")
        return filtered_requires
