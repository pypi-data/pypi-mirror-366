from __future__ import annotations

from typing import Any, Optional, TypeVar, Generic, Type

from .dependency import Dependency

T = TypeVar('T', bound=Dependency)


class DependencyBag:
    def __init__(self, dependencies: dict[str, Dependency]):
        self._dependencies = dependencies

    @staticmethod
    def empty() -> DependencyBag:
        return DependencyBag({})

    def add(self, dependency: Dependency) -> DependencyBag:
        return DependencyBag(
            {
                **self._dependencies,
                dependency.get_id(): dependency
            }
        )

    def find(
        self,
        dependency_type: Type,
        dependency_id: Optional[str],
        filter_values: dict[str, str]
    ) -> Optional[Dependency]:
        candidates = [
            dependency
            for dependency in self._dependencies.values()
            if issubclass(dependency.get_dependency_type(), dependency_type)
            and dependency.get_conditions().is_fulfilled_by(filter_values)
        ]
        if dependency_id is not None:
            candidates = [dependency for dependency in candidates if dependency.get_id() == dependency_id]
        if len(candidates) == 1:
            return next(iter(candidates))
        if len(candidates) > 1:
            raise Exception(f'More than 1 candidate for type {dependency_type}')

        return None
