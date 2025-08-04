from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, Any

from .conditions import Conditions


class Dependency(ABC):
    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def get_dependency_type(self) -> Type:
        pass

    @abstractmethod
    def get_conditions(self) -> Conditions:
        pass


@dataclass(frozen=True)
class ConcreteDependency(Dependency):
    id: str
    value: Any
    conditions: Conditions

    def get_id(self) -> str:
        return self.id

    def get_dependency_type(self) -> Type:
        return type(self.value)

    def get_conditions(self) -> Conditions:
        return self.conditions
