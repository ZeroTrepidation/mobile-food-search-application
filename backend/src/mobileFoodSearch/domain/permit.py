from enum import Enum
from datetime import datetime
from typing import Any, Dict, Optional

class PermitStatus(Enum):
    APPROVED = "APPROVED"
    EXPIRED = "EXPIRED"
    REQUESTED = "REQUESTED"
    SUSPEND = "SUSPEND"
    ISSUED = "ISSUED"


class Permit(object):

    def __init__(self, permitStatus, permitID, approvalDate, recievedDate, expirationDate):
        self.permitStatus = permitStatus
        self.permitID = permitID
        self.approvalDate = approvalDate
        self.recievedDate = recievedDate
        self.expirationDate = expirationDate

    def to_dict(self) -> Dict[str, Any]:
        def _dt(v: Optional[datetime]):
            if isinstance(v, datetime):
                # ISO 8601 string
                return v.isoformat()
            return v
        status = self.permitStatus.value if isinstance(self.permitStatus, PermitStatus) else self.permitStatus
        return {
            "permitStatus": status,
            "permitID": self.permitID,
            "approvalDate": _dt(self.approvalDate),
            "recievedDate": _dt(self.recievedDate),
            "expirationDate": _dt(self.expirationDate),
        }