from datetime import datetime, timezone
from math import radians, sin, cos, sqrt, atan2
from typing import List

from backend.app.domain.models import FoodProvider, PermitStatus
from backend.app.domain.specification import Specification


class HasPermitStatus(Specification[FoodProvider]):
    def __init__(self, status: PermitStatus):
        self.status = status

    def is_satisfied_by(self, provider: FoodProvider) -> bool:
        return (
            provider.permit is not None
            and provider.permit.permitStatus == self.status
        )


class IsExpired(Specification[FoodProvider]):
    def is_satisfied_by(self, provider: FoodProvider) -> bool:
        if not provider.permit or not provider.permit.expirationDate:
            return False
        return provider.permit.expirationDate < datetime.now(timezone.utc)


class LikeName(Specification[FoodProvider]):
    def __init__(self, name: str):
        self.name = name

    def is_satisfied_by(self, provider: FoodProvider) -> bool:
        return self.name.lower() in provider.name.lower()


class LikeStreetName(Specification[FoodProvider]):
    def __init__(self, streetName: str):
        self.streetName = streetName

    def is_satisfied_by(self, provider: FoodProvider) -> bool:
        return self.streetName.lower() in provider.address.lower()


class ClosestToPointSpecification(Specification[FoodProvider]):
    def __init__(self, latitude: float, longitude: float, limit: int = 5):
        self.latitude = latitude
        self.longitude = longitude
        self.limit = limit

    def is_satisfied_by(self, provider: FoodProvider) -> bool:
        return provider.coord is not None

    def sort_by_distance(self, providers: List[FoodProvider]) -> List[FoodProvider]:
        def distance(provider: FoodProvider):
            return haversine_distance(
                self.latitude,
                self.longitude,
                provider.coord.latitude,
                provider.coord.longitude,
            )
        return sorted(providers, key=distance)[: self.limit]


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c