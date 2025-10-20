from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from backend.app.domain.models import FoodProvider
from backend.src.mobileFoodSearch.specification import Specification


class FoodProviderRepository(ABC):
    """Port responsible for persisting domain Models"""

    @abstractmethod
    def save_all(self, providers: List[FoodProvider]):
        """"
        Method for bulk saving of providers. For now the only persistence mechanism since we are bulk saving
        providers provided by the external sfgov api
        """

    @abstractmethod
    def replace_all(self, providers: List[FoodProvider], task_id: str):
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
    def get_providers(self) -> List[FoodProvider]:
        """
        Fetch and return all providers from the external API.
        """

    @abstractmethod
    def get_last_update_time(self) -> datetime:
        """
        Return the last known time the data the client is responsible for was updated.
        """

    @abstractmethod
    def periodic_update(self) -> None:
        """
        Execute the client's update process.
        This is the method Celery will call periodically.
        Should handle fetching and saving new data.
        """

    def get_interval(self) -> int:
        """
        Return the dynamic interval (in seconds) between periodic updates.
        Used by the scheduler (Celery beat) to determine frequency.
        Default: every hour.
        """
        return 3600

    def get_task_name(self) -> str:
        """Unique Celery task name for this client."""
        return f"tasks.{self.__class__.__name__.lower()}_update"

    def get_next_run_eta(self) -> Optional[datetime]:
        """
        Optional: Override to delay first run (useful for staggering many clients).
        Example: return datetime.utcnow() + timedelta(minutes=5)
        """
        return None




