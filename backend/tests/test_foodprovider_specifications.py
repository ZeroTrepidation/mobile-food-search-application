import pytest
from datetime import datetime, timedelta, timezone

from backend.src.mobileFoodSearch.domain.permit import Permit, PermitStatus
from backend.src.mobileFoodSearch.domain.foodprovider import (
    FoodProvider,
    HasPermitStatus,
    IsExpired,
    LikeName,
    LikeStreetName,
    ClosestToPointSpecification,
    haversine_distance,
)
from backend.src.mobileFoodSearch.infrastructure.foodprovider_inmemory_repository import (
    FoodproviderInMemoryRepository,
)


def make_permit(status: PermitStatus | str = PermitStatus.APPROVED,
                exp_delta_days: int | None = None) -> Permit:
    now = datetime.now(timezone.utc)
    expiration = None
    if exp_delta_days is not None:
        expiration = now + timedelta(days=exp_delta_days)
    return Permit(status, permitID="P-1", approvalDate=now, recievedDate=now, expirationDate=expiration)


def make_provider(
    location_id: str,
    name: str = "Test Truck",
    food_items: str = "tacos, soda",
    permit: Permit | None = None,
    longitude: float | None = None,
    latitude: float | None = None,
    address: str = "1 Main St",
):
    return FoodProvider(
        location_id=location_id,
        name=name,
        food_items=food_items,
        permit=permit,
        longitude=longitude,
        latitude=latitude,
        location_description=None,
        blocklot=None,
        block=None,
        lot=None,
        cnn=None,
        address=address,
    )


class TestSpecifications:
    def test_has_permit_status(self):
        approved = make_provider("1", permit=make_permit(PermitStatus.APPROVED))
        expired = make_provider("2", permit=make_permit(PermitStatus.EXPIRED))
        no_permit = make_provider("3", permit=None)

        spec = HasPermitStatus(PermitStatus.APPROVED)

        assert spec.is_satisfied_by(approved) is True
        assert spec.is_satisfied_by(expired) is False
        assert spec.is_satisfied_by(no_permit) is False

    def test_is_expired(self):
        past = make_provider("1", permit=make_permit(PermitStatus.APPROVED, exp_delta_days=-1))
        future = make_provider("2", permit=make_permit(PermitStatus.APPROVED, exp_delta_days=7))
        no_date = make_provider("3", permit=make_permit(PermitStatus.APPROVED, exp_delta_days=None))
        no_permit = make_provider("4", permit=None)

        spec = IsExpired()
        assert spec.is_satisfied_by(past) is True
        assert spec.is_satisfied_by(future) is False
        # Per implementation, missing expiration date returns False, and missing permit returns False
        assert spec.is_satisfied_by(no_date) is False
        assert spec.is_satisfied_by(no_permit) is False

    def test_like_name_case_insensitive(self):
        p = make_provider("1", name="ABC Pizza Truck")
        assert LikeName("pizza").is_satisfied_by(p) is True
        assert LikeName("PiZ").is_satisfied_by(p) is True
        assert LikeName("burger").is_satisfied_by(p) is False

    def test_like_street_name_case_insensitive(self):
        p = make_provider("1", address="500 Market Street")
        assert LikeStreetName("market").is_satisfied_by(p) is True
        assert LikeStreetName("MARK").is_satisfied_by(p) is True
        assert LikeStreetName("Mission").is_satisfied_by(p) is False

    def test_haversine_distance_basic(self):
        # Roughly 111.195 km per degree of longitude at the equator
        d = haversine_distance(0.0, 0.0, 0.0, 1.0)
        assert 110.0 < d < 112.5
        # Symmetry and zero
        assert haversine_distance(10.0, -5.0, 10.0, -5.0) == pytest.approx(0.0, abs=1e-9)
        assert haversine_distance(37.0, -122.0, 38.0, -122.0) == haversine_distance(38.0, -122.0, 37.0, -122.0)

    def test_closest_single_limit_multiple_calls(self):
        repo = FoodproviderInMemoryRepository()

        a = make_provider("A", name="A", latitude=0.0, longitude=0.0)
        b = make_provider("B", name="B", latitude=50.0, longitude=50.0)
        c = make_provider("C", name="C", latitude=-60.0, longitude=-60.0)
        d_no_coords = make_provider("D", name="D", latitude=None, longitude=None)

        repo.bulk_update([a, b, c, d_no_coords])

        # Near A
        spec_a = ClosestToPointSpecification(latitude=0.1, longitude=0.1, limit=1)
        for _ in range(3):  # multiple calls should be consistent
            res = repo.get_by_spec(spec_a)
            assert len(res) == 1
            assert res[0].locationId == "A"

        # Near B
        spec_b = ClosestToPointSpecification(latitude=49.9, longitude=49.9, limit=1)
        for _ in range(3):
            res = repo.get_by_spec(spec_b)
            assert len(res) == 1
            assert res[0].locationId == "B"

        # Near C
        spec_c = ClosestToPointSpecification(latitude=-59.9, longitude=-59.9, limit=1)
        for _ in range(3):
            res = repo.get_by_spec(spec_c)
            assert len(res) == 1
            assert res[0].locationId == "C"

        # Ensure provider without coordinates is ignored
        res_all = repo.get_by_spec(ClosestToPointSpecification(latitude=0.0, longitude=0.0, limit=10))
        ids = [p.locationId for p in res_all]
        assert "D" not in ids
