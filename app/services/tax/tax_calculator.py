# app/services/tax/tax_calculator.py
"""
Service module for computing tax liability per parcel and land use.

Responsibility: Computes tax liability per parcel + land use.
Scope: Phase 3 - Backend API & Services
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.models.land_use_category import LandUseCategory
from app.models.parcel import Parcel
from app.models.tax_record import TaxRecord
from app.repositories.tax_repository import TaxRepository


class TaxCalculator:
    """
    Computes tax liability for land parcels based on land use category and area.
    """

    def __init__(self, tax_repository: TaxRepository):
        """
        Initialize the tax calculator with repository dependency.

        Args:
            tax_repository: Repository for tax records and rate schedules
        """
        self.tax_repository = tax_repository

    async def calculate_tax(
        self,
        parcel: Parcel,
        assessment_year: int,
        land_use_category: Optional[LandUseCategory] = None,
        exemptions: Optional[Decimal] = None,
        current_year: Optional[int] = None
    ) -> dict:
        """
        Calculate tax liability for a parcel including exemptions.

        Args:
            parcel: Parcel entity with area and land use category
            assessment_year: Year for which tax is being calculated
            land_use_category: Optional override of parcel's land use category
            exemptions: Optional exemption amount to deduct from gross tax
            current_year: Optional override for current year (defaults to system date)

        Returns:
            Dictionary containing gross_tax, exemptions_applied, and net_tax_due
        """
        category = land_use_category or parcel.land_use_category
        if not category:
            return {
                "gross_tax": Decimal("0.00"),
                "exemptions_applied": Decimal("0.00"),
                "net_tax_due": Decimal("0.00"),
            }

        rate = await self._get_tax_rate(category, assessment_year)
        
        # Safely convert area to Decimal
        area = Decimal(str(parcel.area_hectares))
        
        gross_tax = area * rate
        gross_tax = gross_tax.quantize(Decimal("0.01"))
        
        exemptions_applied = exemptions or Decimal("0.00")
        exemptions_applied = exemptions_applied.quantize(Decimal("0.01"))
        
        net_tax_due = gross_tax - exemptions_applied
        if net_tax_due < Decimal("0.00"):
            net_tax_due = Decimal("0.00")
        net_tax_due = net_tax_due.quantize(Decimal("0.01"))
        
        return {
            "gross_tax": gross_tax,
            "exemptions_applied": exemptions_applied,
            "net_tax_due": net_tax_due,
        }

    async def calculate_with_existing_record(
        self,
        parcel_id: UUID,
        assessment_year: int,
        current_year: Optional[int] = None
    ) -> Optional[dict]:
        """
        Calculate tax using existing tax record if available.

        Args:
            parcel_id: UUID of the parcel
            assessment_year: Year for which tax is being calculated
            current_year: Optional override for current year

        Returns:
            Dictionary with tax calculation details or None if no record
        """
        tax_record = await self.tax_repository.get_by_parcel_and_year(
            parcel_id, assessment_year
        )

        if not tax_record:
            return None

        return {
            "tax_record_id": str(tax_record.id),
            "parcel_id": str(tax_record.parcel_id),
            "assessment_year": tax_record.assessment_year,
            "assessed_value": tax_record.assessed_value,
            "tax_amount": tax_record.tax_amount,
            "exemptions": tax_record.exemptions,
            "net_tax_due": tax_record.net_tax_due,
        }

    async def get_current_assessment(
        self,
        parcel_id: UUID,
        current_year: Optional[int] = None
    ) -> Optional[TaxRecord]:
        """
        Get current year's tax assessment for a parcel.

        Args:
            parcel_id: UUID of the parcel
            current_year: Optional override for current year

        Returns:
            TaxRecord for current year if exists, None otherwise
        """
        if current_year is None:
            current_year = date.today().year
        
        return await self.tax_repository.get_by_parcel_and_year(
            parcel_id, current_year
        )

    async def _get_tax_rate(
        self,
        land_use_category: LandUseCategory,
        assessment_year: int
    ) -> Decimal:
        """
        Get tax rate for a land use category for a given year.

        Args:
            land_use_category: Land use category entity
            assessment_year: Year for rate determination

        Returns:
            Tax rate as Decimal (amount per hectare)
        """
        rate_schedule = await self.tax_repository.get_rate_schedule(
            land_use_category.id, assessment_year
        )

        if rate_schedule:
            return rate_schedule.rate_per_hectare

        default_rate = land_use_category.default_tax_rate
        if default_rate is None:
            return Decimal("0.00")
        
        return default_rate