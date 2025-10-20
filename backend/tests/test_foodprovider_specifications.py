import pytest
from datetime import datetime, timedelta, timezone

from backend.app.adapters.memory import InMemoryFoodProviderRepository
from backend.app.domain.foodprovider_specifications import HasPermitStatus, LikeName, LikeStreetName, \
    ClosestToPointSpecification
from backend.app.domain.models import PermitStatus, Permit, FoodProvider, Coordinate
from backend.tests.helpers import make_provider, make_permit


class TestSpecifications:
    def test_has_permit_status(self):
        approved = make_provider("1", permit=make_permit(PermitStatus.APPROVED))
        expired = make_provider("2", permit=make_permit(PermitStatus.EXPIRED))

        spec = HasPermitStatus(PermitStatus.APPROVED)

        assert spec.is_satisfied_by(approved) is True
        assert spec.is_satisfied_by(expired) is False

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

    def test_closest_single_limit_multiple_calls(self):
        repo = InMemoryFoodProviderRepository()

        a = make_provider("A", name="A", latitude=1.0, longitude=2.0)
        b = make_provider("B", name="B", latitude=50.0, longitude=50.0)
        c = make_provider("C", name="C", latitude=-60.0, longitude=-60.0)
        d = make_provider("A", name="A", latitude=0.0, longitude=0.0)

        repo.replace_all([a, b, c])

        # Near A
        spec_a = ClosestToPointSpecification(Coordinate(latitude=0.1, longitude=0.1), limit=1)
        for _ in range(3):  # multiple calls should be consistent
            res = repo.get_by_spec(spec_a)
            assert len(res) == 1
            assert res[0].location_id == "A"

        # Near B
        spec_b = ClosestToPointSpecification(Coordinate(latitude=49.9, longitude=49.9), limit=1)
        for _ in range(3):
            res = repo.get_by_spec(spec_b)
            assert len(res) == 1
            assert res[0].location_id == "B"

        # Near C
        spec_c = ClosestToPointSpecification(Coordinate(latitude=-59.9, longitude=-59.9), limit=1)
        for _ in range(3):
            res = repo.get_by_spec(spec_c)
            assert len(res) == 1
            assert res[0].location_id == "C"

        # Near A because of D being 0.0 / 0.0
        spec_d = ClosestToPointSpecification(Coordinate(latitude=0.0, longitude=0.0), limit=1)
        res = repo.get_by_spec(spec_d)
        assert len(res) == 1
        assert res[0].location_id == "A"

        check_order = ClosestToPointSpecification(Coordinate(latitude=0.0, longitude=0.0), limit=4)
        res = repo.get_by_spec(check_order)
        assert len(res) == 3
        assert res[0].location_id == "A"
        assert res[1].location_id == "B"
        assert res[2].location_id == "C"