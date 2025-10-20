import asyncio
from datetime import datetime, timezone
from typing import List

import pytest

from backend.app.adapters.memory import InMemoryFoodProviderRepository
from backend.app.adapters.sfgov_client import SFGovFoodProviderDataClient
from backend.tests import helpers  # type: ignore
from backend.app.data_manager import DataManager


class TestClient(SFGovFoodProviderDataClient):
    def __init__(self):
        # Use a fixed timestamp so DataManager detects "new data" on first loop
        self._updated_at = datetime.now(timezone.utc)

    async def fetch_all(self) -> List[dict]:
        # We don't rely on raw rows in this test since we override map_results.
        return []

    def map_results(self, results: List[dict]):
        # Return a small, deterministic set of domain objects
        return helpers.general_mock_providers()

    def get_source_updated_at(self) -> datetime:
        return self._updated_at

    def get_interval(self) -> int:
        # Keep the polling loop responsive for tests
        return 1


@pytest.mark.asyncio
async def test_data_manager_loads():
    repo = InMemoryFoodProviderRepository()
    client = TestClient()
    dm = DataManager(repo, [client])

    # Start background polling
    dm.start()

    # Wait up to 2 seconds for the repository to be populated
    for _ in range(40):
        if repo.get_all():
            break
        await asyncio.sleep(0.05)

    await dm.stop()

    providers = repo.get_all()
    assert providers, "DataManager should populate the repository with providers"
    assert len(providers) == 5