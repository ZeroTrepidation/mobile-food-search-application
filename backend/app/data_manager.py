from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from app.domain.ports import FoodProviderDataClient, FoodProviderRepository

logger = logging.getLogger(__name__)


class DataManager:
    """
    Manages periodic polling of upstream data sources (data clients).
    - Checks source metadata (last updated timestamp)
    - If new data is available, fetches and maps it
    - Updates the repository
    """

    def __init__(self, repository: FoodProviderRepository, clients: List[FoodProviderDataClient]):
        self._repository = repository
        self._clients = clients
        self._last_updates: Dict[FoodProviderDataClient, Optional[datetime]] = {c: None for c in clients}
        self._task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()

    async def _run_loop(self):
        try:
            while not self._stop_event.is_set():
                min_interval = None
                for client in self._clients:
                    try:
                        interval = max(1, int(client.get_interval()))
                    except Exception:
                        interval = 3600
                    min_interval = interval if min_interval is None else min(min_interval, interval)

                    try:
                        source_updated_at = client.get_source_updated_at()
                    except Exception as e:
                        logger.warning(f"Failed to read metadata for {client.__class__.__name__}: {e}")
                        continue

                    last_seen = self._last_updates.get(client)
                    if last_seen is None or last_seen != source_updated_at:
                        logger.info(f"Change detected for {client.__class__.__name__}. Fetching new data...")
                        try:
                            rows = await client.fetch_all()
                            providers = client.map_results(rows)
                            self._repository.replace_all(providers)
                            self._last_updates[client] = source_updated_at
                            logger.info(
                                f"Updated repository with {len(providers)} providers from {client.__class__.__name__}")
                        except Exception as e:
                            logger.exception(f"Failed to update from {client.__class__.__name__}: {e}")
                # Sleep for the minimum interval among clients
                await asyncio.wait_for(self._stop_event.wait(), timeout=min_interval or 3600)
        except asyncio.TimeoutError:
            # Normal wake-up to continue loop
            if not self._stop_event.is_set():
                await self._run_loop()
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None

    def start(self):
        if self._task is not None and not self._task.done():
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        if self._task is None:
            return
        self._stop_event.set()
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None
