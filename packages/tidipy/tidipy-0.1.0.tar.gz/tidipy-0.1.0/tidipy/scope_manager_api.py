from typing import Optional

from .resolver import Resolver
from .scope_manager import scope_manager
from .scopetype import parse_scope_type


def ensure_scope(scope_id: str = 'root', scope_type: str = 'root', parent_id: Optional[str] = None) -> None:
    if parent_id is None and scope_id != 'root':
        parent_id = 'root'
    return scope_manager.ensure_scope(scope_id, parse_scope_type(scope_type), parent_id)


def add_context(scope_id: str = 'root', **kwargs) -> None:
    scope_manager.add_context(scope_id, kwargs)


def get_resolver(scope_id: str = 'root') -> Resolver:
    return scope_manager.get_resolver(scope_id)


def clear_scope(scope_id: str) -> None:
    scope_manager.clear_scope(scope_id=scope_id)


def reset() -> None:
    scope_manager.reset()
