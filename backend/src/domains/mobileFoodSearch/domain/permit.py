from enum import Enum

class PermitStatus(Enum):
    APPROVED = "APPROVED"
    EXPIRED = "EXPIRED"
    REQUESTED = "REQUESTED"
    SUSPEND = "SUSPEND"
    ISSUED = "ISSUED"

class Permit(object):

    _permitStatus = None
    _permitID = None
    _approvalDate = None
    _recievedDate = None
    _expirationDate = None

    def __init__(self, permitStatus, permitID, approvalDate, recievedDate, expirationDate):
        self._permitStatus = permitStatus
        self._permitID = permitID
        self._approvalDate = approvalDate
        self._recievedDate = recievedDate
        self._expirationDate = expirationDate

    getPermitStatus = property(lambda self: self._permitStatus)
    getPermitID = property(lambda self: self._permitID)