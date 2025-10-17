from typing import Optional, Any

from backend.src.domains.mobileFoodSearch.domain.applicant_repository import ApplicantRepository


class ApplicantService:
    """Application service encapsulating business logic for Applicants.

    For now it simply delegates to the repository, but it is the right place
    to add validation, transformations, or cross-cutting concerns later.
    """

    def __init__(self, repository: ApplicantRepository):
        self._repo = repository

    def get_applicant_by_id(self, applicant_id: str) -> Optional[Any]:
        if not applicant_id:
            return None
        return self._repo.get_by_id(str(applicant_id))
