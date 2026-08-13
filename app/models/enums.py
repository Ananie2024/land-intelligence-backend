"""
Domain Enumerations
Land Intelligence System
"""

from enum import Enum


class TaxRecordStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class DocumentType(str, Enum):
    """
    Land Registry document types as defined by the system.
    Used for categorizing documents in the land management system.
    """
    LAND_TITLES = "land_titles"
    LAND_DEEDS = "land_deeds"
    LETTERS = "letters"
    LAND_LEASES = "land_leases"
    REPORTS = "reports"
    SURVEYS = "surveys"
    CESSION = "cession"
    OTHERS = "others"
    UNSPECIFIED = "unspecified"


class LeaseStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    RENEWED = "renewed"


class PaymentFrequency(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"


class LeasePaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    PARTIAL = "partial"
    CANCELLED = "cancelled"