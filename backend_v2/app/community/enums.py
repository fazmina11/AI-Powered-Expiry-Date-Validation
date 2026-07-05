"""
community/enums.py
All PGN Phase 1 enumerations.
"""
import enum


class ReportType(str, enum.Enum):
    DAMAGED_PACKAGING = "DAMAGED_PACKAGING"
    WRONG_EXPIRY      = "WRONG_EXPIRY"
    BAD_SMELL         = "BAD_SMELL"
    LEAKAGE           = "LEAKAGE"
    WRONG_PRODUCT     = "WRONG_PRODUCT"
    FOREIGN_OBJECT    = "FOREIGN_OBJECT"
    FAKE_PRODUCT      = "FAKE_PRODUCT"
    OTHER             = "OTHER"


class Severity(str, enum.Enum):
    LOW      = "LOW"
    MEDIUM   = "MEDIUM"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"


class ReportStatus(str, enum.Enum):
    PENDING      = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED     = "VERIFIED"
    REJECTED     = "REJECTED"
