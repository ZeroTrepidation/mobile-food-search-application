import pytest
from fastapi.testclient import TestClient

from app.adapters.memory import InMemoryFoodProviderRepository
from app.dependencies import get_repository
from app.main import app
from tests.helpers import general_mock_providers

mock_repository = InMemoryFoodProviderRepository()


@pytest.fixture(autouse=True)
def setup_reposiotry_data():
    mock_providers = general_mock_providers()
    mock_repository.replace_all(mock_providers)


def override_repository():
    return mock_repository


client = TestClient(app)

app.dependency_overrides[get_repository] = override_repository


def test_search_by_name_basic():
    r = client.get("/api/v1/food-providers/name/Truly")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len([d for d in data if "Truly" in d.get("name", "")]) >= 2


def test_search_by_name_with_status_filter():
    r = client.get("/api/v1/food-providers/name/Truly", params={"status": "Expired"})
    assert r.status_code == 200
    data = r.json()
    for d in data:
        if d.get("permit"):
            assert d["permit"].get("permitStatus") == "EXPIRED"


def test_search_by_street_endpoint():
    r = client.get("/api/v1/food-providers/street/Mission")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_closest_endpoint_limit_without_status():
    params = {"lng": "-122.39610066847152", "lat": "37.78798864899528"}
    first = client.get("/api/v1/food-providers/closest", params=params)
    assert first.status_code == 200
    data = first.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_closest_endpoint_limit_with_status():
    params = {"lng": "-122.39610066847152", "lat": "37.78798864899528", "status": "EXPIRED"}
    first = client.get("/api/v1/food-providers/closest", params=params)
    assert first.status_code == 200
    assert len(first.json()) == 3


def test_closest_endpoint_limit_with_status_and_limit():
    params = {"lng": "-122.39610066847152", "lat": "37.78798864899528", "status": "APPROVED", "limit": "1"}
    first = client.get("/api/v1/food-providers/closest", params=params)
    assert first.status_code == 200
    data = first.json()
    assert isinstance(data, list)
    assert len(data) == 1

    params = {"lng": "-122.39610066847152", "lat": "37.78798864899528", "status": "EXPIRED", "limit": "2"}
    first = client.get("/api/v1/food-providers/closest", params=params)
    assert first.status_code == 200
    data = first.json()
    assert isinstance(data, list)
    assert len(data) == 2
