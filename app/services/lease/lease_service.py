# app/services/lease/lease_service.py
"""
Lease Service
Land Intelligence System
"""

import logging
import uuid
from decimal import Decimal
from datetime import date, timedelta
from typing import Optional, List, Tuple
from dateutil.relativedelta import relativedelta

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.lease_agreement import LeaseAgreement
from app.models.lease_payment_schedule import LeasePaymentSchedule
from app.models.enums import LeaseStatus, PaymentFrequency, LeasePaymentStatus
from app.repositories.lease_repository import LeaseRepository
from app.repositories.parcel_repository import ParcelRepository
from app.schemas.lease_agreement_schema import (
    LeaseAgreementCreate,
    LeaseAgreementUpdate,
    LeasePaymentRecordRequest,
    LeaseSummaryStats,
)

logger = logging.getLogger(__name__)


class LeaseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.lease_repo = LeaseRepository(db)
        self.parcel_repo = ParcelRepository(db)

    def _calculate_installment_amount(self, annual_rent: Decimal, frequency: PaymentFrequency) -> Decimal:
        """Calculate per-installment payment amount."""
        annual = Decimal(str(annual_rent))
        if frequency == PaymentFrequency.MONTHLY:
            return (annual / Decimal("12")).quantize(Decimal("0.01"))
        elif frequency == PaymentFrequency.QUARTERLY:
            return (annual / Decimal("4")).quantize(Decimal("0.01"))
        elif frequency == PaymentFrequency.SEMI_ANNUALLY:
            return (annual / Decimal("2")).quantize(Decimal("0.01"))
        else:  # ANNUALLY
            return annual.quantize(Decimal("0.01"))

    def _generate_due_dates(self, start_date: date, end_date: date, frequency: PaymentFrequency) -> List[date]:
        """Generate list of payment due dates between start_date and end_date."""
        due_dates = []
        current = start_date

        if frequency == PaymentFrequency.MONTHLY:
            delta = relativedelta(months=1)
        elif frequency == PaymentFrequency.QUARTERLY:
            delta = relativedelta(months=3)
        elif frequency == PaymentFrequency.SEMI_ANNUALLY:
            delta = relativedelta(months=6)
        else:  # ANNUALLY
            delta = relativedelta(years=1)

        while current < end_date:
            due_dates.append(current)
            next_date = current + delta
            if next_date == current:
                break
            current = next_date

        if not due_dates:
            due_dates.append(start_date)

        return due_dates

    async def _generate_unique_lease_number(self) -> str:
        """Generate unique lease reference code."""
        year = date.today().year
        random_suffix = str(uuid.uuid4().hex[:6]).upper()
        lease_num = f"LEASE-{year}-{random_suffix}"
        existing = await self.lease_repo.get_by_lease_number(lease_num)
        while existing:
            random_suffix = str(uuid.uuid4().hex[:6]).upper()
            lease_num = f"LEASE-{year}-{random_suffix}"
            existing = await self.lease_repo.get_by_lease_number(lease_num)
        return lease_num

    async def create_lease(self, data: LeaseAgreementCreate) -> LeaseAgreement:
        """Create new lease agreement and optionally auto-generate payment schedules."""
        # 1. Verify parcel exists
        parcel = await self.parcel_repo.get(str(data.parcel_id))
        if not parcel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parcel with ID '{data.parcel_id}' not found.",
            )

        # 2. Validate dates
        if data.start_date >= data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lease start_date must be before end_date.",
            )

        # 3. Handle lease number
        lease_number = data.lease_number
        if not lease_number or not lease_number.strip():
            lease_number = await self._generate_unique_lease_number()
        else:
            existing = await self.lease_repo.get_by_lease_number(lease_number.strip())
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Lease number '{lease_number}' already exists.",
                )

        # 4. Calculate installment amount
        installment = self._calculate_installment_amount(data.annual_rent_amount, data.payment_frequency)

        # 5. Build model
        lease = LeaseAgreement(
            parcel_id=data.parcel_id,
            lease_number=lease_number,
            tenant_name=data.tenant_name.strip(),
            tenant_contact=data.tenant_contact.strip() if data.tenant_contact else None,
            tenant_id_number=data.tenant_id_number.strip() if data.tenant_id_number else None,
            start_date=data.start_date,
            end_date=data.end_date,
            annual_rent_amount=data.annual_rent_amount,
            payment_frequency=data.payment_frequency,
            installment_amount=installment,
            status=LeaseStatus.ACTIVE,
            purpose_use=data.purpose_use.strip() if data.purpose_use else None,
            notes=data.notes.strip() if data.notes else None,
        )

        self.db.add(lease)
        await self.db.flush()

        # 6. Auto-generate payment schedule items if requested
        if data.auto_generate_schedules:
            due_dates = self._generate_due_dates(data.start_date, data.end_date, data.payment_frequency)
            for due_d in due_dates:
                schedule = LeasePaymentSchedule(
                    lease_id=lease.id,
                    due_date=due_d,
                    amount_due=installment,
                    amount_paid=Decimal("0.00"),
                    status=LeasePaymentStatus.PENDING,
                )
                self.db.add(schedule)

        await self.db.commit()
        return await self.lease_repo.get_with_details(str(lease.id))

    async def get_lease(self, lease_id: str) -> LeaseAgreement:
        """Get lease agreement with full details."""
        lease = await self.lease_repo.get_with_details(lease_id)
        if not lease:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lease agreement '{lease_id}' not found.",
            )
        return lease

    async def list_leases(
        self,
        parcel_id: Optional[str] = None,
        tenant_search: Optional[str] = None,
        status: Optional[LeaseStatus] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[LeaseAgreement], int]:
        """List lease agreements with pagination."""
        skip = (page - 1) * page_size
        items = await self.lease_repo.list_leases(
            parcel_id=parcel_id,
            tenant_search=tenant_search,
            status=status,
            skip=skip,
            limit=page_size,
        )
        total = await self.lease_repo.count_leases(
            parcel_id=parcel_id,
            tenant_search=tenant_search,
            status=status,
        )
        return items, total

    async def update_lease(self, lease_id: str, data: LeaseAgreementUpdate) -> LeaseAgreement:
        """Update lease agreement details."""
        lease = await self.lease_repo.get_with_details(lease_id)
        if not lease:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lease agreement '{lease_id}' not found.",
            )

        if data.tenant_name is not None:
            lease.tenant_name = data.tenant_name.strip()
        if data.tenant_contact is not None:
            lease.tenant_contact = data.tenant_contact.strip()
        if data.tenant_id_number is not None:
            lease.tenant_id_number = data.tenant_id_number.strip()
        if data.purpose_use is not None:
            lease.purpose_use = data.purpose_use.strip()
        if data.notes is not None:
            lease.notes = data.notes.strip()
        if data.status is not None:
            lease.status = data.status

        # If annual rent or frequency updated, recalculate installment
        new_rent = data.annual_rent_amount if data.annual_rent_amount is not None else lease.annual_rent_amount
        new_freq = data.payment_frequency if data.payment_frequency is not None else lease.payment_frequency
        lease.annual_rent_amount = new_rent
        lease.payment_frequency = new_freq
        lease.installment_amount = self._calculate_installment_amount(new_rent, new_freq)

        if data.start_date is not None:
            lease.start_date = data.start_date
        if data.end_date is not None:
            lease.end_date = data.end_date

        if lease.start_date >= lease.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lease start_date must be before end_date.",
            )

        await self.db.commit()
        return await self.lease_repo.get_with_details(lease_id)

    async def delete_lease(self, lease_id: str) -> bool:
        """Soft delete lease agreement."""
        lease = await self.lease_repo.get(lease_id)
        if not lease:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lease agreement '{lease_id}' not found.",
            )
        lease.is_active = False
        await self.db.commit()
        return True

    async def record_payment(self, schedule_id: str, data: LeasePaymentRecordRequest) -> LeasePaymentSchedule:
        """Record payment against schedule item."""
        schedule = await self.lease_repo.get_payment_schedule(schedule_id)
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment schedule item '{schedule_id}' not found.",
            )

        paid_d = data.paid_date or date.today()
        return await self.lease_repo.record_payment(
            schedule=schedule,
            amount_paid=data.amount_paid,
            paid_date=paid_d,
            payment_reference=data.payment_reference,
            notes=data.notes,
        )

    async def get_summary_stats(self) -> LeaseSummaryStats:
        """Get overview statistics for lease agreements."""
        (
            total_leases,
            active_leases,
            expired_leases,
            draft_leases,
            total_annual_revenue,
            total_collected,
            total_pending,
            overdue_count,
        ) = await self.lease_repo.get_summary_stats()

        return LeaseSummaryStats(
            total_leases=total_leases,
            active_leases=active_leases,
            expired_leases=expired_leases,
            draft_leases=draft_leases,
            total_annual_revenue=total_annual_revenue,
            total_collected_revenue=total_collected,
            total_pending_revenue=total_pending,
            overdue_payments_count=overdue_count,
        )
