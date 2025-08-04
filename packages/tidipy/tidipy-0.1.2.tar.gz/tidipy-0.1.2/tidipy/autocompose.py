import builtins
import inspect
from typing import Type, Optional

from tidipy import Resolver
from tidipy.composer import Composer
from tidipy.conditions import Condition, Conditions
from tidipy.scope_manager import scope_manager
from tidipy.scopetype import parse_scope_type


class AutoFactory:
    def __init__(self, dependency_type: Type):
        self._dependency_type = dependency_type

    def __eq__(self, other) -> bool:
        if not isinstance(other, AutoFactory):
            return False

        return self._dependency_type == other._dependency_type

    def __call__(self, resolver: Resolver):
        constructor = self._dependency_type.__init__
        sig = inspect.signature(constructor)

        params = list(sig.parameters.values())[1:]

        args = []
        for param in params:
            if param.annotation is inspect.Parameter.empty:
                raise TypeError(f"Cannot resolve untyped parameter: {param.name}")
            dependency = resolver(param.annotation)
            args.append(dependency)

        return self._dependency_type(*args)


def auto_compose(
    dependency_type: Type,
    *,
    id: Optional[str] = None,
    scope_type: str = 'root',
    **kwargs
):
    if not inspect.isclass(dependency_type):
        raise ValueError
    factory = AutoFactory(dependency_type)
    composer = Composer(
            id=str(builtins.id(dependency_type)) if id is None else id,
            scope_type=parse_scope_type(scope_type),
            conditions=Conditions(
                conditions={
                    Condition(
                        key=key,
                        one_of_values=frozenset(value) if isinstance(value, set) else frozenset({value})
                    )
                    for key, value in kwargs.items()
                }
            ),
            dependency_type=dependency_type,
            factory=factory
        )
    scope_manager.add_composers({composer})
