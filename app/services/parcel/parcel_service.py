# app/services/parcel/parcel_service.py
"""
Parcel Service
Phase 3 — Section 4.2
Land Intelligence System
"""

import math
import logging
from datetime import datetime, date, timezone
from typing import Optional, List, Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parcel import Parcel
from app.models.parcel_ownership_history import ParcelOwnershipHistory
from app.repositories.parcel_repository import ParcelRepository
from app.repositories.parish_repository import ParishRepository
from app.repositories.parcel_ownership_history_repository import ParcelOwnershipHistoryRepository
from app.schemas.parcel_schema import (
    ParcelCreate,
    ParcelUpdate,
    ParcelListResponse,
)

logger = logging.getLogger(__name__)


class ParcelService:
    """
    Business logic layer for parcel operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.parcel_repo = ParcelRepository(db)
        self.parish_repo = ParishRepository(db)
        self.ownership_repo = ParcelOwnershipHistoryRepository(db)

    async def _audit(self, action: str, record_id: str, user_id: str, old_value: Optional[Dict] = None, new_value: Optional[Dict] = None):
        """Write an audit log entry for parcel changes."""
        from app.models.audit_log import AuditLog
        entry = AuditLog(
            table_name="parcels",
            record_id=record_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            performed_by=user_id,
            performed_at=datetime.now(timezone.utc),
        )
        self.db.add(entry)

    async def list_parcels(
        self,
        page: int = 1,
        size: int = 20,
        filters: Optional[dict] = None,
    ) -> ParcelListResponse:
        """
        Return a paginated, filterable list of all active parcels.
        """
        skip = (page - 1) * size
        any_filter = filters is not None and len(filters) > 0

        if any_filter:
            items = await self.parcel_repo.search(
                owner_name=filters.get("owner_name"),
                parcel_number=filters.get("parcel_number"),
                parish_id=filters.get("parish_id"),
                land_use_category_id=filters.get("land_use_category_id"),
                min_area_sqm=filters.get("min_area_sqm"),
                max_area_sqm=filters.get("max_area_sqm"),
                skip=skip,
                limit=size,
            )
            total = await self.parcel_repo.count(filters={
                k: v for k, v in {
                    "parish_id": filters.get("parish_id"),
                    "land_use_category_id": filters.get("land_use_category_id"),
                }.items() if v is not None
            })
        else:
            total = await self.parcel_repo.count()
            items = await self.parcel_repo.list(skip=skip, limit=size, order_by="created_at", descending=True)

        return ParcelListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=max(1, math.ceil(total / size)),
        )

    async def create_parcel(self, payload: ParcelCreate, user_id: str) -> Parcel:
        """
        Register a new land parcel. Validates parish exists and enforces uniqueness constraints.
        Also creates initial ownership history entry.
        """
        parish = await self.parish_repo.get(payload.parish_id)
        if not parish:
            raise ValueError(f"Parish '{payload.parish_id}' not found.")

        existing = await self.parcel_repo.get_by_parcel_number(payload.parcel_number)
        if existing:
            raise ValueError(f"Parcel number '{payload.parcel_number}' already exists.")

        if payload.title_deed_number:
            deed_conflict = await self.parcel_repo.get_by_title_deed(payload.title_deed_number)
            if deed_conflict:
                raise ValueError(f"Title deed '{payload.title_deed_number}' is already registered.")

        parcel = await self.parcel_repo.create(payload)

        # Initial ownership record
        await self.ownership_repo.add_entry(
            parcel_id=str(parcel.id),
            owner_name=payload.owner_name,
            owner_contact=payload.owner_contact,
            transfer_date=date.today(),
            document_reference=payload.title_deed_number,
            notes="Initial ownership record on parcel creation",
        )

        await self.parish_repo.update_parcel_count(str(payload.parish_id))
        await self.db.commit()
        await self.db.refresh(parcel)

        await self._audit("CREATE", str(parcel.id), user_id, new_value={"parcel_number": payload.parcel_number, "parish_id": payload.parish_id, "owner_name": payload.owner_name, "area_sqm": payload.area_sqm})
        logger.info(f"Parcel created: {parcel.id} in parish {payload.parish_id} by user {user_id}")
        return parcel

    async def get_parcel(self, parcel_id: str) -> Optional[Parcel]:
        """
        Retrieve a single parcel by its UUID.
        """
        return await self.parcel_repo.get(parcel_id)

    async def get_parcel_by_number(self, parcel_number: str) -> Optional[Parcel]:
        """
        Look up a parcel using its unique parcel number.
        """
        return await self.parcel_repo.get_by_parcel_number(parcel_number)

    async def get_parcel_by_deed(self, title_deed_number: str) -> Optional[Parcel]:
        """
        Look up a parcel using its official title deed number.
        """
        return await self.parcel_repo.get_by_title_deed(title_deed_number)

    async def list_parcels_by_parish(
        self,
        parish_id: str,
        page: int = 1,
        size: int = 20,
    ) -> ParcelListResponse:
        """
        Return all active parcels belonging to a specific parish.
        """
        parish = await self.parish_repo.get(parish_id)
        if not parish:
            raise ValueError(f"Parish '{parish_id}' not found.")

        skip = (page - 1) * size
        items = await self.parcel_repo.get_by_parish(parish_id, skip=skip, limit=size)
        total = await self.parcel_repo.count_by_parish(parish_id)

        return ParcelListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=max(1, math.ceil(total / size)),
        )

    async def update_parcel(self, parcel_id: str, payload: ParcelUpdate, user_id: str) -> Optional[Parcel]:
        """
        Partially update a parcel. Enforces uniqueness constraints.
        Tracks ownership changes in history if owner_name changes.
        """
        parcel = await self.parcel_repo.get(parcel_id)
        if not parcel:
            return None

        if payload.parcel_number is not None:
            conflict = await self.parcel_repo.get_by_parcel_number(payload.parcel_number)
            if conflict and conflict.id != parcel_id:
                raise ValueError(f"Parcel number '{payload.parcel_number}' is already in use.")

        if payload.title_deed_number is not None:
            conflict = await self.parcel_repo.get_by_title_deed(payload.title_deed_number)
            if conflict and conflict.id != parcel_id:
                raise ValueError(f"Title deed '{payload.title_deed_number}' is already registered.")

        old_owner_name = str(parcel.owner_name)
        old_owner_contact = str(parcel.owner_contact) if parcel.owner_contact else None

        parcel = await self.parcel_repo.update(parcel_id, payload)
        if not parcel:
            return None

        new_owner_name = str(parcel.owner_name)
        new_owner_contact = str(parcel.owner_contact) if parcel.owner_contact else None

        if (payload.owner_name is not None and new_owner_name != old_owner_name) or (
            payload.owner_contact is not None and new_owner_contact != old_owner_contact
        ):
            await self.ownership_repo.add_entry(
                parcel_id=parcel_id,
                owner_name=new_owner_name,
                owner_contact=new_owner_contact,
                transfer_date=date.today(),
                document_reference=payload.title_deed_number if payload.title_deed_number is not None else str(parcel.title_deed_number),
                notes="Ownership updated",
            )

        await self.db.commit()
        await self.db.refresh(parcel)

        await self._audit("UPDATE", parcel_id, user_id, old_value={"owner_name": old_owner_name} if payload.owner_name else None, new_value={"owner_name": new_owner_name} if payload.owner_name else None)
        logger.info(f"Parcel updated: {parcel_id} by user {user_id}")
        return parcel

    async def delete_parcel(self, parcel_id: str, user_id: str) -> bool:
        """Soft-delete a parcel. Ownership history preserves pre-delete owner state."""
        parcel = await self.parcel_repo.get(parcel_id)
        if not parcel:
            return False

        parish_id = parcel.parish_id
        await self.parcel_repo.soft_delete(parcel_id)
        await self.parish_repo.update_parcel_count(str(parish_id))
        await self.db.commit()

        await self._audit("SOFT_DELETE", parcel_id, user_id, old_value={"is_active": True}, new_value={"is_active": False})
        logger.info(f"Parcel soft-deleted: {parcel_id} by user {user_id}")
        return True

    async def get_ownership_history(self, parcel_id: str, skip: int = 0, limit: int = 100) -> list[ParcelOwnershipHistory]:
        """Return ownership history for a parcel."""
        return await self.ownership_repo.list_by_parcel(parcel_id, skip=skip, limit=limit)