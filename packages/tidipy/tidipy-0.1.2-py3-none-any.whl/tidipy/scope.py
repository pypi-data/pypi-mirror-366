from __future__ import annotations

from typing import Type, TypeVar, Optional

from .dependency_bag import DependencyBag
from .dependency import ConcreteDependency, Dependency
from .composer import Composer
from .resolver import Resolver
from .scope_context import ScopeContext
from .scopetype import ScopeType, RootType, Transient

T = TypeVar('T')


class Scope:
    def __init__(
        self,
        scope_id: str,
        scope_type: ScopeType,
        composers: set[Composer],
        parent: Optional[Scope] = None
    ):
        self._scope_id = scope_id
        self._parent = parent
        self._scope_type = scope_type
        self._dependency_bag: DependencyBag = DependencyBag.empty()
        self._context: ScopeContext = ScopeContext.empty()
        self._add_composers(composers)
        self._validate()

    def _validate(self):
        if self._scope_id == 'root' and self._scope_type != RootType():
            raise Exception('Only root scope can have root type')
        if self._scope_id != 'root' and self._scope_type == RootType():
            raise Exception('Only root scope can have root type')
        if self._scope_id == 'root' and self._parent is not None:
            raise Exception('Root scope can not have parent')
        if self._scope_type in self.get_ancestor_types():
            raise Exception('Ancestor already has a scope of this type')
        if self._scope_type == Transient():
            raise Exception('Scopes can not have type transient')

    def get_id(self) -> str:
        return self._scope_id

    def get_parent(self) -> Scope:
        return self._parent

    def get_type(self) -> ScopeType:
        return self._scope_type

    def __hash__(self) -> int:
        return hash(self._scope_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Scope):
            return False

        return self._scope_id == other.get_id()

    def get_ancestors(self) -> set[Scope]:
        if self._parent is None:
            return set()

        return {self._parent} | self._parent.get_ancestors()

    def get_ancestor_types(self) -> set[ScopeType]:
        return {scope.get_type() for scope in self.get_ancestors()}

    def _add_composers(self, composers: set[Composer]) -> None:
        for composer in composers:
            if composer.scope_type.supports_storing() and composer.scope_type != self._scope_type:
                continue

            self._dependency_bag = self._dependency_bag.add(composer)

    def add_context(self, values: dict[str, str]) -> None:
        self._context = self._context.add(values)

    def get_context(self) -> ScopeContext:
        return self._context

    def resolver(self) -> Resolver:
        return Resolver(self.get)

    def _get_from_dependency(self, dependency: Dependency, resolver: Resolver):
        if isinstance(dependency, ConcreteDependency):
            return dependency.value
        if isinstance(dependency, Composer):
            concrete = dependency.create(resolver)
            if dependency.scope_type.supports_storing():
                self._dependency_bag = self._dependency_bag.add(concrete)
            return concrete.value

        raise Exception

    def get(self, dependency_type: Type[T], dependency_id: Optional[str]) -> T:
        result = self._dependency_bag.find(dependency_type, dependency_id, self._context.values())
        if result is not None:
            return self._get_from_dependency(result, self.resolver())

        if self._parent is None:
            raise Exception(f'No candidate for type {dependency_type}')

        return self._parent.get(dependency_type, dependency_id)
