"""
Parish Repository
Phase 2 — Section 3.2
Land Intelligence System
"""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parish import Parish
from app.models.parcel import Parcel
from app.repositories.base_repository import BaseRepository
from app.schemas.parish_schema import ParishCreate, ParishUpdate


class ParishRepository(BaseRepository[Parish, ParishCreate, ParishUpdate]):
    """
    Repository for Parish entity with extended functionality.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize parish repository.
        
        Args:
            db: Async database session
        """
        super().__init__(Parish, db)
    
    async def get_with_parcel_count(self, id: str) -> Optional[Parish]:
        """
        Get a parish with its cached parcel count.
        
        Args:
            id: UUID of the parish
            
        Returns:
            Parish instance with parcel_count field, None if not found
        """
        return await self.get(id)
    
    async def list_active(self) -> List[Parish]:
        """
        List all active parishes.
        
        Returns:
            List of active parish instances
        """
        return await self.list(filters={"is_active": True})
    
    async def get_by_code(self, code: str) -> Optional[Parish]:
        """
        Get parish by unique code.
        
        Args:
            code: Parish code (e.g., "PAR-001")
            
        Returns:
            Parish instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Parish).where(
                Parish.code == code,
                Parish.is_active
            )
        )
        return result.scalar_one_or_none()
    
    async def update_parcel_count(self, id: str) -> Optional[Parish]:
        """
        Update the cached parcel count for a parish.
        
        Args:
            id: UUID of the parish
            
        Returns:
            Updated parish instance, None if not found
        """
        # Get count of active parcels in this parish
        result = await self.db.execute(
            select(func.count()).select_from(Parcel).where(
                Parcel.parish_id == id,
                Parcel.is_active
            )
        )
        count = result.scalar_one()
        
        # Update parish
        parish = await self.get(id)
        if parish:
            parish.parcel_count = count
            await self.db.flush()
            await self.db.refresh(parish)
        
        return parish
    
    async def search_by_name(self, name: str, limit: int = 20) -> List[Parish]:
        """
        Search parishes by name (partial match).
        
        Args:
            name: Search string for parish name
            limit: Maximum number of results
            
        Returns:
            List of matching parishes
        """
        result = await self.db.execute(
            select(Parish).where(
                Parish.name.contains(name),
                Parish.is_active
            ).limit(limit)
        )
        return list(result.scalars().all())

    async def find_by_point(self, longitude: float, latitude: float) -> Optional[Parish]:
        """
        Find the parish containing a specific geographic point.
        
        Args:
            longitude: Longitude in WGS84
            latitude: Latitude in WGS84
            
        Returns:
            Parish containing the point, or None if not found
        """
        result = await self.db.execute(
            select(Parish).where(
                func.ST_Contains(
                    Parish.boundary_wkb,
                    func.ST_GeomFromText(f"POINT({longitude} {latitude})", 4326)
                ),
                Parish.is_active
            )
        )
        return result.scalar_one_or_none()# app/repositories/parish_repository.py
