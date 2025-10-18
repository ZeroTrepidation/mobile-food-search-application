from abc import ABC, abstractmethod
from datetime import datetime
from typing import List


class IFoodProviderDatasource(ABC):

    @abstractmethod
    def fetch_all(self, batch_size: int = 5000) -> List[dict]:
        pass

    @abstractmethod
    def get_last_update_time(self) -> datetime:
        pass
