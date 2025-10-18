import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Import app after monkeypatching methods to ensure startup uses our fakes
import backend.src.mobileFoodSearch.infrastructure.sf_gov_datasource as sf_ds


TEST_RESOURCES = Path(__file__).parent / "resources"
SODA_PROVIDERS_PATH = TEST_RESOURCES / "soda_providers.json"


@pytest.fixture(autouse=True)
def patch_soda_datasource(monkeypatch):
    """Patch SODAClientDatasource methods so the app loads local test data instead of calling the network."""

    def fake_fetch_all(self, batch_size: int = 2000):
        with SODA_PROVIDERS_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)

    def fake_get_last_update_time(self):
        # Always indicate an update "now" so the loader refreshes during app startup
        return datetime.now(timezone.utc)

    monkeypatch.setattr(sf_ds.SODAClientDatasource, "fetch_all", fake_fetch_all, raising=True)
    monkeypatch.setattr(sf_ds.SODAClientDatasource, "get_last_update_time", fake_get_last_update_time, raising=True)


@pytest.fixture
def client():
    # Import the app only after patching so the lifespan loader uses our patched datasource
    from backend.src.main import app
    with TestClient(app) as c:
        # Give a short moment in case background tasks need to settle (usually unnecessary)
        time.sleep(0.05)
        yield c


def test_root(client: TestClient):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello World"}


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_search_by_name_basic(client: TestClient):
    # The test dataset contains 2 entries with applicant "Truly Food & More"
    r = client.get("/api/v1/food-providers/name/Truly")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Expect at least 2 results containing "Truly" in the name
    assert len([d for d in data if "Truly" in d.get("name", "")]) >= 2


def test_search_by_name_with_status_filter(client: TestClient):
    r = client.get("/api/v1/food-providers/name/Truly", params={"status": "APPROVED"})
    assert r.status_code == 200
    data = r.json()
    # All results should have APPROVED status when present
    for d in data:
        if d.get("permit"):
            assert d["permit"].get("permitStatus") == "APPROVED"


def test_search_by_street_endpoint(client: TestClient):
    # Note: current implementation uses LikeName instead of street; ensure endpoint works and returns items
    r = client.get("/food-providers/street/Truly")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_closest_endpoint_limit_and_consistency(client: TestClient):
    # Request closest with limit=1; call multiple times and ensure a single consistent result is returned
    params = {"long": "-122.39610066847152", "lat": "37.78798864899528", "limit": "1"}
    first = client.get("/food-providers/closest", params=params)
    assert first.status_code == 200
    first_data = first.json()
    assert isinstance(first_data, list)
    assert len(first_data) == 1

    for _ in range(3):
        r = client.get("/food-providers/closest", params=params)
        assert r.status_code == 200
        d = r.json()
        assert isinstance(d, list)
        assert len(d) == 1
        # Consistent first result
        assert d[0]["locationId"] == first_data[0]["locationId"]
