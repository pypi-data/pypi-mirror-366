from __future__ import annotations


class ScopeContext:
    def __init__(self, values: dict[str, str]):
        self._values = values

    @staticmethod
    def empty() -> ScopeContext:
        return ScopeContext({})

    def add(self, values: dict[str, str]) -> ScopeContext:
        if not set(values.keys()).isdisjoint(set(self._values.keys())):
            raise Exception('Can only add values to scope context, not override values')

        return ScopeContext({**self._values, **values})

    def values(self) -> dict[str, str]:
        return self._values
