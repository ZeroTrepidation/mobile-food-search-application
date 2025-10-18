from typing import Optional, Any

from backend.src.mobileFoodSearch.domain.foodprovider_repository import FoodProviderRepository


class FoodProviderSearchService:
    def __init__(self, repository: FoodProviderRepository):
        self._repo = repository

    def get_applicant_by_id(self, applicant_id: str) -> Optional[Any]:
        if not applicant_id:
            return None
        return self._repo.get_by_id(str(applicant_id))

