# app/services/location/location_validator.py
"""
Location Validator Service
Phase 2 — Section 3.2
Land Intelligence System
"""

import re
from typing import Optional
from app.models.storage_cabinet import StorageCabinet
from app.schemas.physical_location_schema import StorageCabinetCreate, PhysicalLocationCreate

class LocationValidator:
    """
    Validates physical location codes, building rooms, and cabinet storage capacities.
    """
    
    # Code pattern: e.g. LOC-BLD1-RM2-CAB3
    CODE_PATTERN = r"^[A-Z0-9_-]+$"

    @staticmethod
    def validate_location_code(code: str) -> bool:
        """
        Verify that a physical location code conforms to administrative standards.
        """
        return bool(re.match(LocationValidator.CODE_PATTERN, code))

    @staticmethod
    def has_available_capacity(cabinet: StorageCabinet, documents_to_add: int = 1) -> bool:
        """
        Check if a storage cabinet has enough physical capacity left to store new documents.
        """
        if cabinet.max_capacity is None:
            return True  # Unlimited capacity if not specified
            
        remaining = cabinet.max_capacity - cabinet.current_count
        return remaining >= documents_to_add
