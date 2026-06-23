# app/services/location/location_service.py
"""
Physical Location Service
Phase 2 — Section 3.2
Land Intelligence System
"""

import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.physical_location import PhysicalLocation
from app.models.storage_cabinet import StorageCabinet
from app.repositories.location_repository import LocationRepository
from app.services.location.location_validator import LocationValidator
from app.services.location.storage_mapper import StorageMapper
from app.services.location.physical_finder import PhysicalFinder
from app.schemas.physical_location_schema import (
    PhysicalLocationCreate,
    PhysicalLocationUpdate,
    StorageCabinetCreate,
    StorageCabinetUpdate,
)

logger = logging.getLogger(__name__)


class LocationService:
    """
    Business logic layer for physical location operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LocationRepository(db)
        self.physical_finder = PhysicalFinder(db)

    async def create_location(self, payload: PhysicalLocationCreate, user_id: str) -> PhysicalLocation:
        """
        Register a new physical archive room, warehouse, or shelf location.
        """
        # Validate unique location code
        existing = await self.db.execute(
            select(PhysicalLocation).where(
                PhysicalLocation.location_code == payload.location_code,
                PhysicalLocation.is_active
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Location code '{payload.location_code}' is already registered.")

        # Code format validation
        if not LocationValidator.validate_location_code(payload.location_code):
            raise ValueError("Location code must contain only alphanumeric characters, dashes, or underscores.")

        location = await self.repo.create(payload)
        await self.db.commit()
        await self.db.refresh(location)

        logger.info(f"Physical location created: {location.id} (code: {payload.location_code}) by user {user_id}")
        return location

    async def list_locations(self, skip: int = 0, limit: int = 100) -> List[PhysicalLocation]:
        """
        List active physical archive locations.
        """
        return await self.repo.list(skip=skip, limit=limit, order_by="location_code")

    async def get_location(self, location_id: str) -> Optional[PhysicalLocation]:
        """
        Fetch details of a single physical location by UUID.
        """
        return await self.repo.get(location_id)

    async def update_location(self, location_id: str, payload: PhysicalLocationUpdate, user_id: str) -> Optional[PhysicalLocation]:
        """
        Partially update physical location parameters.
        """
        # Verify location code uniqueness if modified
        if payload.location_code is not None:
            existing = await self.db.execute(
                select(PhysicalLocation).where(
                    PhysicalLocation.location_code == payload.location_code,
                    PhysicalLocation.is_active
                )
            )
            conflict = existing.scalar_one_or_none()
            if conflict and str(conflict.id) != location_id:
                raise ValueError(f"Location code '{payload.location_code}' is already registered.")

            if not LocationValidator.validate_location_code(payload.location_code):
                raise ValueError("Location code must contain only alphanumeric characters, dashes, or underscores.")

        location = await self.repo.update(location_id, payload)
        if not location:
            return None

        await self.db.commit()
        await self.db.refresh(location)

        logger.info(f"Physical location updated: {location_id} by user {user_id}")
        return location

    async def delete_location(self, location_id: str, user_id: str) -> bool:
        """
        Soft-delete a physical location.
        """
        location = await self.repo.get(location_id)
        if not location:
            return False

        await self.repo.soft_delete(location_id)
        await self.db.commit()

        logger.info(f"Physical location deleted: {location_id} by user {user_id}")
        return True

    async def locate_document(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve and locate the physical storage coordinates of a document or parcel.
        """
        res = await self.physical_finder.find_location(
            parcel_id=payload.get("parcel_id"),
            document_id=payload.get("document_id"),
            reference_number=payload.get("reference_number")
        )
        return res

    async def create_cabinet(self, payload: StorageCabinetCreate, user_id: str) -> StorageCabinet:
        """
        Create a storage cabinet under an existing physical location.
        """
        # Verify location exists
        location = await self.repo.get(payload.physical_location_id)
        if not location:
            raise ValueError(f"Physical location '{payload.physical_location_id}' not found.")

        # Create cabinet
        data = payload.model_dump(exclude_none=True)
        cabinet = StorageCabinet(**data)
        self.db.add(cabinet)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(cabinet)

        logger.info(f"Storage cabinet created: {cabinet.id} in location {payload.physical_location_id} by user {user_id}")
        return cabinet

    async def get_cabinet(self, cabinet_id: str) -> Optional[StorageCabinet]:
        """
        Retrieve details of a storage cabinet by UUID.
        """
        return await self.repo.get_cabinet(cabinet_id)

    async def update_cabinet(self, cabinet_id: str, payload: StorageCabinetUpdate, user_id: str) -> Optional[StorageCabinet]:
        """
        Partially update a cabinet.
        """
        cabinet = await self.repo.get_cabinet(cabinet_id)
        if not cabinet:
            return None

        if payload.physical_location_id is not None:
            location = await self.repo.get(payload.physical_location_id)
            if not location:
                raise ValueError(f"Physical location '{payload.physical_location_id}' not found.")

        # Validate current count is not exceeding max capacity
        if payload.current_count is not None or payload.max_capacity is not None:
            new_count = payload.current_count if payload.current_count is not None else cabinet.current_count
            new_max = payload.max_capacity if payload.max_capacity is not None else cabinet.max_capacity
            if new_max is not None and new_count > new_max:
                raise ValueError(f"New count {new_count} cannot exceed cabinet max capacity {new_max}.")

        # Apply changes
        data = payload.model_dump(exclude_none=True)
        for field, value in data.items():
            if hasattr(cabinet, field):
                setattr(cabinet, field, value)

        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(cabinet)

        logger.info(f"Storage cabinet updated: {cabinet_id} by user {user_id}")
        return cabinet

    async def get_location_grid(self, location_id: str) -> Dict[str, Any]:
        """
        Retrieve the visual row-column map coordinate grid representation of all cabinets in this location.
        """
        location = await self.repo.get(location_id)
        if not location:
            raise ValueError(f"Physical location '{location_id}' not found.")

        cabinets = await self.repo.get_cabinets_by_location(location_id)
        return StorageMapper.map_cabinet_layout_grid(cabinets)