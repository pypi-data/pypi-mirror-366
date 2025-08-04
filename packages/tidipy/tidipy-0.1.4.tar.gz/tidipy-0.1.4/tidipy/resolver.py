from __future__ import annotations

from typing import TypeVar, Type, Callable, Any, Optional

T = TypeVar('T')


class Resolver:
    def __init__(self, method: Callable[[Type, Optional[str]], Any]):
        self._method = method

    def __call__(self, dependency_type: Type[T], id=None) -> T:
        return self._method(dependency_type, id)

