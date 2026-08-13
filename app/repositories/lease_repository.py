# app/repositories/lease_repository.py
"""
Lease Agreement Repository
Land Intelligence System
"""

import logging
from typing import Optional, List, Tuple
from decimal import Decimal
from datetime import date

from sqlalchemy import select, func, or_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lease_agreement import LeaseAgreement
from app.models.lease_payment_schedule import LeasePaymentSchedule
from app.models.parcel import Parcel
from app.models.enums import LeaseStatus, LeasePaymentStatus
from app.repositories.base_repository import BaseRepository
from app.schemas.lease_agreement_schema import LeaseAgreementCreate, LeaseAgreementUpdate

logger = logging.getLogger(__name__)


class LeaseRepository(BaseRepository[LeaseAgreement, LeaseAgreementCreate, LeaseAgreementUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(LeaseAgreement, db)

    async def get_with_details(self, lease_id: str) -> Optional[LeaseAgreement]:
        """Fetch lease agreement with parcel and payment schedules populated."""
        query = (
            select(LeaseAgreement)
            .options(
                selectinload(LeaseAgreement.parcel),
                selectinload(LeaseAgreement.payment_schedules),
            )
            .where(LeaseAgreement.id == str(lease_id), LeaseAgreement.is_active == True)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_leases(
        self,
        parcel_id: Optional[str] = None,
        tenant_search: Optional[str] = None,
        status: Optional[LeaseStatus] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[LeaseAgreement]:
        """List lease agreements with optional filters."""
        query = (
            select(LeaseAgreement)
            .options(selectinload(LeaseAgreement.parcel))
            .where(LeaseAgreement.is_active == True)
        )

        if parcel_id:
            query = query.where(LeaseAgreement.parcel_id == str(parcel_id))
        if status:
            query = query.where(LeaseAgreement.status == status)
        if tenant_search:
            search_pattern = f"%{tenant_search.strip()}%"
            query = query.where(
                or_(
                    LeaseAgreement.tenant_name.ilike(search_pattern),
                    LeaseAgreement.lease_number.ilike(search_pattern),
                    LeaseAgreement.tenant_id_number.ilike(search_pattern),
                )
            )

        query = query.order_by(desc(LeaseAgreement.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_leases(
        self,
        parcel_id: Optional[str] = None,
        tenant_search: Optional[str] = None,
        status: Optional[LeaseStatus] = None,
    ) -> int:
        """Count lease agreements matching filters."""
        query = select(func.count(LeaseAgreement.id)).where(LeaseAgreement.is_active == True)

        if parcel_id:
            query = query.where(LeaseAgreement.parcel_id == str(parcel_id))
        if status:
            query = query.where(LeaseAgreement.status == status)
        if tenant_search:
            search_pattern = f"%{tenant_search.strip()}%"
            query = query.where(
                or_(
                    LeaseAgreement.tenant_name.ilike(search_pattern),
                    LeaseAgreement.lease_number.ilike(search_pattern),
                    LeaseAgreement.tenant_id_number.ilike(search_pattern),
                )
            )

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def get_by_lease_number(self, lease_number: str) -> Optional[LeaseAgreement]:
        """Find lease agreement by lease number."""
        query = select(LeaseAgreement).where(
            LeaseAgreement.lease_number == lease_number,
            LeaseAgreement.is_active == True,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_payment_schedule(self, schedule_id: str) -> Optional[LeasePaymentSchedule]:
        """Fetch payment schedule item by ID."""
        query = select(LeasePaymentSchedule).where(
            LeasePaymentSchedule.id == str(schedule_id),
            LeasePaymentSchedule.is_active == True,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def record_payment(
        self,
        schedule: LeasePaymentSchedule,
        amount_paid: Decimal,
        paid_date: date,
        payment_reference: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> LeasePaymentSchedule:
        """Record payment against schedule item."""
        new_total_paid = Decimal(str(schedule.amount_paid or 0)) + Decimal(str(amount_paid))
        schedule.amount_paid = new_total_paid
        schedule.paid_date = paid_date
        if payment_reference:
            schedule.payment_reference = payment_reference
        if notes:
            schedule.notes = notes

        due = Decimal(str(schedule.amount_due))
        if new_total_paid >= due:
            schedule.status = LeasePaymentStatus.PAID
        elif new_total_paid > 0:
            schedule.status = LeasePaymentStatus.PARTIAL

        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def get_summary_stats(self) -> Tuple[int, int, int, int, Decimal, Decimal, Decimal, int]:
        """Calculate lease statistics summary."""
        # Total counts by status
        total_q = await self.db.execute(select(func.count(LeaseAgreement.id)).where(LeaseAgreement.is_active == True))
        total_leases = total_q.scalar() or 0

        active_q = await self.db.execute(
            select(func.count(LeaseAgreement.id)).where(
                LeaseAgreement.is_active == True, LeaseAgreement.status == LeaseStatus.ACTIVE
            )
        )
        active_leases = active_q.scalar() or 0

        expired_q = await self.db.execute(
            select(func.count(LeaseAgreement.id)).where(
                LeaseAgreement.is_active == True, LeaseAgreement.status == LeaseStatus.EXPIRED
            )
        )
        expired_leases = expired_q.scalar() or 0

        draft_q = await self.db.execute(
            select(func.count(LeaseAgreement.id)).where(
                LeaseAgreement.is_active == True, LeaseAgreement.status == LeaseStatus.DRAFT
            )
        )
        draft_leases = draft_q.scalar() or 0

        # Financial totals
        rev_q = await self.db.execute(
            select(func.sum(LeaseAgreement.annual_rent_amount)).where(
                LeaseAgreement.is_active == True, LeaseAgreement.status == LeaseStatus.ACTIVE
            )
        )
        total_annual_revenue = Decimal(str(rev_q.scalar() or 0))

        coll_q = await self.db.execute(
            select(func.sum(LeasePaymentSchedule.amount_paid)).where(
                LeasePaymentSchedule.is_active == True,
                LeasePaymentSchedule.status.in_([LeasePaymentStatus.PAID, LeasePaymentStatus.PARTIAL]),
            )
        )
        total_collected = Decimal(str(coll_q.scalar() or 0))

        pend_q = await self.db.execute(
            select(func.sum(LeasePaymentSchedule.amount_due - LeasePaymentSchedule.amount_paid)).where(
                LeasePaymentSchedule.is_active == True,
                LeasePaymentSchedule.status.in_([LeasePaymentStatus.PENDING, LeasePaymentStatus.OVERDUE, LeasePaymentStatus.PARTIAL]),
            )
        )
        total_pending = Decimal(str(pend_q.scalar() or 0))

        today = date.today()
        overdue_q = await self.db.execute(
            select(func.count(LeasePaymentSchedule.id)).where(
                LeasePaymentSchedule.is_active == True,
                LeasePaymentSchedule.due_date < today,
                LeasePaymentSchedule.status.in_([LeasePaymentStatus.PENDING, LeasePaymentStatus.PARTIAL]),
            )
        )
        overdue_count = overdue_q.scalar() or 0

        return (
            total_leases,
            active_leases,
            expired_leases,
            draft_leases,
            total_annual_revenue,
            total_collected,
            total_pending,
            overdue_count,
        )
