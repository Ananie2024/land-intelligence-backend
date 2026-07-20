"""
Parish Repository
Phase 2 — Section 3.2
Land Intelligence System
"""

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parish import Parish
from app.repositories.base_repository import BaseRepository
from app.schemas.parish_schema import ParishCreate, ParishUpdate


class ParishRepository(BaseRepository[Parish, ParishCreate, ParishUpdate]):
    """
    Repository for Parish entity with extended functionality.
    Simplified to only manage parish name.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize parish repository.
        
        Args:
            db: Async database session
        """
        super().__init__(Parish, db)
    
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
    
    async def update_parcel_count(self, parish_id: str) -> None:
        """
        Update parcel count for a parish.
        
        Note: This method is kept for backward compatibility with ParcelService.
        The parcel_count column was removed in the parish simplification migration,
        so this is now a no-op method. Parcel counts should be computed dynamically.
        
        Args:
            parish_id: UUID of the parish (unused)
        """
        # No-op - parcel_count was removed in simplify_parish_entity migration
        pass
