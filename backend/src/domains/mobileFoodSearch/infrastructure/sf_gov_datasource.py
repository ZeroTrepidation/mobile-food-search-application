from typing import List, Optional
from sodapy import Socrata
from datetime import datetime, timezone
import json
import os
import requests
import asyncio


class SODAClientDatasource:

    def __init__(self, domain, dataset_id):
        self.domain = domain
        self.dataset_id = dataset_id
        assert domain is not None
        self.client = Socrata(self.domain, None)
        self.last_seen: dict[str, datetime] = {}

    def fetch_data(self, limit: int = 1000):
        return self.client.get(self.dataset_id, limit=limit)

    def get_last_update_time(self, dataset_id: str) -> datetime:
        url = f"https://{self.domain}/api/views/{self.dataset_id}.json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        timestamp = data.get("rowsUpdatedAt") or data.get("viewLastModified")
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    async def check_for_updates(self, dataset_id: str, callback):
        current = self.get_last_update_time(dataset_id)
        last_seen = self.last_seen.get(dataset_id)

        if not last_seen or current > last_seen:
            print(f"📈 Dataset {dataset_id} updated at {current}")
            await callback(dataset_id)
            self.last_seen[dataset_id] = current
        else:
            print(f"⏸️ No change for dataset {dataset_id}")