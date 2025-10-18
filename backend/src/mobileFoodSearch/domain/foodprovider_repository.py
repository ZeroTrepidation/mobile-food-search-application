from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.mobileFoodSearch.domain.foodprovider import FoodProvider
from backend.src.mobileFoodSearch.specification import Specification


class FoodProviderRepository(ABC):
    """Defines how applicant data is accessed and stored.

    Note: The repository is intentionally not responsible for fetching or refreshing
    data from external sources. Use an external loader/service to obtain data and
    push it into the repository via replace_all().
    """

    @abstractmethod
    def get_all(self) -> List[FoodProvider]:
        """Return all applicants."""
        pass

    @abstractmethod
    def get_by_spec(self, spec: Specification[FoodProvider]) -> List[FoodProvider]:
        """Return all applicants matching the given spec."""
        pass

    @abstractmethod
    def bulk_update(self, applicants: List[FoodProvider]) -> None:
        """Replace the entire stored collection with the provided applicants. This could be replaced later by
        a more granular update method that potentially only updates outdated records. We could compare versions of data
        by hashing the rows when received and storing the hash alongside the domain objects"""
        pass