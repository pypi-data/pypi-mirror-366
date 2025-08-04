from __future__ import annotations

import builtins
import inspect
from dataclasses import dataclass
from typing import TypeVar, Callable, Type, get_type_hints, Optional

from .conditions import Conditions, Condition
from .dependency import Dependency, ConcreteDependency
from .resolver import Resolver
from .scopetype import ScopeType, parse_scope_type

T = TypeVar('T')

FactoryMethod = Callable[[Resolver], T]


@dataclass(frozen=True)
class Composer(Dependency):
    id: str
    scope_type: ScopeType
    conditions: Conditions
    factory: Callable[[Resolver], T]
    dependency_type: Type

    def get_id(self) -> str:
        return self.id

    def __hash__(self) -> int:
        return hash(self.id)

    def get_dependency_type(self) -> Type:
        return self.dependency_type

    def get_conditions(self) -> Conditions:
        return self.conditions

    def create(self, resolver: Resolver) -> ConcreteDependency:
        return ConcreteDependency(
            id=self.id,
            conditions=self.conditions,
            value=self.factory(resolver)
        )


def composer(
    factory: Optional[Callable] = None,
    *,
    id: Optional[str] = None,
    scope_type: str = 'root',
    **kwargs: str | set[str]
):
    parsed_scope_type = parse_scope_type(scope_type)

    def inner(func: Callable):
        has_parameter = len(inspect.signature(func).parameters) > 0
        return Composer(
            id=str(builtins.id(func)) if id is None else id,
            scope_type=parsed_scope_type,
            conditions=Conditions(
                conditions={
                    Condition(
                        key=key,
                        one_of_values=frozenset(value) if isinstance(value, set) else frozenset({value})
                    )
                    for key, value in kwargs.items()
                }
            ),
            factory=func if has_parameter else lambda resolve: func(),
            dependency_type=get_type_hints(func).get('return', object)
        )

    if factory is not None:
        return inner(factory)

    return inner
