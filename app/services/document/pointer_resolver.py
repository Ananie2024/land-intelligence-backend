# app/services/document/pointer_resolver.py
"""
Service module for resolving physical archive location from digital document pointer.

Responsibility: Resolves physical location from digital pointer.
Scope: Phase 3 - Backend API & Services
"""

from typing import Optional
from uuid import UUID

from app.models.document import Document
from app.models.physical_location import PhysicalLocation
from app.repositories.location_repository import LocationRepository


class PointerResolver:
    """
    Resolves physical archive location from a digital document pointer.

    Maps a document's digital identifier to its physical storage location
    including building, room, cabinet, drawer, and folder reference.
    """

    def __init__(self, location_repository: LocationRepository):
        """
        Initialize the pointer resolver with location repository dependency.

        Args:
            location_repository: Repository for physical location queries
        """
        self.location_repository = location_repository

    async def resolve_from_document(self, document: Document) -> Optional[PhysicalLocation]:
        """
        Resolve physical location from a document entity.

        Args:
            document: Document entity containing physical location reference

        Returns:
            PhysicalLocation if found, None otherwise
        """
        return await self.location_repository.find_by_document(document.id)

    async def resolve_with_cabinet(self, document: Document) -> Optional[dict]:
        """
        Resolve physical location including cabinet details.

        Args:
            document: Document entity containing physical location reference

        Returns:
            Dictionary with location and cabinet information if found,
            None otherwise
        """
        location = await self.resolve_from_document(document)
        if not location:
            return None

        result = {
            "location_id": str(location.id),
            "name": location.name,
            "location_code": location.location_code,
            "building": location.building or "Unknown Building",
            "floor": location.floor or "",
            "room_number": location.room_number or "",
            "description": location.description or "",
            "access_restrictions": location.access_restrictions or "",
        }

        cabinets = await self.location_repository.get_cabinets_by_location(location.id)
        if cabinets:
            cabinet = cabinets[0]
            if cabinet:
                result["cabinet"] = {
                    "cabinet_id": str(cabinet.id),
                    "cabinet_number": cabinet.cabinet_number or "",
                    "cabinet_type": cabinet.cabinet_type or "",
                    "row_number": cabinet.row_number,
                    "column_number": cabinet.column_number,
                    "description": cabinet.description or "",
                }

        return result

    async def resolve_by_document_id(self, document_id: UUID, document_repository) -> Optional[dict]:
        """
        Resolve physical location by document ID.

        Args:
            document_id: UUID of the document
            document_repository: Document repository instance for fetching document

        Returns:
            Dictionary with location and cabinet information if found,
            None otherwise
        """
        document = await document_repository.get(document_id)
        if not document:
            return None

        return await self.resolve_with_cabinet(document)

    async def get_location_summary(self, document: Document) -> Optional[str]:
        """
        Get human-readable location summary for a document.

        Args:
            document: Document entity

        Returns:
            Formatted location string or None if no location
        """
        location_data = await self.resolve_with_cabinet(document)
        if not location_data:
            return None

        parts = []
        
        building = location_data.get("building", "")
        if building and building != "Unknown Building":
            parts.append(building)
        elif location_data.get("name"):
            parts.append(location_data["name"])
        else:
            parts.append("Unspecified Location")

        floor = location_data.get("floor")
        if floor:
            parts.append(f"Floor {floor}")

        room = location_data.get("room_number")
        if room:
            parts.append(f"Room {room}")

        cabinet = location_data.get("cabinet")
        if cabinet:
            cabinet_number = cabinet.get("cabinet_number")
            if cabinet_number:
                parts.append(f"Cabinet {cabinet_number}")
            
            row_number = cabinet.get("row_number")
            if row_number:
                parts.append(f"Row {row_number}")
            
            column_number = cabinet.get("column_number")
            if column_number:
                parts.append(f"Column {column_number}")

        return " > ".join(parts)
