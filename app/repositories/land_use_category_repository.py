"""
Land Use Category Repository
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.land_use_category import LandUseCategory
from app.repositories.base_repository import BaseRepository
from app.schemas.land_use_category_schema import LandUseCategoryCreate, LandUseCategoryUpdate


class LandUseCategoryRepository(BaseRepository[LandUseCategory, LandUseCategoryCreate, LandUseCategoryUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(LandUseCategory, db)

    async def get_by_code(self, code: str) -> Optional[LandUseCategory]:
        result = await self.db.execute(
            select(LandUseCategory).where(
                LandUseCategory.code == code,
                LandUseCategory.is_active
            )
        )
        return result.scalar_one_or_none()

    async def get(self, id: str) -> Optional[LandUseCategory]:
        return await self.get_by_id(id)
