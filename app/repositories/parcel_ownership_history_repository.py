# app/repositories/parcel_ownership_history_repository.py
"""
Parcel Ownership History Repository
Land Intelligence System
"""

from typing import Optional, List
from datetime import date
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.parcel_ownership_history import ParcelOwnershipHistory
from app.repositories.base_repository import BaseRepository


class ParcelOwnershipHistoryRepository(BaseRepository[ParcelOwnershipHistory, None, None]):
    """
    Repository for ParcelOwnershipHistory entity.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(ParcelOwnershipHistory, db)

    async def list_by_parcel(self, parcel_id: str, skip: int = 0, limit: int = 100) -> List[ParcelOwnershipHistory]:
        """List ownership history entries for a parcel (most recent first)."""
        query = (
            select(ParcelOwnershipHistory)
            .where(ParcelOwnershipHistory.parcel_id == parcel_id)
            .order_by(desc(ParcelOwnershipHistory.transfer_date), desc(ParcelOwnershipHistory.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def add_entry(self, parcel_id: str, owner_name: str, transfer_date: date, **kwargs) -> ParcelOwnershipHistory:
        """Create a new ownership history record."""
        data = {
            "parcel_id": parcel_id,
            "owner_name": owner_name,
            "transfer_date": transfer_date,
        }
        data.update(kwargs)
        return await self.create_by_dict(data)