from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from app.domain.models import FoodProvider
from app.domain.specification import Specification


class FoodProviderRepository(ABC):
    """Port responsible for persisting domain Models"""

    @abstractmethod
    def replace_all(self, providers: List[FoodProvider]):
        """
        Replace the entire stored collection with the provided providers. This could be replaced later by
        a more granular update method that potentially only updates outdated records. We could compare versions of data
        by hashing the rows when received and storing the hash alongside the domain objects
        """

    @abstractmethod
    def get_all(self) -> List[FoodProvider]:
        """
        Return all applicants.
        """

    @abstractmethod
    def get_by_spec(self, spec: Specification[FoodProvider]) -> List[FoodProvider]:
        """
        Return all applicants matching the given spec. Utilizes the specification pattern.
        """


class FoodProviderDataClient(ABC):
    """
    Port responsible for communicating with an external food provider API.
    Each implementation should define how to fetch raw data and map it to domain models.
    It should NOT perform scheduling or repository updates.
    """

    @abstractmethod
    async def fetch_all(self) -> List[dict]:
        """
        Fetch and return all providers from the external API as raw dict rows.
        """

    @abstractmethod
    def map_results(self, results: List[dict]) -> List[FoodProvider]:
        """
        Map raw result rows into domain FoodProvider objects. May use update_time for metadata.
        """

    @abstractmethod
    def get_source_updated_at(self) -> datetime:
        """
        Return the last-updated timestamp from the upstream data source (in UTC).
        Implementations should query source metadata and parse to datetime.
        """

    def get_interval(self) -> int:
        """
        Return the dynamic interval (in seconds) between metadata checks.
        Default: every hour.
        """
        return 3600
