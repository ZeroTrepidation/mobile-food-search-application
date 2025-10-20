from math import radians, sin, cos, sqrt, atan2
from typing import List

from backend.app.domain.models import FoodProvider, PermitStatus, Coordinate
from backend.app.domain.specification import Specification


class HasPermitStatus(Specification[FoodProvider]):
    def __init__(self, status: PermitStatus):
        self.status = status

    def is_satisfied_by(self, provider: FoodProvider) -> bool:
        return (
            provider.permit is not None
            and provider.permit.permitStatus == self.status
        )


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
    def __init__(self, point: Coordinate, limit: int = 5):
        self.reference_point: Coordinate = point
        self.limit = limit

    def is_satisfied_by(self, provider: FoodProvider) -> bool:
        return provider.coord is not None and (provider.coord.latitude != 0.0 and provider.coord.longitude != 0.0)

    def sort_by_distance(self, providers: List[FoodProvider]) -> List[FoodProvider]:
        def get_distance(provider: FoodProvider):
            return provider.coord.distance_to(self.reference_point)
        return sorted(providers, key=get_distance)[: self.limit]

    def order(self, items: List[FoodProvider]) -> List[FoodProvider]:
        # Delegate to existing distance-based sorter while enforcing limit
        return self.sort_by_distance(items)