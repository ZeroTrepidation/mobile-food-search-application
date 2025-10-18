from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional, List

from backend.src.mobileFoodSearch.domain.foodprovider import FoodProvider
from backend.src.mobileFoodSearch.domain.foodprovider_repository import FoodProviderRepository
from backend.src.mobileFoodSearch.domain.permit import PermitStatus, Permit
from backend.src.mobileFoodSearch.infrastructure.sf_gov_datasource import SODAClientDatasource


class SodaApplicantLoaderService:
    def __init__(
        self,
        repository: FoodProviderRepository,
        datasource: SODAClientDatasource,
        interval_seconds: int = 3600,
    ) -> None:
        self._repo = repository
        self._datasource = datasource
        self._interval = max(1, int(interval_seconds))
        self._task: Optional[asyncio.Task] = None
        self._stopping = False
        self._local_data_version: Optional[datetime] = None
        self._lock = asyncio.Lock()

    def start(self) -> None:
        """Start the periodic background refresh loop."""
        if self._task and not self._task.done():
            return
        self._stopping = False
        self._task = asyncio.create_task(self._run_loop(), name="SodaApplicantLoaderServiceLoop")

    async def stop(self) -> None:
        """Stop the background loop and wait for it to finish."""
        self._stopping = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            finally:
                self._task = None

    async def run_once(self) -> None:
        """Perform a single refresh cycle: if dataset updated, fetch and replace."""
        async with self._lock:
            try:
                last_datesource_update = await asyncio.to_thread(self._datasource.get_last_update_time)
                if not self._local_data_version or last_datesource_update > self._local_data_version:
                    # Fetch full dataset (with paging if available)

                    rows: List[dict] = await asyncio.to_thread(self._datasource.fetch_all)

                    entities = [map_json_to_food_provider(r) for r in rows if r is not None]
                    self._repo.bulk_update(entities)
                    self._local_data_version = last_datesource_update
                    # self.logger.info(f"Local data version: {self._local_data_version}")
                else:
                    print("SodaApplicantLoaderService: no changes detected.")
            except Exception as exc:
                # Do not update _last_seen on failures
                print(f"SodaApplicantLoaderService: error during refresh: {exc}")

    async def _run_loop(self) -> None:
        # Initial load at startup
        await self.run_once()

        # Periodic loop
        while not self._stopping:
            try:
                await asyncio.sleep(self._interval)
            except asyncio.CancelledError:
                break
            await self.run_once()


def map_json_to_food_provider(data: dict) -> FoodProvider:
    """
    Converts a raw JSON dictionary from the Socrata dataset
    into a FoodProvider domain object.
    """

    # --- Permit construction ---
    status_str = data.get("status")
    permit_status = None
    if status_str:
        try:
            permit_status = PermitStatus[status_str.upper()]
        except KeyError:
            # Handle unexpected status gracefully
            permit_status = None

    permit_id = data.get("permit")
    approval_date = data.get("approved")  # field not in sample but safe to include
    received_date = data.get("received")
    expiration_date = data.get("expirationdate")

    # Normalize date strings
    def parse_date(value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        for fmt in ("%Y%m%d", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return None

    permit = None
    if permit_id or permit_status:
        permit = Permit(
            permitStatus=permit_status,
            permitID=permit_id,
            approvalDate=parse_date(approval_date),
            recievedDate=parse_date(received_date),
            expirationDate=parse_date(expiration_date),
        )

    # --- FoodProvider construction ---
    provider = FoodProvider(
        location_id=str(data.get("objectid", "")),
        name=data.get("applicant", ""),
        food_items=data.get("fooditems", ""),
        permit=permit,
        longitude=_try_float(data.get("longitude")),
        latitude=_try_float(data.get("latitude")),
        location_description=data.get("locationdescription"),
        blocklot=data.get("blocklot"),
        block=data.get("block"),
        lot=data.get("lot"),
        cnn=_try_int(data.get("cnn")),
        address=data.get("address"),
    )

    return provider


def _try_float(value) -> Optional[float]:
    try:
        return float(value) if value is not None else None
    except (ValueError, TypeError):
        return None


def _try_int(value) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except (ValueError, TypeError):
        return None