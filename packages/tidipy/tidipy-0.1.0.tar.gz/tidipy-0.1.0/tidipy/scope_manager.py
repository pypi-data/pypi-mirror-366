from typing import Optional

from .composer import Composer
from .scope import Scope
from .scopetype import ScopeType, RootType
from .resolver import Resolver


class ScopeManager:
    def __init__(self):
        self._composers = []
        self._scopes: dict[str, Scope] = {}
        self.ensure_scope(scope_id='root', scope_type=RootType())

    def add_composers(self, composers: list[Composer]) -> None:
        self._composers = self._composers + composers
        for scope in self._scopes.values():
            scope.add_composers(composers)

    def get_resolver(self, scope_id: str) -> Resolver:
        return self._scopes[scope_id].resolver()

    def ensure_scope(self, scope_id: str, scope_type: ScopeType, parent_id: Optional[str] = None) -> None:
        if scope_id not in self._scopes:
            self._create_scope(scope_id, scope_type, parent_id)
            return

        existing_scope = self._scopes[scope_id]
        if existing_scope.get_type() != scope_type:
            raise Exception
        if existing_scope.get_parent() is None and parent_id is not None:
            raise Exception
        if existing_scope.get_parent() is not None and existing_scope.get_parent().get_id() != parent_id:
            raise Exception

    def _create_scope(self, scope_id: str, scope_type: ScopeType, parent_id: Optional[str]) -> None:
        parent = self._scopes[parent_id] if parent_id is not None else None
        scope = Scope(
            scope_id=scope_id,
            parent=parent,
            scope_type=scope_type
        )
        scope.add_composers(self._composers)
        if parent is not None:
            scope.add_context(parent.get_context().values())

        if scope_id in self._scopes:
            raise Exception('Scope already exists')

        self._scopes[scope_id] = scope

    def add_context(self, scope_id: str, values: dict[str, str]):
        self._scopes[scope_id].add_context(values)

    def clear_scope(self, scope_id: str):
        deleted_scope = self._scopes.pop(scope_id)
        child_ids = {scope.get_id() for scope in self._scopes.values() if scope.get_parent() == deleted_scope}
        for child_id in child_ids:
            self.clear_scope(child_id)

        if scope_id == 'root':
            self.ensure_scope(scope_id='root', scope_type=RootType())

    def reset(self) -> None:
        self.__init__()


scope_manager = ScopeManager()
