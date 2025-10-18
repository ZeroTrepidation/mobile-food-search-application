from typing import List

from backend.src.mobileFoodSearch.domain.foodprovider_repository import FoodProviderRepository
from backend.src.mobileFoodSearch.domain.foodprovider import FoodProvider
from backend.src.mobileFoodSearch.specification import Specification


class FoodproviderInMemoryRepository(FoodProviderRepository):
    """Stores applicants in memory (non-persistent).

    Note: This repository does not fetch or refresh data from external sources.
    Use an external loader/service to obtain data and push it via replace_all().
    """

    def __init__(self):
        self._store: dict[str, FoodProvider] = {}

    def get_all(self) -> List[FoodProvider]:
        return list(self._store.values())

    def get_by_spec(self, spec: Specification[FoodProvider]) -> List[FoodProvider]:
        """Return all FoodProviders satisfying a spec, respecting sorting if defined."""
        # Filter by satisfaction first
        filtered = [p for p in self._store.values() if spec.is_satisfied_by(p)]

        # If the spec supports sorting (like our ClosestToPointSpecification), apply it
        if hasattr(spec, "sort_by_distance"):
            return spec.sort_by_distance(filtered)

        return filtered
    def bulk_update(self, applicants: List[FoodProvider]) -> None:
        new_store: dict[str, FoodProvider] = {}
        for a in applicants:
            if a is None:
                continue
            key = None
            # Support objects with attributes
            if hasattr(a, 'locationId'):
                key = getattr(a, 'locationId')
            if key:
                new_store[str(key)] = a
        self._store = new_store