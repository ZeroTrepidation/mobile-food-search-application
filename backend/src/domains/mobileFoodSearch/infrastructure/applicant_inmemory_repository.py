from typing import List, Optional

from backend.src.domains.mobileFoodSearch.domain.applicant_repository import ApplicantRepository
from backend.src.domains.mobileFoodSearch.domain.applicant import Applicant


class ApplicantInMemoryRepository(ApplicantRepository):
    """Stores applicants in memory (non-persistent).

    Note: This repository does not fetch or refresh data from external sources.
    Use an external loader/service to obtain data and push it via replace_all().
    """

    def __init__(self):
        self._store: dict[str, Applicant] = {}

    def get_all(self) -> List[Applicant]:
        return list(self._store.values())

    def get_by_id(self, applicant_id: str) -> Optional[Applicant]:
        return self._store.get(applicant_id)

    def replace_all(self, applicants: List[Applicant]) -> None:
        new_store: dict[str, Applicant] = {}
        for a in applicants:
            if a is None:
                continue
            key = None
            # Support objects with attributes
            if hasattr(a, 'locationId'):
                key = getattr(a, 'locationId')
            elif hasattr(a, 'id'):
                key = getattr(a, 'id')
            # Support dict rows from SODA
            elif isinstance(a, dict):
                key = a.get('locationid') or a.get('locationId') or a.get('id')
            if key:
                new_store[str(key)] = a
        self._store = new_store