# app/api/v1/routes/physical_locations.py
"""
Physical Locations & Cabinets API Routes
Phase 2 — Section 3.2
Land Intelligence System
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_id
from app.repositories.location_repository import LocationRepository
from app.services.location.physical_finder import PhysicalFinder
from app.services.location.storage_mapper import StorageMapper
from app.services.location.location_validator import LocationValidator
from app.schemas.physical_location_schema import (
    PhysicalLocationCreate,
    PhysicalLocationUpdate,
    PhysicalLocationResponse,
    StorageCabinetCreate,
    StorageCabinetUpdate,
    StorageCabinetResponse,
    PhysicalLocationFinderRequest,
    PhysicalLocationFinderResponse,
)
from app.models.physical_location import PhysicalLocation
from app.models.storage_cabinet import StorageCabinet

logger = logging.getLogger(__name__)

router = APIRouter()

# ---------------------------------------------------------------------------
# Location Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=PhysicalLocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create physical location",
    description="Register a new physical archive room, warehouse, or shelf location."
)
async def create_location(
    payload: PhysicalLocationCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        # Validate unique location code
        repo = LocationRepository(db)
        existing = await db.execute(
            select(PhysicalLocation).where(
                PhysicalLocation.location_code == payload.location_code,
                PhysicalLocation.is_active
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Location code '{payload.location_code}' is already registered."
            )
            
        # Code format validation
        if not LocationValidator.validate_location_code(payload.location_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Location code must contain only alphanumeric characters, dashes, or underscores."
            )
            
        location = await repo.create(payload)
        await db.commit()
        await db.refresh(location)
        
        logger.info(f"Physical location created: {location.id} (code: {payload.location_code}) by user {user_id}")
        return location
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating location: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register physical location."
        )


@router.get(
    "/",
    response_model=List[PhysicalLocationResponse],
    summary="List physical locations",
    description="List active physical archive locations."
)
async def list_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        repo = LocationRepository(db)
        return await repo.list(skip=skip, limit=limit, order_by="location_code")
    except Exception as e:
        logger.error(f"Error listing locations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve physical locations."
        )


@router.get(
    "/{location_id}",
    response_model=PhysicalLocationResponse,
    summary="Get physical location",
    description="Fetch details of a single physical location by UUID."
)
async def get_location(
    location_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        repo = LocationRepository(db)
        location = await repo.get(location_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID '{location_id}' not found."
            )
        return location
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve physical location."
        )


@router.patch(
    "/{location_id}",
    response_model=PhysicalLocationResponse,
    summary="Update physical location",
    description="Partially update physical location parameters."
)
async def update_location(
    location_id: str,
    payload: PhysicalLocationUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        repo = LocationRepository(db)
        
        # Verify location code uniqueness if modified
        if payload.location_code is not None:
            existing = await db.execute(
                select(PhysicalLocation).where(
                    PhysicalLocation.location_code == payload.location_code,
                    PhysicalLocation.is_active
                )
            )
            conflict = existing.scalar_one_or_none()
            if conflict and str(conflict.id) != location_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Location code '{payload.location_code}' is already registered."
                )
                
            if not LocationValidator.validate_location_code(payload.location_code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Location code must contain only alphanumeric characters, dashes, or underscores."
                )
                
        location = await repo.update(location_id, payload)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID '{location_id}' not found."
            )
            
        await db.commit()
        await db.refresh(location)
        
        logger.info(f"Physical location updated: {location_id} by user {user_id}")
        return location
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update physical location."
        )


@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete physical location",
    description="Soft-delete a physical location. Cascading constraints apply."
)
async def delete_location(
    location_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        repo = LocationRepository(db)
        location = await repo.get(location_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID '{location_id}' not found."
            )
            
        await repo.soft_delete(location_id)
        await db.commit()
        
        logger.info(f"Physical location deleted: {location_id} by user {user_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting location: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete location."
        )


# ---------------------------------------------------------------------------
# Search and Finder Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/find",
    response_model=PhysicalLocationFinderResponse,
    summary="Locate archive document",
    description="Resolve and locate the physical storage coordinates of a document or parcel."
)
async def locate_document(
    payload: PhysicalLocationFinderRequest,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        finder = PhysicalFinder(db)
        res = await finder.find_location(
            parcel_id=payload.parcel_id,
            document_id=payload.document_id,
            reference_number=payload.reference_number
        )
        return res
    except Exception as e:
        logger.error(f"Error finding physical document location: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal search resolution failed."
        )


# ---------------------------------------------------------------------------
# Cabinet Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/cabinets",
    response_model=StorageCabinetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create cabinet",
    description="Create a storage cabinet under an existing physical location."
)
async def create_cabinet(
    payload: StorageCabinetCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        repo = LocationRepository(db)
        
        # Verify location exists
        location = await repo.get(payload.physical_location_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Physical location '{payload.physical_location_id}' not found."
            )
            
        # Create cabinet
        data = payload.model_dump(exclude_none=True)
        cabinet = StorageCabinet(**data)
        db.add(cabinet)
        await db.flush()
        await db.commit()
        await db.refresh(cabinet)
        
        logger.info(f"Storage cabinet created: {cabinet.id} in location {payload.physical_location_id} by user {user_id}")
        return cabinet
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating storage cabinet: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register storage cabinet."
        )


@router.get(
    "/cabinets/{cabinet_id}",
    response_model=StorageCabinetResponse,
    summary="Get cabinet detail",
    description="Retrieve details of a storage cabinet by UUID."
)
async def get_cabinet(
    cabinet_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        repo = LocationRepository(db)
        cabinet = await repo.get_cabinet(cabinet_id)
        if not cabinet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Storage cabinet '{cabinet_id}' not found."
            )
        return cabinet
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting storage cabinet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve storage cabinet."
        )


@router.patch(
    "/cabinets/{cabinet_id}",
    response_model=StorageCabinetResponse,
    summary="Update cabinet details",
    description="Partially update a cabinet (capacity, location reference, count, coordinates)."
)
async def update_cabinet(
    cabinet_id: str,
    payload: StorageCabinetUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    try:
        repo = LocationRepository(db)
        cabinet = await repo.get_cabinet(cabinet_id)
        if not cabinet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cabinet '{cabinet_id}' not found."
            )
            
        if payload.physical_location_id is not None:
            location = await repo.get(payload.physical_location_id)
            if not location:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Physical location '{payload.physical_location_id}' not found."
                )
                
        # Validate current count is not exceeding max capacity
        if payload.current_count is not None or payload.max_capacity is not None:
            new_count = payload.current_count if payload.current_count is not None else cabinet.current_count
            new_max = payload.max_capacity if payload.max_capacity is not None else cabinet.max_capacity
            if new_max is not None and new_count > new_max:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"New count {new_count} cannot exceed cabinet max capacity {new_max}."
                )
                
        # Apply changes
        data = payload.model_dump(exclude_none=True)
        for field, value in data.items():
            if hasattr(cabinet, field):
                setattr(cabinet, field, value)
                
        await db.flush()
        await db.commit()
        await db.refresh(cabinet)
        
        logger.info(f"Storage cabinet updated: {cabinet_id} by user {user_id}")
        return cabinet
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating storage cabinet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cabinet."
        )


@router.get(
    "/{location_id}/grid",
    summary="Get grid room map layout",
    description="Retrieve the visual row-column map coordinate grid representation of all cabinets in this location."
)
async def get_location_grid(
    location_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user_id),
):
    try:
        repo = LocationRepository(db)
        location = await repo.get(location_id)
        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Physical location '{location_id}' not found."
            )
            
        cabinets = await repo.get_cabinets_by_location(location_id)
        return StorageMapper.map_cabinet_layout_grid(cabinets)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error mapping cabinet grid for location {location_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to build room grid map."
        )
