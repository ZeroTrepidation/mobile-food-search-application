from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Coordinate(BaseModel):
    longitude: float
    latitude: float

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