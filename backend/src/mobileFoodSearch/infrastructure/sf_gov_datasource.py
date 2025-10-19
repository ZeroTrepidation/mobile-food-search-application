from typing import List
from sodapy import Socrata
from datetime import datetime, timezone
import requests

from backend.src.mobileFoodSearch.infrastructure.foodprovider_datasource import IFoodProviderDatasource


class SODAClientDatasource(IFoodProviderDatasource):

    def __init__(self, domain: str, dataset_id: str, app_token: str | None = None):
        assert domain and dataset_id
        self.domain = domain
        self.dataset_id = dataset_id
        self.client = Socrata(self.domain, app_token)

    def fetch_all(self, batch_size: int = 2000) -> List[dict]:
        results: List[dict] = []
        offset = 0
        while True:
            chunk = self.client.get(self.dataset_id, limit=batch_size, offset=offset)
            if not chunk:
                break
            results.extend(chunk)
            if len(chunk) < batch_size:
                break
            offset += batch_size
        return results

    def get_last_update_time(self) -> datetime:
        url = f"https://{self.domain}/api/views/{self.dataset_id}.json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        timestamp = data.get("rowsUpdatedAt") or data.get("viewLastModified")
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)