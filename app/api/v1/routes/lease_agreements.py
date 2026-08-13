# app/api/v1/routes/lease_agreements.py
"""
Lease Agreements API Routes
Land Intelligence System
"""

import logging
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import LeaseStatus
from app.services.lease.lease_service import LeaseService
from app.schemas.lease_agreement_schema import (
    LeaseAgreementCreate,
    LeaseAgreementUpdate,
    LeaseAgreementResponse,
    LeaseAgreementDetailResponse,
    LeasePaymentRecordRequest,
    LeasePaymentScheduleResponse,
    LeaseSummaryStats,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=LeaseAgreementDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lease agreement",
    description="Registers a new lease agreement between parish land and a tenant with optional payment schedules.",
)
async def create_lease(
    data: LeaseAgreementCreate,
    db: AsyncSession = Depends(get_db),
):
    service = LeaseService(db)
    return await service.create_lease(data)


@router.get(
    "/stats",
    response_model=LeaseSummaryStats,
    summary="Get lease statistics summary",
    description="Returns financial metrics, active/expired contract counts, and overdue payment stats.",
)
async def get_lease_stats(
    db: AsyncSession = Depends(get_db),
):
    service = LeaseService(db)
    return await service.get_summary_stats()


@router.get(
    "",
    summary="List lease agreements",
    description="Retrieve paginated list of lease agreements filtered by parcel, tenant name, or status.",
)
async def list_leases(
    parcel_id: Optional[UUID] = Query(None, description="Filter by parcel UUID"),
    tenant: Optional[str] = Query(None, description="Search by tenant name or lease number"),
    status: Optional[LeaseStatus] = Query(None, description="Filter by lease status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
):
    service = LeaseService(db)
    items, total = await service.list_leases(
        parcel_id=str(parcel_id) if parcel_id else None,
        tenant_search=tenant,
        status=status,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [LeaseAgreementResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get(
    "/{lease_id}",
    response_model=LeaseAgreementDetailResponse,
    summary="Get lease agreement details",
    description="Returns detailed info for a specific lease agreement including payment schedules.",
)
async def get_lease(
    lease_id: UUID = Path(..., description="Lease agreement UUID"),
    db: AsyncSession = Depends(get_db),
):
    service = LeaseService(db)
    return await service.get_lease(str(lease_id))


@router.put(
    "/{lease_id}",
    response_model=LeaseAgreementDetailResponse,
    summary="Update lease agreement",
    description="Modifies existing lease agreement attributes.",
)
async def update_lease(
    data: LeaseAgreementUpdate,
    lease_id: UUID = Path(..., description="Lease agreement UUID"),
    db: AsyncSession = Depends(get_db),
):
    service = LeaseService(db)
    return await service.update_lease(str(lease_id), data)


@router.delete(
    "/{lease_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete lease agreement",
    description="Soft-deletes a lease agreement.",
)
async def delete_lease(
    lease_id: UUID = Path(..., description="Lease agreement UUID"),
    db: AsyncSession = Depends(get_db),
):
    service = LeaseService(db)
    await service.delete_lease(str(lease_id))
    return None


@router.post(
    "/{lease_id}/schedules/{schedule_id}/pay",
    response_model=LeasePaymentScheduleResponse,
    summary="Record lease payment",
    description="Records payment for a specific installment schedule item.",
)
async def record_lease_payment(
    data: LeasePaymentRecordRequest,
    lease_id: UUID = Path(..., description="Lease agreement UUID"),
    schedule_id: UUID = Path(..., description="Schedule item UUID"),
    db: AsyncSession = Depends(get_db),
):
    service = LeaseService(db)
    return await service.record_payment(str(schedule_id), data)
