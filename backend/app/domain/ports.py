from abc import ABC, abstractmethod, abstractproperty
from datetime import datetime
from typing import List, Optional

from backend.app.domain.models import FoodProvider
from backend.app.domain.specification import Specification


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


class FoodProviderClient(ABC):
    """
    Port responsible for communicating with an external food provider API.
    Each implementation should know how to fetch and transform data into domain models.
    """

    @abstractmethod
    async def fetch_all(self) -> List[FoodProvider]:
        """
        Fetch and return all providers from the external API.
        """

    @abstractmethod
    async def periodic_task(self) -> None:
        """
        Execute the client's update process.
        This is the method Celery will call periodically.
        Should handle checking for, fetching and saving new data.
        """

    def get_interval(self) -> int:
        """
        Return the dynamic interval (in seconds) between periodic updates.
        Used by the scheduler (Celery beat) to determine frequency.
        Default: every hour.
        """
        return 3600



