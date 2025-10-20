from asyncio import sleep
from datetime import datetime
from pathlib import Path
import json
from typing import List
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient


from backend.app.main import app, repository

# Load mock providers from backend/tests/fixtures
ROOT_DIR = Path(__file__).parents[1]
SFGOV_MOCK_DATA = Path(__file__).parent / "data" / "sfgov_mock_data.json"




@pytest.fixture(autouse=True)
def clear_repository():
    """Ensure repository starts clean before each test."""
    if hasattr(repository, "_providers"):
        repository._providers.clear()
    elif hasattr(repository, "providers"):
        repository.providers.clear()
    yield
    if hasattr(repository, "_providers"):
        repository._providers.clear()
    elif hasattr(repository, "providers"):
        repository.providers.clear()


@pytest.fixture(scope="session", autouse=True)
def disable_background_bus():
    """
    Prevent AsyncTaskBus from starting in tests by monkeypatching FastAPI lifespan.
    We'll mock out both the bus and the sfgov_datasource fetch_all call.
    """
    from backend.app import main

    async def mock_lifespan(app):
        data = json.loads(SFGOV_MOCK_DATA.read_text())
        main.sfgov_datasource.fetch_all = AsyncMock(return_value=data)

        # Skip starting AsyncTaskBus
        yield

    app.router.lifespan_context = mock_lifespan

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_search_by_name_basic():
    async with AsyncClient(app=app, base_url="http://test") as client:
        r = client.get("/api/v1/food-providers/name/Truly")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len([d for d in data if "Truly" in d.get("name", "")]) >= 2


async def test_search_by_name_with_status_filter():
    r = client.get("/api/v1/food-providers/name/Truly", params={"status": "Expired"})
    assert r.status_code == 200
    data = r.json()
    for d in data:
        if d.get("permit"):
            assert d["permit"].get("permitStatus") == "EXPIRED"


async def test_search_by_street_endpoint():
    r = client.get("/api/v1/food-providers/street/Mission")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1


async def test_closest_endpoint_limit_and_consistency():
    params = {"lng": "-122.39610066847152", "lat": "37.78798864899528", "limit": "1"}
    first = client.get("/api/v1/food-providers/closest", params=params)
    assert first.status_code == 200
    first_data = first.json()
    assert isinstance(first_data, list)
    assert len(first_data) == 1

    for _ in range(3):
        r = client.get("/api/v1/food-providers/closest", params=params)
        assert r.status_code == 200
        d = r.json()
        assert isinstance(d, list)
        assert len(d) == 1
        # Consistent first result
        assert d[0]["locationId"] == first_data[0]["locationId"]
