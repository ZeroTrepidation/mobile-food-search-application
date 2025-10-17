from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domains.mobileFoodSearch.domain.location import Location
from backend.src.domains.mobileFoodSearch.domain.permit import Permit


class Applicant(object):
    permit: Permit
    location: Location
    name: str
    foodItems: str

def __init__(self, permit: Permit, location: Location):
        self.permit = permit


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
    def save(self, applicant: Applicant) -> None:
        """Create or update an applicant."""
        pass

    @abstractmethod
    def delete(self, applicant_id: str) -> None:
        """Remove an applicant."""
        pass