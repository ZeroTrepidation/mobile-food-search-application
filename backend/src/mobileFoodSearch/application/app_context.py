from __future__ import annotations

from typing import Optional

from backend.src.mobileFoodSearch.application.foodprovider_search_service import FoodProviderSearchService
from backend.src.mobileFoodSearch.application.soda_foodprovider_loader_service import SodaApplicantLoaderService
from backend.src.mobileFoodSearch.domain.foodprovider_repository import FoodProviderRepository
from backend.src.mobileFoodSearch.infrastructure.foodprovider_datasource import IFoodProviderDatasource


class ApplicationContext:
    """Application wiring and lifecycle management.

    Construct with the concrete implementations of the required interfaces.
    Provides start/stop methods to control background services.
    """

    def __init__(
        self,
        repository: FoodProviderRepository,
        datasource: IFoodProviderDatasource,
        interval_seconds: int = 3600,
    ) -> None:
        self.repository: FoodProviderRepository = repository
        self.datasource: IFoodProviderDatasource = datasource
        self.search_service = FoodProviderSearchService(self.repository)
        self._loader_service: Optional[SodaApplicantLoaderService] = SodaApplicantLoaderService(
            repository=self.repository,
            datasource=self.datasource,
            interval_seconds=interval_seconds,
        )

    def start(self) -> None:
        if self._loader_service:
            self._loader_service.start()

    async def stop(self) -> None:
        if self._loader_service:
            await self._loader_service.stop()
            self._loader_service = None
