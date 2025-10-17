from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Callable, Optional, List

from backend.src.domains.mobileFoodSearch.domain.applicant_repository import ApplicantRepository
from backend.src.domains.mobileFoodSearch.infrastructure.sf_gov_datasource import SODAClientDatasource


class SodaApplicantLoaderService:
    """Loads and periodically updates applicant data from a Socrata (SODA) dataset.

    Responsibilities:
    - On startup and hourly, check if the dataset has changed.
    - If changed, fetch the full dataset and push it into the repository via replace_all().

    Notes:
    - The repository remains storage-only; this service owns loading and change detection.
    - Blocking I/O to SODA is offloaded to a thread to avoid blocking the event loop.
    - last_seen is only advanced after a successful replace_all to avoid missing updates on errors.
    """

    def __init__(
        self,
        repository: ApplicantRepository,
        datasource: SODAClientDatasource,
        row_to_entity: Callable[[dict], object],
        interval_seconds: int = 3600,
    ) -> None:
        self._repo = repository
        self._ds = datasource
        self._map = row_to_entity
        self._interval = max(1, int(interval_seconds))
        self._task: Optional[asyncio.Task] = None
        self._stopping = False
        self._last_seen: Optional[datetime] = None
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
                current = await asyncio.to_thread(self._ds.get_last_update_time)
                if not self._last_seen or current > self._last_seen:
                    # Fetch full dataset (with paging if available)
                    fetch_all = getattr(self._ds, "fetch_all", None)
                    if callable(fetch_all):
                        rows: List[dict] = await asyncio.to_thread(fetch_all, 5000)
                    else:
                        # Fallback to single-page fetch; may truncate if dataset is large
                        rows = await asyncio.to_thread(self._ds.fetch_data, 1000)

                    entities = [self._map(r) for r in rows if r is not None]
                    self._repo.replace_all(entities)
                    self._last_seen = current
                    print(f"SodaApplicantLoaderService: refreshed {len(entities)} applicants at {current.isoformat()}.")
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
