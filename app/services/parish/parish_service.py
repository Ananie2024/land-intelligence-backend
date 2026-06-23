# app/services/parish/parish_service.py
"""
Parish Service
Phase 3 — Section 4.1
Land Intelligence System
"""

import math
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parish import Parish
from app.repositories.parish_repository import ParishRepository
from app.schemas.parish_schema import ParishCreate, ParishUpdate, ParishListResponse

logger = logging.getLogger(__name__)


class ParishService:
    """
    Business logic layer for parish operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ParishRepository(db)

    async def list_parishes(
        self,
        page: int = 1,
        size: int = 20,
        name: Optional[str] = None,
    ) -> ParishListResponse:
        """
        Return a paginated list of all active parishes, with optional name search.
        """
        if name:
            items = await self.repo.search_by_name(name, limit=size)
            total = len(items)
            start = (page - 1) * size
            items = items[start: start + size]
        else:
            skip = (page - 1) * size
            total = await self.repo.count()
            items = await self.repo.list(skip=skip, limit=size, order_by="name")

        return ParishListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=max(1, math.ceil(total / size)),
        )

    async def create_parish(self, payload: ParishCreate, user_id: str) -> Parish:
        """
        Create a new parish. Enforces unique code constraint.
        """
        existing = await self.repo.get_by_code(payload.code)
        if existing:
            raise ValueError(f"Parish with code '{payload.code}' already exists.")

        parish = await self.repo.create(payload)
        await self.db.commit()
        await self.db.refresh(parish)

        logger.info(f"Parish created: {parish.id} by user {user_id}")
        return parish

    async def get_parish(self, parish_id: str) -> Optional[Parish]:
        """
        Retrieve a single parish by its UUID.
        """
        return await self.repo.get_with_parcel_count(parish_id)

    async def update_parish(self, parish_id: str, payload: ParishUpdate, user_id: str) -> Optional[Parish]:
        """
        Partially update a parish. Enforces unique code if changed.
        """
        if payload.code is not None:
            existing = await self.repo.get_by_code(payload.code)
            if existing is not None and existing.id != parish_id:
                raise ValueError(f"Parish code '{payload.code}' is already in use.")

        parish = await self.repo.update(parish_id, payload)

        if parish is None:
            return None

        await self.db.commit()
        await self.db.refresh(parish)

        logger.info(f"Parish updated: {parish_id} by user {user_id}")
        return parish

    async def delete_parish(self, parish_id: str, user_id: str) -> bool:
        """
        Soft-delete a parish.
        """
        deleted = await self.repo.soft_delete(parish_id)

        if deleted is False:
            return False

        await self.db.commit()
        logger.info(f"Parish soft-deleted: {parish_id} by user {user_id}")
        return True

    async def refresh_parcel_count(self, parish_id: str, user_id: str) -> Optional[Parish]:
        """
        Recalculate and update the cached parcel count for a parish.
        """
        parish = await self.repo.update_parcel_count(parish_id)

        if not parish:
            return None

        await self.db.commit()
        await self.db.refresh(parish)

        logger.info(f"Parish parcel count refreshed: {parish_id} by user {user_id}")
        return parish