# app/repositories/tax_repository.py
"""
Tax Repository
Phase 2 — Section 3.2
Land Intelligence System
"""

from typing import Optional, List
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tax_record import TaxRecord
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
                TaxRecord.parcel_id == parcel_id,
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
                TaxRecord.parcel_id == parcel_id,
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
                TaxRecord.parcel_id == parcel_id,
                TaxRecord.is_active,
                TaxRecord.status != "paid"
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
                    not TaxPayment.is_reversal
                )
            )
            total_paid = payments_result.scalar_one() or 0.0
            
            # Calculate outstanding
            outstanding = record.total_amount - total_paid
            if outstanding > 0:
                total_balance += outstanding
        
        return total_balance
    
    async def get_by_parcel_and_year(self, parcel_id: str, year: str) -> Optional[TaxRecord]:
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
                TaxRecord.parcel_id == parcel_id,
                TaxRecord.assessment_year == year,
                TaxRecord.is_active
            )
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
                TaxRecord.status == "pending",
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
                not TaxPayment.is_reversal
            )
            .order_by(TaxPayment.payment_date)
        )
        return list(result.scalars().all())