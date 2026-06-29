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