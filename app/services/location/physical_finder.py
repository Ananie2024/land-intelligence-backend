# app/services/location/physical_finder.py
"""
Physical Location Finder Service
Phase 2 — Section 3.2
Land Intelligence System
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.location_repository import LocationRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.parcel_repository import ParcelRepository

logger = logging.getLogger(__name__)

class PhysicalFinder:
    """
    Service for locating physical archive materials from digital records.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize finder service with database session.
        """
        self.location_repo = LocationRepository(db)
        self.document_repo = DocumentRepository(db)
        self.parcel_repo = ParcelRepository(db)

    async def find_location(
        self,
        parcel_id: Optional[str] = None,
        document_id: Optional[str] = None,
        reference_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search for physical document locations using various criteria.
        
        Resolves location down to Building, Room, Shelf, Cabinet and Drawer.
        """
        doc = None
        
        if document_id:
            doc = await self.document_repo.get(document_id)
            if not doc:
                return {
                    "found": False,
                    "message": f"Document ID '{document_id}' not found."
                }
        elif reference_number:
            doc = await self.document_repo.get_by_reference_number(reference_number)
            if not doc:
                return {
                    "found": False,
                    "message": f"Document with reference number '{reference_number}' not found."
                }
        elif parcel_id:
            parcel = await self.parcel_repo.get(parcel_id)
            if not parcel:
                return {
                    "found": False,
                    "message": f"Parcel ID '{parcel_id}' not found."
                }
            docs = await self.document_repo.get_by_parcel(parcel_id, limit=1)
            if not docs:
                return {
                    "found": False,
                    "parcel_id": parcel_id,
                    "upi": parcel.upi,
                    "message": f"No active documents found for parcel with UPI '{parcel.upi}'."
                }
            doc = docs[0]
        else:
            return {
                "found": False,
                "message": "At least one search parameter (parcel_id, document_id, reference_number) must be provided."
            }

        # Resolve location for the matched document
        location = await self.location_repo.find_by_document(doc.id)
        
        # Resolve parcel info
        parcel_info = None
        if doc.parcel_id:
            parcel_info = await self.parcel_repo.get(doc.parcel_id)

        if not location:
            return {
                "found": False,
                "parcel_id": str(parcel_info.id) if parcel_info else None,
                "upi": parcel_info.upi if parcel_info else None,
                "document_id": str(doc.id),
                "document_filename": doc.filename,
                "message": f"No physical archive location mapped for document '{doc.filename}'."
            }

        # Retrieve cabinets associated with this room/location
        cabinets = await self.location_repo.get_cabinets_by_location(location.id)
        cabinet = cabinets[0] if cabinets else None

        return {
            "found": True,
            "parcel_id": str(parcel_info.id) if parcel_info else None,
            "upi": parcel_info.upi if parcel_info else None,
            "document_id": str(doc.id),
            "document_filename": doc.filename,
            "physical_location": location,
            "storage_cabinet": cabinet,
            "message": "Physical archive location successfully resolved."
        }
