# app/services/tax/payment_processor.py
"""
Service module for recording payments and issuing receipts.

Responsibility: Records payments; issues receipts.
Scope: Phase 3 - Backend API & Services
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.models.tax_payment import TaxPayment
from app.repositories.tax_repository import TaxRepository
from app.services.tax.penalty_engine import PenaltyEngine


class PaymentProcessor:
    """
    Records tax payments and issues payment receipts.
    """

    def __init__(
        self,
        tax_repository: TaxRepository,
        penalty_engine: PenaltyEngine
    ):
        """
        Initialize the payment processor with dependencies.

        Args:
            tax_repository: Repository for tax record and payment operations
            penalty_engine: Engine for calculating outstanding penalties
        """
        self.tax_repository = tax_repository
        self.penalty_engine = penalty_engine

    async def record_payment(
        self,
        parcel_id: UUID,
        assessment_year: int,
        amount_paid: Decimal,
        payment_method: str,
        reference_number: Optional[str] = None,
        payment_date: Optional[date] = None,
        received_by: str = "system",
        apply_to_penalties_first: bool = True
    ) -> dict:
        """
        Record a tax payment for a parcel with transaction safety and overpayment handling.

        Args:
            parcel_id: UUID of the parcel
            assessment_year: Year of assessment being paid
            amount_paid: Amount being paid
            payment_method: Method of payment (cash, bank_transfer, check, mobile_money)
            reference_number: Optional payment reference or transaction ID
            payment_date: Optional override for payment date (defaults to today)
            apply_to_penalties_first: If True, penalties paid before principal

        Returns:
            Dictionary with payment processing result
        """
        if payment_date is None:
            payment_date = date.today()

        if amount_paid <= Decimal("0.00"):
            return {
                "success": False,
                "error": "Payment amount must be greater than zero",
                "payment_id": None,
            }

        # Use transaction with row lock for safety
        async with self.tax_repository.transaction():
            # Lock the tax record for update to prevent race conditions
            tax_record = await self.tax_repository.get_by_parcel_and_year_for_update(
                parcel_id, assessment_year
            )

            if not tax_record:
                return {
                    "success": False,
                    "error": f"No tax record found for parcel {parcel_id} year {assessment_year}",
                    "payment_id": None,
                }

            # Get already paid amount
            already_paid = await self.tax_repository.get_total_paid_for_assessment(
                tax_record.id
            )
            
            # Calculate remaining principal
            remaining_principal = Decimal(str(tax_record.total_amount)) - Decimal(str(already_paid))
            if remaining_principal < Decimal("0.00"):
                remaining_principal = Decimal("0.00")
            
            # Calculate penalties on the remaining principal only
            due_date = self._get_due_date_for_year(assessment_year)
            
            if payment_date > due_date and remaining_principal > Decimal("0.00"):
                penalty_calculation = await self.penalty_engine.calculate_penalty_on_balance(
                    remaining_principal, due_date, payment_date
                )
                penalty_amount = penalty_calculation["base_penalty"] + penalty_calculation["interest_accrued"]
            else:
                penalty_amount = Decimal("0.00")
            
            total_outstanding = remaining_principal + penalty_amount
            
            # Check for overpayment
            if amount_paid > total_outstanding:
                return {
                    "success": False,
                    "error": f"Payment amount {amount_paid} exceeds total outstanding {total_outstanding}. Overpayments must be processed as credits.",
                    "payment_id": None,
                    "overpayment_amount": amount_paid - total_outstanding,
                }
            
            # Apply payment according to priority rules
            if apply_to_penalties_first:
                penalty_portion = min(amount_paid, penalty_amount)
                principal_portion = amount_paid - penalty_portion
            else:
                principal_portion = min(amount_paid, remaining_principal)
                penalty_portion = amount_paid - principal_portion

            # Create payment record
            payment = TaxPayment(
                tax_record_id=tax_record.id,
                payment_amount=float(amount_paid),
                payment_date=payment_date,
                payment_method=payment_method,
                payment_reference=reference_number,
                receipt_number=self._generate_receipt_number_for_date(payment_date),
                received_by=received_by,
                notes=(
                    f"Principal: {principal_portion}; Penalty: {penalty_portion}"
                ),
            )

            created_payment = await self.tax_repository.create_payment(payment)
            
            # Calculate new remaining balances
            new_remaining_principal = remaining_principal - principal_portion
            new_remaining_penalty = penalty_amount - penalty_portion
            
            # Update tax record status if fully paid
            if new_remaining_principal <= Decimal("0.00") and new_remaining_penalty <= Decimal("0.00"):
                await self.tax_repository.update_tax_record_status(
                    tax_record.id, "paid"
                )
            elif payment_date > due_date and remaining_principal > Decimal("0.00"):
                await self.tax_repository.update_tax_record_status(
                    tax_record.id, "partial"
                )

            return {
                "success": True,
                "payment_id": str(created_payment.id),
                "amount_applied": amount_paid,
                "principal_portion": principal_portion,
                "penalty_portion": penalty_portion,
                "remaining_principal": new_remaining_principal,
                "remaining_penalty": new_remaining_penalty,
                "total_remaining": new_remaining_principal + new_remaining_penalty,
                "is_fully_paid": new_remaining_principal <= Decimal("0.00") and new_remaining_penalty <= Decimal("0.00"),
            }

    async def issue_receipt(self, payment_id: UUID) -> Optional[dict]:
        """
        Generate a payment receipt for a recorded payment.

        Args:
            payment_id: UUID of the payment

        Returns:
            Dictionary with receipt data or None if payment not found
        """
        payment = await self.tax_repository.get_payment(payment_id)
        
        if not payment:
            return None

        tax_record = await self.tax_repository.get(payment.tax_record_id)
        parcel = await self.tax_repository.get_parcel(tax_record.parcel_id)

        receipt = {
            "receipt_id": str(payment.id),
            "receipt_number": payment.receipt_number,
            "receipt_date": payment.payment_date.isoformat(),
            "parcel": {
                "id": str(parcel.id),
                "parcel_number": parcel.parcel_number,
            },
            "assessment_year": tax_record.assessment_year,
            "payment_details": {
                "payment_amount": str(payment.payment_amount),
                "payment_method": payment.payment_method,
                "payment_reference": payment.payment_reference,
            },
            "is_reversal": payment.is_reversal,
        }

        return receipt

    async def get_payment_history(self, parcel_id: UUID) -> list:
        """
        Get payment history for a parcel.

        Args:
            parcel_id: UUID of the parcel

        Returns:
            List of payment history entries
        """
        payments = await self.tax_repository.get_payments_by_parcel(parcel_id)
        
        history = []
        for payment in payments:
            history.append({
                "payment_id": str(payment.id),
                "date": payment.payment_date.isoformat(),
                "amount": str(payment.payment_amount),
                "method": payment.payment_method,
                "reference": payment.payment_reference,
            })
        
        return history

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

    def _generate_receipt_number(self, payment: TaxPayment) -> str:
        """
        Generate a unique receipt number for a payment.

        Args:
            payment: TaxPayment entity

        Returns:
            Formatted receipt number string
        """
        # Format: RCP-YYYYMMDD-XXXX (where XXXX is last 4 chars of UUID)
        date_str = payment.payment_date.strftime("%Y%m%d")
        short_id = str(payment.id)[-4:].upper()
        return f"RCP-{date_str}-{short_id}"

    def _generate_receipt_number_for_date(self, payment_date: date) -> str:
        """
        Generate a receipt number before the payment UUID exists.
        """
        from uuid import uuid4

        date_str = payment_date.strftime("%Y%m%d")
        short_id = str(uuid4())[-4:].upper()
        return f"RCP-{date_str}-{short_id}"
