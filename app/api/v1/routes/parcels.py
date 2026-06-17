# app/api/v1/routes/parcels.py

"""
Parcel Routes
Phase 3 — Section 4.2
Land Intelligence System
"""

import math
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id
from app.repositories.parcel_repository import ParcelRepository
from app.repositories.parish_repository import ParishRepository
from app.schemas.parcel_schema import (
    ParcelCreate,
    ParcelUpdate,
    ParcelResponse,
    ParcelListResponse,
    ParcelSearchParams,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /parcels/  — paginated list with rich filtering
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=ParcelListResponse,
    summary="List parcels",
    description="Return a paginated, filterable list of all active parcels.",
)
async def list_parcels(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    parish_id: Optional[str] = Query(None, description="Filter by parish UUID"),
    land_use_category_id: Optional[str] = Query(None, description="Filter by land use category UUID"),
    owner_name: Optional[str] = Query(None, description="Partial match on owner name"),
    parcel_number: Optional[str] = Query(None, description="Partial match on parcel number"),
    min_area_sqm: Optional[float] = Query(None, ge=0, description="Minimum area in m²"),
    max_area_sqm: Optional[float] = Query(None, ge=0, description="Maximum area in m²"),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    repo = ParcelRepository(db)
    skip = (page - 1) * size

    any_filter = any([
        owner_name, parcel_number, parish_id,
        land_use_category_id, min_area_sqm, max_area_sqm,
    ])

    if any_filter:
        items = await repo.search(
            owner_name=owner_name,
            parcel_number=parcel_number,
            parish_id=parish_id,
            land_use_category_id=land_use_category_id,
            min_area_sqm=min_area_sqm,
            max_area_sqm=max_area_sqm,
            skip=skip,
            limit=size,
        )
        # Count with same filters for accurate pagination
        total = await repo.count(filters={
            k: v for k, v in {
                "parish_id": parish_id,
                "land_use_category_id": land_use_category_id,
            }.items() if v is not None
        })
    else:
        total = await repo.count()
        items = await repo.list(skip=skip, limit=size, order_by="created_at", descending=True)

    return ParcelListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=max(1, math.ceil(total / size)),
    )


# ---------------------------------------------------------------------------
# POST /parcels/  — create a new parcel
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=ParcelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create parcel",
    description="Register a new land parcel. Parcel number must be unique. Parish must exist.",
)
async def create_parcel(
    payload: ParcelCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    parcel_repo = ParcelRepository(db)
    parish_repo = ParishRepository(db)

    # Validate parish exists
    parish = await parish_repo.get(payload.parish_id)
    if not parish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parish '{payload.parish_id}' not found.",
        )

    # Enforce unique parcel number
    existing = await parcel_repo.get_by_parcel_number(payload.parcel_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Parcel number '{payload.parcel_number}' already exists.",
        )

    # Enforce unique title deed if provided
    if payload.title_deed_number:
        deed_conflict = await parcel_repo.get_by_title_deed(payload.title_deed_number)
        if deed_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Title deed '{payload.title_deed_number}' is already registered.",
            )

    parcel = await parcel_repo.create(payload)

    # Keep parish parcel count in sync
    await parish_repo.update_parcel_count(payload.parish_id)

    await db.commit()
    await db.refresh(parcel)

    logger.info(f"Parcel created: {parcel.id} in parish {payload.parish_id} by user {user_id}")
    return parcel


# ---------------------------------------------------------------------------
# GET /parcels/{parcel_id}  — fetch single parcel
# ---------------------------------------------------------------------------

@router.get(
    "/{parcel_id}",
    response_model=ParcelResponse,
    summary="Get parcel",
    description="Retrieve a single parcel by its UUID.",
)
async def get_parcel(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    repo = ParcelRepository(db)
    parcel = await repo.get(parcel_id)

    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parcel '{parcel_id}' not found.",
        )

    return parcel


# ---------------------------------------------------------------------------
# GET /parcels/by-number/{parcel_number}  — lookup by business key
# ---------------------------------------------------------------------------

@router.get(
    "/by-number/{parcel_number}",
    response_model=ParcelResponse,
    summary="Get parcel by number",
    description="Look up a parcel using its unique parcel number (e.g. 'P-2024-001').",
)
async def get_parcel_by_number(
    parcel_number: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    repo = ParcelRepository(db)
    parcel = await repo.get_by_parcel_number(parcel_number)

    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parcel number '{parcel_number}' not found.",
        )

    return parcel


# ---------------------------------------------------------------------------
# GET /parcels/by-deed/{title_deed_number}  — lookup by title deed
# ---------------------------------------------------------------------------

@router.get(
    "/by-deed/{title_deed_number}",
    response_model=ParcelResponse,
    summary="Get parcel by title deed",
    description="Look up a parcel using its official title deed number.",
)
async def get_parcel_by_deed(
    title_deed_number: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    repo = ParcelRepository(db)
    parcel = await repo.get_by_title_deed(title_deed_number)

    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Title deed '{title_deed_number}' not found.",
        )

    return parcel


# ---------------------------------------------------------------------------
# GET /parcels/parish/{parish_id}  — all parcels in a parish
# ---------------------------------------------------------------------------

@router.get(
    "/parish/{parish_id}",
    response_model=ParcelListResponse,
    summary="List parcels by parish",
    description="Return all active parcels belonging to a specific parish.",
)
async def list_parcels_by_parish(
    parish_id: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    parcel_repo = ParcelRepository(db)
    parish_repo = ParishRepository(db)

    # Validate parish exists
    parish = await parish_repo.get(parish_id)
    if not parish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parish '{parish_id}' not found.",
        )

    skip = (page - 1) * size
    items = await parcel_repo.get_by_parish(parish_id, skip=skip, limit=size)
    total = await parcel_repo.count_by_parish(parish_id)

    return ParcelListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=max(1, math.ceil(total / size)),
    )


# ---------------------------------------------------------------------------
# PATCH /parcels/{parcel_id}  — partial update
# ---------------------------------------------------------------------------

@router.patch(
    "/{parcel_id}",
    response_model=ParcelResponse,
    summary="Update parcel",
    description="Partially update a parcel. Uniqueness constraints on parcel_number and title_deed_number are enforced.",
)
async def update_parcel(
    parcel_id: str,
    payload: ParcelUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    repo = ParcelRepository(db)

    # Check parcel number uniqueness if being changed
    if payload.parcel_number is not None:
        conflict = await repo.get_by_parcel_number(payload.parcel_number)
        if conflict and conflict.id != parcel_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Parcel number '{payload.parcel_number}' is already in use.",
            )

    # Check title deed uniqueness if being changed
    if payload.title_deed_number is not None:
        conflict = await repo.get_by_title_deed(payload.title_deed_number)
        if conflict and conflict.id != parcel_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Title deed '{payload.title_deed_number}' is already registered.",
            )

    parcel = await repo.update(parcel_id, payload)

    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parcel '{parcel_id}' not found.",
        )

    await db.commit()
    await db.refresh(parcel)

    logger.info(f"Parcel updated: {parcel_id} by user {user_id}")
    return parcel


# ---------------------------------------------------------------------------
# DELETE /parcels/{parcel_id}  — soft delete
# ---------------------------------------------------------------------------

@router.delete(
    "/{parcel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete parcel",
    description="Soft-delete a parcel. The parish parcel count is updated automatically.",
)
async def delete_parcel(
    parcel_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    parcel_repo = ParcelRepository(db)
    parish_repo = ParishRepository(db)

    # Fetch first so we have the parish_id for count update
    parcel = await parcel_repo.get(parcel_id)
    if not parcel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parcel '{parcel_id}' not found.",
        )

    parish_id = parcel.parish_id
    await parcel_repo.soft_delete(parcel_id)
    await parish_repo.update_parcel_count(parish_id)

    await db.commit()
    logger.info(f"Parcel soft-deleted: {parcel_id} by user {user_id}")