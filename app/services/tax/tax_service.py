# app/services/tax/tax_service.py
"""
Tax Calculation Service
Phase 3 — Section 4.2
Land Intelligence System
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import desc

from app.models.parcel import Parcel
from app.models.land_use_category import LandUseCategory
from app.models.tax_record import TaxRecord
from app.models.tax_payment import TaxPayment
from app.repositories.tax_repository import TaxRepository
from app.repositories.parcel_repository import ParcelRepository
from app.repositories.parish_repository import ParishRepository
from app.services.tax.tax_calculator import TaxCalculator
from app.services.tax.penalty_engine import PenaltyEngine
from app.services.tax.payment_processor import PaymentProcessor
from app.services.tax.assessment_generator import AssessmentGenerator

logger = logging.getLogger(__name__)


class TaxService:
    """
    Business logic layer for tax operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = TaxRepository(db)
        self.parcel_repo = ParcelRepository(db)
        self.parish_repo = ParishRepository(db)
        self.tax_calculator = TaxCalculator(self.repo)
        self.penalty_engine = PenaltyEngine(self.repo)
        self.payment_processor = PaymentProcessor(self.repo, self.penalty_engine)
        self.assessment_generator = AssessmentGenerator(self.repo, self.tax_calculator, self.penalty_engine)

    async def calculate_tax(
        self,
        parcel_id: str,
        assessment_year: str,
        land_use_category_id: Optional[str] = None,
        include_penalties: bool = False
    ) -> Dict[str, Any]:
        """
        Simulate tax calculation without storing a record.
        """
        parcel = await self.parcel_repo.get(parcel_id)
        if not parcel:
            raise ValueError(f"Parcel with ID '{parcel_id}' not found.")

        override_category = None
        category_name = "Unassigned"
        if land_use_category_id:
            result = await self.db.execute(
                select(LandUseCategory).where(
                    LandUseCategory.id == land_use_category_id,
                    LandUseCategory.is_active
                )
            )
            override_category = result.scalar_one_or_none()
            if not override_category:
                raise ValueError(f"Land use category override '{land_use_category_id}' not found.")
            category_name = override_category.name
        else:
            if parcel.land_use_category_id:
                result = await self.db.execute(
                    select(LandUseCategory).where(
                        LandUseCategory.id == parcel.land_use_category_id,
                        LandUseCategory.is_active
                    )
                )
                cat = result.scalar_one_or_none()
                if cat:
                    category_name = cat.name

        calc_result = await self.tax_calculator.calculate_tax(
            parcel=parcel,
            assessment_year=int(assessment_year),
            land_use_category=override_category
        )

        penalties = Decimal("0.00")
        due_date = date(int(assessment_year), 12, 31)

        if include_penalties:
            today = date.today()
            if today > due_date:
                penalty_result = await self.penalty_engine.calculate_penalty_on_balance(
                    Decimal(str(calc_result["base_tax_amount"])),
                    due_date,
                    today
                )
                penalties = penalty_result["base_penalty"] + penalty_result["interest_accrued"]

        total_tax_amount = Decimal(str(calc_result["base_tax_amount"])) + penalties

        return {
            "parcel_id": str(parcel.id),
            "parcel_number": parcel.parcel_number,
            "assessment_year": int(assessment_year),
            "land_use_category_name": category_name,
            "area_sqm": parcel.area_sqm,
            "assessed_value": float(calc_result["assessed_value"]),
            "tax_rate": float(calc_result["tax_rate_applied"]),
            "base_tax_amount": float(calc_result["base_tax_amount"]),
            "penalties_amount": float(penalties),
            "total_amount": float(total_tax_amount),
            "due_date": due_date
        }

    async def generate_assessment(
        self,
        parcel_id: str,
        assessment_year: str,
        user_id: str
    ) -> Optional[TaxRecord]:
        """
        Create a tax assessment record for a parcel.
        """
        parcel = await self.parcel_repo.get(parcel_id)
        if not parcel:
            raise ValueError(f"Parcel with ID '{parcel_id}' not found.")

        existing = await self.repo.get_by_parcel_and_year(parcel_id, assessment_year)
        if existing:
            raise ValueError(f"Tax assessment record already exists for parcel '{parcel_id}' and year '{assessment_year}'.")

        return await self.assessment_generator.generate_assessment(
            parcel=parcel,
            assessment_year=int(assessment_year)
        )

    async def generate_parish_assessments(
        self,
        parish_id: str,
        assessment_year: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Generate tax assessments for all active parcels belonging to a specific parish.
        """
        parish = await self.parish_repo.get(parish_id)
        if not parish:
            raise ValueError(f"Parish '{parish_id}' not found.")

        parcels = await self.repo.get_parcels_by_parish(parish_id)
        if not parcels:
            return {
                "success": True,
                "parish_id": parish_id,
                "assessment_year": assessment_year,
                "generated_count": 0,
                "skipped_count": 0,
            }

        parcel_ids = [str(p.id) for p in parcels]
        existing_map = await self.repo.get_existing_assessments_map(parcel_ids, assessment_year)

        generated = 0
        skipped = 0
        async with self.repo.transaction():
            for parcel in parcels:
                parcel_id = str(parcel.id)
                if parcel_id in existing_map:
                    skipped += 1
                    continue
                await self.assessment_generator.generate_assessment(
                    parcel=parcel,
                    assessment_year=int(assessment_year)
                )
                generated += 1

        return {
            "success": True,
            "parish_id": parish_id,
            "assessment_year": assessment_year,
            "generated_count": generated,
            "skipped_count": skipped,
        }

    async def record_tax_payment(
        self,
        tax_record_id: str,
        payment_amount: float,
        payment_method: str,
        payment_reference: str,
        payment_date: date,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Record a tax payment transaction against an annual assessment record.
        """
        record = await self.repo.get(tax_record_id)
        if not record:
            raise ValueError(f"Tax record with ID '{tax_record_id}' not found.")

        res = await self.payment_processor.record_payment(
            parcel_id=UUID(record.parcel_id),
            assessment_year=int(record.assessment_year),
            amount_paid=Decimal(str(payment_amount)),
            payment_method=payment_method,
            reference_number=payment_reference,
            payment_date=payment_date,
            received_by=user_id
        )

        if not res["success"]:
            raise ValueError(res.get("error", "Failed to process payment"))

        await self.db.commit()
        return res

    async def get_outstanding_tax(
        self,
        parcel_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Calculate the breakdown of outstanding, overdue, and upcoming tax liabilities for a parcel.
        """
        parcel = await self.parcel_repo.get(parcel_id)
        if not parcel:
            raise ValueError(f"Parcel with ID '{parcel_id}' not found.")

        records = await self.repo.get_all_assessments_for_parcel(parcel_id)

        total_outstanding = 0.0
        overdue_amount = 0.0
        upcoming_amount = 0.0
        today = date.today()

        for record in records:
            if record.status == "paid":
                continue

            total_paid = await self.repo.get_total_paid_for_assessment(record.id)

            penalty = Decimal("0.00")
            if today > record.due_date:
                remaining_principal = Decimal(str(record.total_amount)) - Decimal(str(total_paid))
                if remaining_principal > 0:
                    penalty_result = await self.penalty_engine.calculate_penalty_on_balance(
                        remaining_principal,
                        record.due_date,
                        today
                    )
                    penalty = penalty_result["base_penalty"] + penalty_result["interest_accrued"]

            outstanding = float(Decimal(str(record.total_amount)) + penalty - Decimal(str(total_paid)))
            if outstanding > 0:
                total_outstanding += outstanding
                if record.due_date < today:
                    overdue_amount += outstanding
                else:
                    upcoming_amount += outstanding

        return {
            "parcel_id": str(parcel.id),
            "parcel_number": parcel.parcel_number,
            "total_outstanding": round(total_outstanding, 2),
            "overdue_amount": round(overdue_amount, 2),
            "upcoming_amount": round(upcoming_amount, 2),
            "records": records
        }

    async def get_payment_history(
        self,
        parcel_id: str,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all historical payment transactions posted for a parcel's assessments.
        """
        parcel = await self.parcel_repo.get(parcel_id)
        if not parcel:
            raise ValueError(f"Parcel with ID '{parcel_id}' not found.")

        return await self.repo.get_payment_history(parcel_id, skip=skip, limit=limit)

    async def get_tax_record(self, record_id: str, user_id: Optional[str] = None) -> Optional[TaxRecord]:
        """
        Fetch details of a single tax record by UUID.
        """
        return await self.repo.get(record_id)
