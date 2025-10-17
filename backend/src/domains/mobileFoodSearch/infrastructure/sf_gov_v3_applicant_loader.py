from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from sodapy import Socrata

from backend.src.domains.mobileFoodSearch.application.food_data_loader import IFoodDataLoader
from backend.src.domains.mobileFoodSearch.domain.applicant import Applicant


@dataclass
class SFGovApplicant:
    locationid: Optional[int]
    applicant: Optional[str]
    facility_type: Optional[str]
    cnn: Optional[int]
    location_description: Optional[str]
    address: Optional[str]
    blocklot: Optional[str]
    block: Optional[str]
    lot: Optional[str]
    permit: Optional[str]
    status: Optional[str]
    food_items: Optional[str]
    x: Optional[float]
    y: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    schedule: Optional[str]
    dayshours: Optional[str]
    noi_sent: Optional[str]
    approved: Optional[str]
    received: Optional[str]
    prior_permit: Optional[str]
    expiration_date: Optional[str]
    location: Optional[str]

    @staticmethod
    def from_dict(data: dict) -> "SFGovApplicant":
        """Create an SFGovApplicant instance from a dictionary returned by the API."""
        def to_int(val):
            try:
                return int(val) if val is not None else None
            except (TypeError, ValueError):
                return None

        def to_float(val):
            try:
                return float(val) if val is not None else None
            except (TypeError, ValueError):
                return None

        return SFGovApplicant(
            locationid=to_int(data.get("locationid")),
            applicant=data.get("applicant"),
            facility_type=data.get("facilitytype"),
            cnn=to_int(data.get("cnn")),
            location_description=data.get("locationdescription"),
            address=data.get("address"),
            blocklot=data.get("blocklot"),
            block=data.get("block"),
            lot=data.get("lot"),
            permit=data.get("permit"),
            status=data.get("status"),
            food_items=data.get("fooditems"),
            x=to_float(data.get("x")),
            y=to_float(data.get("y")),
            latitude=to_float(data.get("latitude")),
            longitude=to_float(data.get("longitude")),
            schedule=data.get("schedule"),
            dayshours=data.get("dayshours"),
            noi_sent=data.get("noisent"),
            approved=data.get("approved"),
            received=data.get("received"),
            prior_permit=data.get("priorpermit"),
            expiration_date=data.get("expirationdate"),
            location=data.get("location"),
        )


class SFGovLoader(IFoodDataLoader):
    DATASET_URL = "https://data.sfgov.org/resource/rqzj-sfat.json"
    USER_AGENT = "github.io/ZeroTrepidation/mobile-food-search/1.0"
    DATASET_ID = "rqzj-sfat"

    def __init__(self, url: Optional[str] = None, user_agent: str = USER_AGENT):
        self._url = url or self.DATASET_URL
        self._user_agent = user_agent


    def load_applicants(self) -> List[Applicant]:
        # Fetch raw rows from the API
        rows = self._fetch()

        # Map rows to SFGovApplicant and verify instances
        sf_rows: List[SFGovApplicant] = []
        for row in rows:
            mapped = SFGovApplicant.from_dict(row)
            if not isinstance(mapped, SFGovApplicant):
                # Runtime guard to ensure mapping yields the expected type
                raise TypeError(
                    f"Mapped item is not SFGovApplicant, got {type(mapped)!r} for row with locationid={row.get('locationid')}"
                )
            sf_rows.append(mapped)

        # Convert to domain Applicant objects for the application layer
        applicants: List[Applicant] = []
        for s in sf_rows:
            applicants.append(
                Applicant(
                    permit=None,  # Domain Permit mapping is out of scope here
                    locationId=s.locationid,
                    name=s.applicant,
                    foodItems=s.food_items,
                )
            )

        # Final runtime verification that we indeed return Applicant instances
        if not all(isinstance(a, Applicant) for a in applicants):
            raise TypeError("load_applicants must return a List[Applicant]")

        return applicants


        