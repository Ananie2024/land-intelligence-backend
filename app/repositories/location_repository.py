# app/repositories/location_repository.py
"""
Location Repository
Phase 2 — Section 3.2
Land Intelligence System
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.physical_location import PhysicalLocation
from app.models.storage_cabinet import StorageCabinet
from app.repositories.base_repository import BaseRepository
from app.schemas.physical_location_schema import PhysicalLocationCreate, PhysicalLocationUpdate


class LocationRepository(BaseRepository[PhysicalLocation, PhysicalLocationCreate, PhysicalLocationUpdate]):
    """
    Repository for PhysicalLocation entity with extended functionality.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize location repository.
        
        Args:
            db: Async database session
        """
        super().__init__(PhysicalLocation, db)
    
    async def find_by_document(self, document_id: str) -> Optional[PhysicalLocation]:
        """
        Find physical location by document ID.
        
        Args:
            document_id: UUID of the document
            
        Returns:
            Physical location if found, None otherwise
        """
        result = await self.db.execute(
            select(PhysicalLocation).where(
                PhysicalLocation.document_id == document_id,
                PhysicalLocation.is_active
            )
        )
        return result.scalar_one_or_none()
    
    async def get_cabinet_contents(self, cabinet_id: str) -> List[StorageCabinet]:
        """
        Get storage cabinet details for a cabinet.
        
        Args:
            cabinet_id: UUID of the storage cabinet
            
        Returns:
            Storage cabinet instance as list (single item)
        """
        result = await self.db.execute(
            select(StorageCabinet).where(
                StorageCabinet.id == cabinet_id,
                StorageCabinet.is_active
            )
        )
        cabinet = result.scalar_one_or_none()
        return [cabinet] if cabinet else []
    
    async def get_cabinets_by_location(self, location_id: str) -> List[StorageCabinet]:
        """
        Get all cabinets in a physical location.
        
        Args:
            location_id: UUID of the physical location
            
        Returns:
            List of storage cabinets
        """
        result = await self.db.execute(
            select(StorageCabinet).where(
                StorageCabinet.physical_location_id == location_id,
                StorageCabinet.is_active
            ).order_by(StorageCabinet.cabinet_number)
        )
        return list(result.scalars().all())
    
    async def get_cabinet(self, cabinet_id: str) -> Optional[StorageCabinet]:
        """
        Get a specific storage cabinet by ID.
        
        Args:
            cabinet_id: UUID of the storage cabinet
            
        Returns:
            Storage cabinet if found, None otherwise
        """
        result = await self.db.execute(
            select(StorageCabinet).where(
                StorageCabinet.id == cabinet_id,
                StorageCabinet.is_active
            )
        )
        return result.scalar_one_or_none()
    
    async def get_cabinet_by_number(self, location_id: str, cabinet_number: str) -> Optional[StorageCabinet]:
        """
        Get a storage cabinet by its number within a location.
        
        Args:
            location_id: UUID of the physical location
            cabinet_number: Cabinet identifier
            
        Returns:
            Storage cabinet if found, None otherwise
        """
        result = await self.db.execute(
            select(StorageCabinet).where(
                StorageCabinet.physical_location_id == location_id,
                StorageCabinet.cabinet_number == cabinet_number,
                StorageCabinet.is_active
            )
        )
        return result.scalar_one_or_none()
    
    async def get_location_by_code(self, location_code: str) -> Optional[PhysicalLocation]:
        """
        Get physical location by unique code.
        
        Args:
            location_code: Unique location code
            
        Returns:
            Physical location if found, None otherwise
        """
        result = await self.db.execute(
            select(PhysicalLocation).where(
                PhysicalLocation.location_code == location_code,
                PhysicalLocation.is_active
            )
        )
        return result.scalar_one_or_none()
    
    async def create_cabinet(self, cabinet_data: dict) -> StorageCabinet:
        """
        Create a new storage cabinet.
        
        Args:
            cabinet_data: Dictionary of cabinet attributes
            
        Returns:
            Created storage cabinet
        """
        cabinet = StorageCabinet(**cabinet_data)
        self.db.add(cabinet)
        await self.db.flush()
        await self.db.refresh(cabinet)
        return cabinet
    
    async def update_cabinet_count(self, cabinet_id: str, increment: int = 1) -> Optional[StorageCabinet]:
        """
        Update the current count of documents in a cabinet.
        
        Args:
            cabinet_id: UUID of the storage cabinet
            increment: Amount to add to current count (positive or negative)
            
        Returns:
            Updated storage cabinet, None if not found
        """
        cabinet = await self.get_cabinet(cabinet_id)
        if cabinet:
            new_count = max(0, cabinet.current_count + increment)
            cabinet.current_count = new_count
            await self.db.flush()
            await self.db.refresh(cabinet)
        return cabinet
    
    async def search_locations(
        self,
        name: Optional[str] = None,
        building: Optional[str] = None,
        location_code: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PhysicalLocation]:
        """
        Search physical locations by various criteria.
        
        Args:
            name: Filter by location name (partial match)
            building: Filter by building (partial match)
            location_code: Filter by location code (partial match)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching physical locations
        """
        query = select(PhysicalLocation).where(PhysicalLocation.is_active)
        
        if name:
            query = query.where(PhysicalLocation.name.contains(name))
        
        if building:
            query = query.where(PhysicalLocation.building.contains(building))
        
        if location_code:
            query = query.where(PhysicalLocation.location_code.contains(location_code))
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())