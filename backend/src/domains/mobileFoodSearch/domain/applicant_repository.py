from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domains.mobileFoodSearch.domain.applicant import Applicant


class ApplicantRepository(ABC):
    """Defines how applicant data is accessed."""

    @abstractmethod
    def get_all(self) -> List[Applicant]:
        """Return all applicants."""
        pass

    @abstractmethod
    def get_by_id(self, applicant_id: str) -> Optional[Applicant]:
        """Return a single applicant by ID."""
        pass


    @abstractmethod
    async def refresh(self) -> None:
        """Reload data from source."""
        pass