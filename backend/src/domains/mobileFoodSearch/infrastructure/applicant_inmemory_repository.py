from typing import List, Optional

from backend.src.domains.mobileFoodSearch.domain.applicant import ApplicantRepository, Applicant


class ApplicantInMemoryRepository(ApplicantRepository):
    """Stores applicants in memory (non-persistent)."""

    def __init__(self):
        self._store: dict[str, Applicant] = {}

    def get_all(self) -> List[Applicant]:
        return list(self._store.values())

    def get_by_id(self, applicant_id: str) -> Optional[Applicant]:
        return self._store.get(applicant_id)

    async def refresh(self) -> None:
        """Reload the dataset from Socrata and rebuild the in-memory cache."""
        print(f"🔄 Refreshing applicants from Socrata dataset: {self._dataset_id}")
        records = self._soda_client.fetch_data(self._dataset_id, limit=self._limit)

        new_store: dict[str, Applicant] = {}
        for row in records:
            applicant = Applicant(
                id=row.get("locationid", ""),
                name=row.get("Applicant", ""),
                facility_type=row.get("FacilityType", ""),
                address=row.get("Address", ""),
                status=row.get("Status", "")
            )
            new_store[applicant.id] = applicant

        self._store = new_store
        print(f"✅ Repository refreshed with {len(new_store)} applicants.")