# app/repositories/parcel_repository.py
"""
Parcel Repository
Phase 2 — Section 3.2
Land Intelligence System
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parcel import Parcel
from app.repositories.base_repository import BaseRepository
from app.schemas.parcel_schema import ParcelCreate, ParcelUpdate


class ParcelRepository(BaseRepository[Parcel, ParcelCreate, ParcelUpdate]):
    """
    Repository for Parcel entity with extended functionality.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize parcel repository.
        
        Args:
            db: Async database session
        """
        super().__init__(Parcel, db)
    
    async def get_by_parish(self, parish_id: str, skip: int = 0, limit: int = 100) -> List[Parcel]:
        """
        Get all parcels belonging to a parish.
        
        Args:
            parish_id: UUID of the parish
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of parcel instances
        """
        return await self.list(
            filters={"parish_id": parish_id},
            skip=skip,
            limit=limit
        )
    
    async def list_by_land_use(self, category_id: str, skip: int = 0, limit: int = 100) -> List[Parcel]:
        """
        Get all parcels by land use category.
        
        Args:
            category_id: UUID of land use category
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of parcel instances
        """
        return await self.list(
            filters={"land_use_category_id": category_id},
            skip=skip,
            limit=limit
        )
    
    async def search_by_geometry(self, geometry_wkb: str) -> List[Parcel]:
        """
        Search parcels by geometry using PostGIS spatial intersection.
        
        Args:
            geometry_wkb: WKB hex string for comparison
            
        Returns:
            List of parcels intersecting the provided geometry
        """
        from sqlalchemy import func
        
        # We use ST_GeomFromText if it was WKT, but for WKB we can use ST_GeomFromWKB
        # GeoAlchemy2's functions work well here
        result = await self.db.execute(
            select(Parcel).where(
                func.ST_Intersects(
                    Parcel.geometry_wkb,
                    func.ST_GeomFromWKB(func.unhex(geometry_wkb), 4326)
                ),
                Parcel.is_active
            )
        )
        return list(result.scalars().all())
    
    async def get_by_parcel_number(self, parcel_number: str) -> Optional[Parcel]:
        """
        Get parcel by unique parcel number.
        
        Args:
            parcel_number: Unique parcel identifier
            
        Returns:
            Parcel instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Parcel).where(
                Parcel.parcel_number == parcel_number,
                Parcel.is_active
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_title_deed(self, title_deed_number: str) -> Optional[Parcel]:
        """
        Get parcel by title deed number.
        
        Args:
            title_deed_number: Official title deed reference
            
        Returns:
            Parcel instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Parcel).where(
                Parcel.title_deed_number == title_deed_number,
                Parcel.is_active
            )
        )
        return result.scalar_one_or_none()
    
    async def search(
        self,
        owner_name: Optional[str] = None,
        parcel_number: Optional[str] = None,
        parish_id: Optional[str] = None,
        land_use_category_id: Optional[str] = None,
        min_area_sqm: Optional[float] = None,
        max_area_sqm: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Parcel]:
        """
        Advanced search with multiple filters.
        
        Args:
            owner_name: Filter by owner name (partial match)
            parcel_number: Filter by parcel number (partial match)
            parish_id: Filter by parish
            land_use_category_id: Filter by land use category
            min_area_sqm: Minimum area in square meters
            max_area_sqm: Maximum area in square meters
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching parcel instances
        """
        query = select(Parcel).where(Parcel.is_active)
        
        if owner_name:
            query = query.where(Parcel.owner_name.contains(owner_name))
        
        if parcel_number:
            query = query.where(Parcel.parcel_number.contains(parcel_number))
        
        if parish_id:
            query = query.where(Parcel.parish_id == parish_id)
        
        if land_use_category_id:
            query = query.where(Parcel.land_use_category_id == land_use_category_id)
        
        if min_area_sqm is not None:
            query = query.where(Parcel.area_sqm >= min_area_sqm)
        
        if max_area_sqm is not None:
            query = query.where(Parcel.area_sqm <= max_area_sqm)
        
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_by_parish(self, parish_id: str) -> int:
        """
        Count parcels in a parish.
        
        Args:
            parish_id: UUID of the parish
            
        Returns:
            Count of active parcels
        """
        return await self.count(filters={"parish_id": parish_id})

    async def get_total_area_by_parish(self, parish_id: str) -> float:
        """
        Calculate total area of all parcels in a parish using native spatial functions.
        
        
        Args:
            parish_id: UUID of the parish
            
        Returns:
            Total area in square meters
        """
        from sqlalchemy import func
        result = await self.db.execute(
            select(func.sum(func.ST_Area(Parcel.geometry_wkb))).where(
                Parcel.parish_id == parish_id,
                Parcel.is_active
            )
        )
        return result.scalar() or 0.0