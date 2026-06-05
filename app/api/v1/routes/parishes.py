# app/api/v1/routes/parishes.py

"""
Parish Routes
Phase 3 — Section 4.1
Land Intelligence System
"""

import math
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.middleware.authentication import get_current_user_id
from app.repositories.parish_repository import ParishRepository
from app.schemas.parish_schema import (
    ParishCreate,
    ParishUpdate,
    ParishResponse,
    ParishListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /parishes/  — paginated list with optional name search
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=ParishListResponse,
    summary="List parishes",
    description="Return a paginated list of all active parishes, with optional name search.",
)
async def list_parishes(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Search by parish name (partial match)"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    repo = ParishRepository(db)

    if name:
        items = await repo.search_by_name(name, limit=size)
        total = len(items)
        # Apply manual offset for searched results
        start = (page - 1) * size
        items = items[start: start + size]
    else:
        skip = (page - 1) * size
        total = await repo.count()
        items = await repo.list(skip=skip, limit=size, order_by="name")

    return ParishListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=max(1, math.ceil(total / size)),
    )


# ---------------------------------------------------------------------------
# POST /parishes/  — create a new parish
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=ParishResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create parish",
    description="Create a new parish. Parish code must be unique.",
)
async def create_parish(
    payload: ParishCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = ParishRepository(db)

    # Enforce unique code
    existing = await repo.get_by_code(payload.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Parish with code '{payload.code}' already exists.",
        )

    parish = await repo.create(payload)
    await db.commit()
    await db.refresh(parish)

    logger.info(f"Parish created: {parish.id} by user {user_id}")
    return parish


# ---------------------------------------------------------------------------
# GET /parishes/{parish_id}  — fetch single parish
# ---------------------------------------------------------------------------

@router.get(
    "/{parish_id}",
    response_model=ParishResponse,
    summary="Get parish",
    description="Retrieve a single parish by its UUID.",
)
async def get_parish(
    parish_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    repo = ParishRepository(db)
    parish = await repo.get_with_parcel_count(parish_id)

    if not parish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parish '{parish_id}' not found.",
        )

    return parish


# ---------------------------------------------------------------------------
# PATCH /parishes/{parish_id}  — partial update
# ---------------------------------------------------------------------------

@router.patch(
    "/{parish_id}",
    response_model=ParishResponse,
    summary="Update parish",
    description="Partially update a parish. Only provided fields are changed.",
)
async def update_parish(
    parish_id: str,
    payload: ParishUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = ParishRepository(db)

    # If code is being changed, check it isn't already taken
    if payload.code is not None:
        existing = await repo.get_by_code(payload.code)
        if existing and existing.id != parish_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Parish code '{payload.code}' is already in use.",
            )

    parish = await repo.update(parish_id, payload)

    if not parish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parish '{parish_id}' not found.",
        )

    await db.commit()
    await db.refresh(parish)

    logger.info(f"Parish updated: {parish_id} by user {user_id}")
    return parish


# ---------------------------------------------------------------------------
# DELETE /parishes/{parish_id}  — soft delete
# ---------------------------------------------------------------------------

@router.delete(
    "/{parish_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete parish",
    description="Soft-delete a parish (sets is_active=False). Parcels are not removed.",
)
async def delete_parish(
    parish_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = ParishRepository(db)
    deleted = await repo.soft_delete(parish_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parish '{parish_id}' not found.",
        )

    await db.commit()
    logger.info(f"Parish soft-deleted: {parish_id} by user {user_id}")


# ---------------------------------------------------------------------------
# POST /parishes/{parish_id}/refresh-count  — sync cached parcel count
# ---------------------------------------------------------------------------

@router.post(
    "/{parish_id}/refresh-count",
    response_model=ParishResponse,
    summary="Refresh parcel count",
    description="Recalculate and update the cached parcel count for a parish.",
)
async def refresh_parcel_count(
    parish_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = ParishRepository(db)
    parish = await repo.update_parcel_count(parish_id)

    if not parish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parish '{parish_id}' not found.",
        )

    await db.commit()
    await db.refresh(parish)

    logger.info(f"Parish parcel count refreshed: {parish_id} by user {user_id}")
    return parish