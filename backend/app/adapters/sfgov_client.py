from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import ValidationError
from sodapy import Socrata

from backend.app.domain.models import FoodProvider, Permit, PermitStatus, Coordinate
from backend.app.domain.ports import FoodProviderDataClient


DATASET_ID = "rqzj-sfat"  # Mobile Food Facility Permits (SF Gov)
DOMAIN = "data.sfgov.org"

logger = logging.getLogger(__name__)

class SFGovFoodProviderDataClient(FoodProviderDataClient):
    """SFGov implementation of FoodProviderClient using the Socrata API."""

    def __init__(self, app_token: Optional[str] = None):
        self.client = Socrata(DOMAIN, app_token, timeout=30)



    async def fetch_all(self) -> List[dict]:
        logger.info("Fetching SFGovFoodProviderClient data")
        results: List[dict] = []
        offset = 0
        batch_size = 2000
        while True:
            chunk = self.client.get(DATASET_ID, limit=batch_size, offset=offset)
            if not chunk:
                break
            results.extend(chunk)
            if len(chunk) < batch_size:
                break
            offset += batch_size
        logger.info(f"Fetched {len(results)} rows from SFGovFoodProviderClient")
        return results

    def map_results(self, results: List[dict]) -> List[FoodProvider]:
        providers: List[FoodProvider] = []
        for row in results:
            try:
                fp = _foodprovider_from_row(row)
            except ValidationError:
                continue

            if fp is not None:
                providers.append(fp)

        return providers

    def get_source_updated_at(self) -> datetime:
        meta = self.client.get_metadata(DATASET_ID)
        ts = meta.get("rowsUpdatedAt") or meta.get("rowsUpdatedAt")
        try:
            return datetime.fromtimestamp(int(ts), tz=timezone.utc)
        except Exception:
            raise Exception(f"Unable to parse Socrata rowsUpdatedAt: {ts}")

    def get_interval(self) -> int:
        return 3600

def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        # Many dates in this dataset are ISO-like strings
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        try:
            # Fallback: epoch seconds as string
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except Exception:
            return None


def _foodprovider_from_row(r: dict) -> FoodProvider | None:
    try:
        status_str = (r.get("status") or "").upper()
        permit_status = PermitStatus[
            status_str] if status_str in PermitStatus.__members__ else PermitStatus.APPROVED
    except Exception:
        # Default to APPROVED if unknown
        permit_status = PermitStatus.APPROVED

    permit = Permit(
        permitStatus=permit_status,
        permitID=r.get("permit") or r.get("objectid") or "",
        approvalDate=_parse_dt(r.get("approved")),
        recievedDate=_parse_dt(r.get("received")),
        expirationDate=_parse_dt(r.get("expirationdate")),
    )

    coord = (Coordinate(latitude=r.get("latitude"), longitude=r.get("longitude")))

    fp = FoodProvider(
        location_id=str(r.get("locationid") or r.get("objectid") or ""),
        name=r.get("applicant") or "",
        food_items=r.get("fooditems") or "",
        permit=permit,
        coord=coord,
        location_description=r.get("locationdescription"),
        blocklot=r.get("blocklot"),
        block=r.get("block"),
        lot=r.get("lot"),
        cnn=int(r["cnn"]) if r.get("cnn") not in (None, "") else None,
        address=r.get("address"),
    )
    return fp
