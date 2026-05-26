# app/services/tax/penalty_engine.py
"""
Service module for late payment penalties and interest accrual.

Responsibility: Late payment penalties and interest accrual.
Scope: Phase 3 - Backend API & Services
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.models.tax_record import TaxRecord
from app.repositories.tax_repository import TaxRepository


class PenaltyEngine:
    """
    Calculates late payment penalties and interest accrual for overdue tax assessments.
    """

    # Default penalty rates (can be overridden via configuration)
    DEFAULT_PENALTY_RATE = Decimal("0.10")  # 10% base penalty
    DEFAULT_INTEREST_RATE = Decimal("0.02")  # 2% per month
    DAILY_INTEREST_RATE = Decimal("0.0006667")  # ~0.06667% per day (2%/30 days)

    def __init__(self, tax_repository: TaxRepository):
        """
        Initialize the penalty engine with repository dependency.

        Args:
            tax_repository: Repository for tax records and payment history
        """
        self.tax_repository = tax_repository

    async def calculate_penalty(
        self,
        tax_record: TaxRecord,
        due_date: date,
        current_date: Optional[date] = None,
        remaining_balance: Optional[Decimal] = None
    ) -> dict:
        """
        Calculate total penalty and interest for an overdue tax record.

        Args:
            tax_record: Tax record with net_tax_due amount
            due_date: Date when payment was due
            current_date: Optional override for calculation date (defaults to today)
            remaining_balance: Optional override for remaining balance (accounts for partial payments)

        Returns:
            Dictionary containing base_penalty, interest_accrued, and total_due
        """
        if current_date is None:
            current_date = date.today()

        # Use remaining balance if provided, otherwise use full net_tax_due
        principal = remaining_balance if remaining_balance is not None else tax_record.net_tax_due
        principal = principal.quantize(Decimal("0.01"))

        if current_date <= due_date or principal <= Decimal("0.00"):
            return {
                "base_penalty": Decimal("0.00"),
                "interest_accrued": Decimal("0.00"),
                "total_due": principal,
            }

        days_overdue = (current_date - due_date).days

        # Base penalty applies immediately when overdue
        base_penalty = principal * self.DEFAULT_PENALTY_RATE
        base_penalty = base_penalty.quantize(Decimal("0.01"))

        # Calculate daily interest (no arbitrary month floor)
        interest_accrued = principal * self.DAILY_INTEREST_RATE * days_overdue
        interest_accrued = interest_accrued.quantize(Decimal("0.01"))

        total_due = principal + base_penalty + interest_accrued
        total_due = total_due.quantize(Decimal("0.01"))

        return {
            "base_penalty": base_penalty,
            "interest_accrued": interest_accrued,
            "total_due": total_due,
        }

    async def calculate_penalty_for_parcel(
        self,
        parcel_id: UUID,
        assessment_year: int,
        due_date: date,
        current_date: Optional[date] = None,
        remaining_balance: Optional[Decimal] = None
    ) -> Optional[dict]:
        """
        Calculate penalty for a specific parcel's tax assessment.

        Args:
            parcel_id: UUID of the parcel
            assessment_year: Year of the tax assessment
            due_date: Date when payment was due
            current_date: Optional override for calculation date
            remaining_balance: Optional override for remaining balance

        Returns:
            Dictionary with penalty details or None if no tax record found
        """
        tax_record = await self.tax_repository.get_by_parcel_and_year(
            parcel_id, assessment_year
        )

        if not tax_record:
            return None

        # Get paid amount to calculate remaining balance if not provided
        if remaining_balance is None:
            paid_amount = await self.tax_repository.get_total_paid_for_assessment(
                tax_record.id
            )
            remaining_balance = tax_record.net_tax_due - paid_amount
            if remaining_balance < Decimal("0.00"):
                remaining_balance = Decimal("0.00")

        return await self.calculate_penalty(
            tax_record, due_date, current_date, remaining_balance
        )

    async def calculate_outstanding_penalty(
        self,
        parcel_id: UUID,
        current_date: Optional[date] = None
    ) -> dict:
        """
        Calculate total penalty for all assessments for a parcel.

        Includes both due and upcoming assessments in net due calculation.

        Args:
            parcel_id: UUID of the parcel
            current_date: Optional override for calculation date

        Returns:
            Dictionary with total outstanding penalty details
        """
        if current_date is None:
            current_date = date.today()

        all_assessments = await self.tax_repository.get_all_assessments_for_parcel(
            parcel_id
        )

        total_net_due = Decimal("0.00")
        total_penalty = Decimal("0.00")
        total_interest = Decimal("0.00")
        overdue_count = 0

        for record in all_assessments:
            due_date = self._get_due_date_for_year(record.assessment_year)
            
            # Get paid amount for this assessment
            paid_amount = await self.tax_repository.get_total_paid_for_assessment(
                record.id
            )
            remaining_balance = record.net_tax_due - paid_amount
            if remaining_balance < Decimal("0.00"):
                remaining_balance = Decimal("0.00")
            
            # Add to total net due regardless of due date status
            total_net_due += remaining_balance
            
            # Calculate penalty only if overdue
            if current_date > due_date and remaining_balance > Decimal("0.00"):
                penalty_result = await self.calculate_penalty(
                    record, due_date, current_date, remaining_balance
                )
                total_penalty += penalty_result["base_penalty"]
                total_interest += penalty_result["interest_accrued"]
                overdue_count += 1

        total_due = total_net_due + total_penalty + total_interest
        total_due = total_due.quantize(Decimal("0.01"))

        return {
            "total_net_due": total_net_due.quantize(Decimal("0.01")),
            "total_penalty": total_penalty.quantize(Decimal("0.01")),
            "total_interest": total_interest.quantize(Decimal("0.01")),
            "grand_total_due": total_due,
            "total_assessments_count": len(all_assessments),
            "overdue_assessments_count": overdue_count,
        }

    def _get_due_date_for_year(self, assessment_year: int) -> date:
        """
        Get the due date for a given assessment year.
        Default due date is March 31st of the following year.

        Args:
            assessment_year: Year of assessment

        Returns:
            Due date as date object
        """
        return date(assessment_year + 1, 3, 31)