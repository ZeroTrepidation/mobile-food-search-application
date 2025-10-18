from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, List

from backend.src.mobileFoodSearch.domain.permit import Permit, PermitStatus
from backend.src.mobileFoodSearch.specification import Specification
from math import radians, sin, cos, sqrt, atan2


class FoodProvider:
    def __init__(
            self,
            location_id: str,
            name: str,
            food_items: str = "",
            permit: Optional[Permit] = None,
            longitude: Optional[float] = None,
            latitude: Optional[float] = None,
            location_description: Optional[str] = None,
            blocklot: Optional[str] = None,
            block: Optional[str] = None,
            lot: Optional[str] = None,
            cnn: Optional[int] = None,
            address: Optional[str] = None,
    ):
        self.locationId = str(location_id) if location_id is not None else ""
        self.name = name or ""
        self.foodItems = food_items or ""
        self.permit = permit
        self.longitude = longitude
        self.latitude = latitude
        self.locationDescription = location_description
        self.blocklot = blocklot
        self.block = block
        self.lot = lot
        self.cnn = cnn
        self.address = address

    def to_dict(self) -> dict:
        return {
            "locationId": self.locationId,
            "name": self.name,
            "foodItems": self.foodItems,
            "permit": self.permit.to_dict() if self.permit else None,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "locationDescription": self.locationDescription,
            "blocklot": self.blocklot,
            "block": self.block,
            "lot": self.lot,
            "cnn": self.cnn,
            "address": self.address,
        }


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
    """Returns the closest N FoodProviders to a given (lat, lon) point."""

    def __init__(self, latitude: float, longitude: float, limit: int = 5):
        self.latitude = latitude
        self.longitude = longitude
        self.limit = limit

    def is_satisfied_by(self, provider: FoodProvider) -> bool:
        """All providers with valid coordinates are 'satisfied' — ranking happens later."""
        return provider.latitude is not None and provider.longitude is not None

    def sort_by_distance(self, providers: List[FoodProvider]) -> List[FoodProvider]:
        """Return providers sorted by distance ascending."""
        def distance(provider: FoodProvider):
            return haversine_distance(
                self.latitude,
                self.longitude,
                provider.latitude,
                provider.longitude,
            )
        return sorted(providers, key=distance)[: self.limit]


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in kilometers between two lat/lon pairs."""
    R = 6371.0  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c