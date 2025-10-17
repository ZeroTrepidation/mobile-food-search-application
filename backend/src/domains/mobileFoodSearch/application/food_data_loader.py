from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Protocol, runtime_checkable

from backend.src.domains.mobileFoodSearch.domain.applicant import Applicant


class IFoodDataLoader(ABC):

    @abstractmethod
    def load_applicants(self) -> List[Applicant]:

        raise NotImplementedError

