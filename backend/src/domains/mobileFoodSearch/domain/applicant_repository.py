from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domains.mobileFoodSearch.domain.applicant import Applicant


class ApplicantRepository(ABC):
    """Defines how applicant data is accessed and stored.

    Note: The repository is intentionally not responsible for fetching or refreshing
    data from external sources. Use an external loader/service to obtain data and
    push it into the repository via replace_all().
    """

    @abstractmethod
    def get_all(self) -> List[Applicant]:
        """Return all applicants."""
        pass

    @abstractmethod
    def get_by_id(self, applicant_id: str) -> Optional[Applicant]:
        """Return a single applicant by ID."""
        pass

    @abstractmethod
    def replace_all(self, applicants: List[Applicant]) -> None:
        """Replace the entire stored collection with the provided applicants."""
        pass