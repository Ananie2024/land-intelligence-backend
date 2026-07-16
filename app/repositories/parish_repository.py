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