from datetime import datetime
from enum import Enum
from math import radians, atan2, sin, sqrt, cos
from typing import Optional

from pydantic import BaseModel, field_validator, ValidationError, BeforeValidator, model_validator
from typing_extensions import Annotated


def parse_float(value):
    try:
        return float(value)
    except ValueError:
        raise ValidationError('Value not parseable as float')


def parse_int(value):
    try:
        return int(value)
    except ValueError:
        raise ValidationError('Value not parseable as int')


Longitude = Annotated[float, BeforeValidator(parse_float)]
Latitude = Annotated[float, BeforeValidator(parse_float)]


class Coordinate(BaseModel):
    longitude: Longitude
    latitude: Latitude

    def distance_to(self, other: 'Coordinate') -> float:
        def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            R = 6371.0  # Earth radius in km
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            return R * c

        return haversine_distance(other.latitude, other.longitude, self.latitude, self.longitude)

    @field_validator('longitude', mode='after')
    @classmethod
    def validate_longitude(cls, v):
        if v < -180 or v > 180:
            raise ValueError('Coordinate must be between -180 and 180')
        return v

    @field_validator('latitude', mode='after')
    @classmethod
    def validate_latitude(cls, v):
        if v < -90 or v > 90:
            raise ValueError('Coordinate must be between -90 and 90')
        return v

    # I got sick of dealing with locations in the middle of nowhere
    @model_validator(mode='after')
    def validate_coordinate(self):
        if self.longitude is None or self.latitude is None or (self.longitude == 0.0 and self.latitude == 0.0):
            raise ValueError('Coordinate cannot be 0.0 / 0.0')
        return self


class PermitStatus(Enum):
    APPROVED = "APPROVED"
    EXPIRED = "EXPIRED"
    REQUESTED = "REQUESTED"
    SUSPEND = "SUSPEND"
    ISSUED = "ISSUED"


class Permit(BaseModel):
    permitStatus: PermitStatus
    permitID: str
    approvalDate: Optional[datetime]
    recievedDate: Optional[datetime]
    expirationDate: Optional[datetime]


class FoodProvider(BaseModel):
    location_id: str
    name: str
    food_items: str
    permit: Permit
    coord: Coordinate
    location_description: Optional[str]
    blocklot: Optional[str]
    block: Optional[str]
    lot: Optional[str]
    cnn: Optional[int]
    address: Optional[str]
