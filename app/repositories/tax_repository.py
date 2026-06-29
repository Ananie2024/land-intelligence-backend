# app/repositories/tax_repository.py
"""
Tax Repository
Phase 2 — Section 3.2
Land Intelligence System
"""

from contextlib import asynccontextmanager
from typing import Optional, List, Sequence, Union, Dict

from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.parcel import Parcel
from app.models.tax_record import TaxRecord
from app.models.enums import TaxRecordStatus
from app.models.tax_payment import TaxPayment
from app.repositories.base_repository import BaseRepository
from app.schemas.tax_schema import TaxRecordCreate, TaxRecordUpdate


class TaxRepository(BaseRepository[TaxRecord, TaxRecordCreate, TaxRecordUpdate]):
    """
    Repository for TaxRecord entity with extended functionality.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize tax repository.
        
        Args:
            db: Async database session
        """
        super().__init__(TaxRecord, db)
    
    async def get_current_assessment(self, parcel_id: str) -> Optional[TaxRecord]:
        """
        Get the current (most recent) tax assessment for a parcel.
        
        Args:
            parcel_id: UUID of the parcel
            
        Returns:
            Most recent tax record, None if none exists
        """
        result = await self.db.execute(
            select(TaxRecord)
            .where(
                TaxRecord.parcel_id == str(parcel_id),
                TaxRecord.is_active
            )
            .order_by(
                desc(TaxRecord.assessment_year),
                desc(TaxRecord.created_at)
            )
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    async def get_payment_history(self, parcel_id: str, skip: int = 0, limit: int = 100) -> List[TaxPayment]:
        """
        Get payment history for a parcel across all tax records.
        
        Args:
            parcel_id: UUID of the parcel
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of tax payment instances
        """
        result = await self.db.execute(
            select(TaxPayment)
            .join(TaxRecord)
            .where(
                TaxRecord.parcel_id == str(parcel_id),
                TaxPayment.is_active
            )
            .order_by(desc(TaxPayment.payment_date))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_outstanding_balance(self, parcel_id: str) -> float:
        """
        Get total outstanding balance for a parcel.
        Sum of unpaid tax amounts minus payments.
        
        Args:
            parcel_id: UUID of the parcel
            
        Returns:
            Total outstanding balance
        """
        # Get all tax records for this parcel
        result = await self.db.execute(
            select(TaxRecord).where(
                TaxRecord.parcel_id == str(parcel_id),
                TaxRecord.is_active,
                TaxRecord.status != TaxRecordStatus.PAID
            )
        )
        tax_records = result.scalars().all()
        
        total_balance = 0.0
        for record in tax_records:
            # Get total payments for this record
            payments_result = await self.db.execute(
                select(func.sum(TaxPayment.payment_amount))
                .where(
                    TaxPayment.tax_record_id == record.id,
                    TaxPayment.is_active,
                    TaxPayment.is_reversal.is_(False)
                )
            )
            total_paid = payments_result.scalar_one() or 0.0
            
            # Calculate outstanding
            outstanding = record.total_amount - total_paid
            if outstanding > 0:
                total_balance += outstanding
        
        return total_balance
    
    async def get_by_parcel_and_year(
        self,
        parcel_id: str,
        year: Union[int, str],
    ) -> Optional[TaxRecord]:
        """
        Get tax record for a specific parcel and year.
        
        Args:
            parcel_id: UUID of the parcel
            year: Assessment year (YYYY)
            
        Returns:
            Tax record if found, None otherwise
        """
        result = await self.db.execute(
            select(TaxRecord).where(
                TaxRecord.parcel_id == str(parcel_id),
                TaxRecord.assessment_year == str(year),
                TaxRecord.is_active
            )
        )
        return result.scalar_one_or_none()

    async def get_by_parcel_and_year_for_update(
        self,
        parcel_id: str,
        year: Union[int, str],
    ) -> Optional[TaxRecord]:
        """
        Get tax record for a parcel/year with a row lock.
        """
        result = await self.db.execute(
            select(TaxRecord)
            .where(
                TaxRecord.parcel_id == str(parcel_id),
                TaxRecord.assessment_year == str(year),
                TaxRecord.is_active,
            )
            .with_for_update()
        )
        return result.scalar_one_or_none()
    
    async def list_by_year(self, year: str, skip: int = 0, limit: int = 100) -> List[TaxRecord]:
        """
        List tax records by assessment year.
        
        Args:
            year: Assessment year (YYYY)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of tax records
        """
        return await self.list(
            filters={"assessment_year": year},
            skip=skip,
            limit=limit,
            order_by="created_at",
            descending=True
        )
    
    async def list_overdue(self) -> List[TaxRecord]:
        """
        List all overdue tax records.
        
        Returns:
            List of overdue tax records
        """
        from datetime import date
        
        today = date.today()
        
        result = await self.db.execute(
            select(TaxRecord).where(
                TaxRecord.is_active,
                TaxRecord.status == TaxRecordStatus.PENDING,
                TaxRecord.due_date < today
            )
        )
        return list(result.scalars().all())
    
    async def update_status(self, id: str, status: str) -> Optional[TaxRecord]:
        """
        Update tax record status.
        
        Args:
            id: UUID of tax record
            status: New status (pending, paid, overdue)
            
        Returns:
            Updated tax record, None if not found
        """
        return await self.update(id, TaxRecordUpdate(status=status))
    
    async def get_payments_for_record(self, tax_record_id: str) -> List[TaxPayment]:
        """
        Get all payments for a specific tax record.
        
        Args:
            tax_record_id: UUID of tax record
            
        Returns:
            List of tax payments
        """
        result = await self.db.execute(
            select(TaxPayment)
            .where(
                TaxPayment.tax_record_id == tax_record_id,
                TaxPayment.is_active,
                TaxPayment.is_reversal.is_(False)
            )
            .order_by(TaxPayment.payment_date)
        )
        return list(result.scalars().all())

    async def get_parcel(self, parcel_id: str) -> Optional[Parcel]:
        """
        Get an active parcel by ID for tax workflows.
        """
        result = await self.db.execute(
            select(Parcel).where(
                Parcel.id == str(parcel_id),
                Parcel.is_active,
            )
        )
        return result.scalar_one_or_none()

    async def get_parcels_by_parish(self, parish_id: str) -> List[Parcel]:
        """
        Get active parcels in a parish for batch assessment.
        """
        result = await self.db.execute(
            select(Parcel).where(
                Parcel.parish_id == str(parish_id),
                Parcel.is_active,
            )
        )
        return list(result.scalars().all())

    async def get_all_assessments_for_parcel(self, parcel_id: str) -> List[TaxRecord]:
        """
        Get all active tax assessments for a parcel.
        """
        result = await self.db.execute(
            select(TaxRecord)
            .where(
                TaxRecord.parcel_id == str(parcel_id),
                TaxRecord.is_active,
            )
            .order_by(desc(TaxRecord.assessment_year))
        )
        return list(result.scalars().all())

    async def get_existing_assessments_map(
        self,
        parcel_ids: Sequence[str],
        year: Union[int, str],
    ) -> dict[str, TaxRecord]:
        """
        Return existing assessments keyed by parcel ID.
        """
        if not parcel_ids:
            return {}

        result = await self.db.execute(
            select(TaxRecord).where(
                TaxRecord.parcel_id.in_([str(parcel_id) for parcel_id in parcel_ids]),
                TaxRecord.assessment_year == str(year),
                TaxRecord.is_active,
            )
        )
        return {record.parcel_id: record for record in result.scalars().all()}

    async def get_total_paid_for_assessment(self, tax_record_id: str) -> float:
        """
        Sum active, non-reversed payments for a tax record.
        """
        result = await self.db.execute(
            select(func.sum(TaxPayment.payment_amount)).where(
                TaxPayment.tax_record_id == str(tax_record_id),
                TaxPayment.is_active,
                TaxPayment.is_reversal.is_(False),
            )
        )
        return result.scalar_one() or 0.0

    async def get_payments_for_records(self, tax_record_ids: List[str]) -> Dict[str, float]:
        """
        Aggregate total paid amount per tax record in a single query.

        Args:
            tax_record_ids: List of tax record UUIDs

        Returns:
            Dict mapping tax_record_id (str) -> total_paid (float)
        """
        if not tax_record_ids:
            return {}

        result = await self.db.execute(
            select(
                TaxPayment.tax_record_id,
                func.sum(TaxPayment.payment_amount).label("total_paid")
            )
            .where(
                TaxPayment.tax_record_id.in_([str(rid) for rid in tax_record_ids]),
                TaxPayment.is_active,
                TaxPayment.is_reversal.is_(False),
            )
            .group_by(TaxPayment.tax_record_id)
        )
        rows = result.all()
        return {str(row.tax_record_id): float(row.total_paid or 0.0) for row in rows}


    async def create_payment(self, payment: TaxPayment) -> TaxPayment:
        """
        Persist a TaxPayment instance.
        """
        self.db.add(payment)
        await self.db.flush()
        await self.db.refresh(payment)
        return payment

    async def get_payment(self, payment_id: str) -> Optional[TaxPayment]:
        """
        Get an active payment by ID.
        """
        result = await self.db.execute(
            select(TaxPayment).where(
                TaxPayment.id == str(payment_id),
                TaxPayment.is_active,
            )
        )
        return result.scalar_one_or_none()

    async def get_payments_by_parcel(self, parcel_id: str) -> List[TaxPayment]:
        """
        Get payment history for all assessments on a parcel.
        """
        return await self.get_payment_history(parcel_id)

    async def update_tax_record_status(
        self,
        tax_record_id: str,
        status: str,
    ) -> Optional[TaxRecord]:
        """
        Update a tax record status.
        """
        return await self.update_status(tax_record_id, status)

    @asynccontextmanager
    async def transaction(self):
        """
        Transaction context helper for tax services.
        """
        async with self.db.begin():
            yield
