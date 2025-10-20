from __future__ import annotations

import logging
from asyncio import sleep
from datetime import datetime, timezone
from typing import List, Optional

from celery import shared_task
from sodapy import Socrata

from backend.app.domain.models import FoodProvider, Permit, PermitStatus, Coordinate
from backend.app.domain.ports import FoodProviderClient, FoodProviderRepository


DATASET_ID = "rqzj-sfat"  # Mobile Food Facility Permits (SF Gov)
DOMAIN = "data.sfgov.org"

logger = logging.getLogger(__name__)


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

    # Coordinates can be in 'latitude'/'longitude' or in 'location' object
    try:
        lat = float(r.get("latitude")) if r.get("latitude") is not None else None
        lon = float(r.get("longitude")) if r.get("longitude") is not None else None
    except Exception:
        lat, lon = None, None

    if lat is None or lon is None:
        loc = r.get("location") or {}
        try:
            lat = float(loc.get("latitude")) if loc and loc.get("latitude") is not None else 0.0
            lon = float(loc.get("longitude")) if loc and loc.get("longitude") is not None else 0.0
        except Exception:
            lat, lon = 0.0, 0.0

    coord = Coordinate(latitude=lat or 0.0, longitude=lon or 0.0)

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


class SFGovFoodProviderClient(FoodProviderClient):
    """SFGov implementation of FoodProviderClient using the Socrata API."""

    def __init__(self, repository: FoodProviderRepository, app_token: Optional[str] = None):
        self.repository = repository
        self.client = Socrata(DOMAIN, app_token, timeout=30)
        self._last_update_time: datetime | None = None


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

    def map_results(self, results: List[dict], update_time: datetime) -> List[FoodProvider]:
        providers: List[FoodProvider] = []
        for row in results:
            try:
                fp = _foodprovider_from_row(row)
            except Exception:
                continue

            if fp is not None:
                providers.append(fp)

        self._last_update_time = update_time
        return providers

    async def periodic_task(self) -> None:
        logger.info("Running periodic task for SFGovFoodProviderClient")
        meta = self.client.get_metadata(DATASET_ID)
        ts = meta.get("rowsUpdatedAt") or meta.get("rowsUpdatedAt")
        try:
            source_updated_at = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        except Exception:
            raise Exception(f"Unable to parse Socrata rowsUpdatedAt: {ts}")

        if self._last_update_time is None or self._last_update_time != source_updated_at:
            results = await self.fetch_all()
            providers = self.map_results(results, source_updated_at)
            self.repository.replace_all(providers)

    def get_interval(self) -> int:
        return 3600


