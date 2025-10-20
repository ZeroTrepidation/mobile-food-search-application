from __future__ import annotations

from typing import List, Dict

from backend.app.domain.models import FoodProvider, PermitStatus
from backend.app.domain.ports import FoodProviderRepository
from backend.app.domain.specification import Specification


class InMemoryFoodProviderRepository(FoodProviderRepository):
    """
    In-memory implementation of the FoodProviderRepository port. For the sake of simplicity, this is currently just
    a list of FoodProvider objects. This is technically not a reliable way to store data if we are intending on
    implementing multiple clients and should be replaced by a more robust data store in the future.
    """

    def __init__(self):
        self._store: Dict[str, FoodProvider] = {}

    def replace_all(self, providers: List[FoodProvider]):
        new_store: dict[str, FoodProvider] = {}
        for p in providers:
            if p is None:
                continue
            key = None
            if hasattr(p, 'location_id'):
                key = getattr(p, 'location_id')
            if key:
                new_store[str(key)] = p
        self._store = new_store

    def get_all(self) -> List[FoodProvider]:
        return list(self._store.values())

    def get_by_spec(self, spec: Specification[FoodProvider]) -> List[FoodProvider]:
        filtered = [p for p in self._store.values() if spec.is_satisfied_by(p)]

        if hasattr(spec, "sort_by_distance"):
            return spec.sort_by_distance(filtered)

        return filtered
