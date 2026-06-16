# app/services/tax/tax_calculator.py
"""
Service module for computing tax liability per parcel and land use.

Responsibility: Computes tax liability per parcel + land use.
Scope: Phase 3 - Backend API & Services
"""

from datetime import date
from decimal import Decimal
from typing import Optional, Union

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
        assessment_year: Union[int, str],
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
            Dictionary containing tax fields aligned with TaxRecord.
        """
        category = land_use_category or parcel.land_use_category
        if not category:
            return {
                "assessed_value": Decimal("0.00"),
                "tax_rate_applied": Decimal("0.00"),
                "base_tax_amount": Decimal("0.00"),
                "penalties_amount": Decimal("0.00"),
                "total_amount": Decimal("0.00"),
                "gross_tax": Decimal("0.00"),
                "exemptions_applied": Decimal("0.00"),
                "net_tax_due": Decimal("0.00"),
            }

        rate = await self._get_tax_rate(category, assessment_year)
        
        area = Decimal(str(parcel.area_sqm))
        
        base_tax_amount = area * rate
        base_tax_amount = base_tax_amount.quantize(Decimal("0.01"))
        
        exemptions_applied = exemptions or Decimal("0.00")
        exemptions_applied = exemptions_applied.quantize(Decimal("0.01"))
        
        total_amount = base_tax_amount - exemptions_applied
        if total_amount < Decimal("0.00"):
            total_amount = Decimal("0.00")
        total_amount = total_amount.quantize(Decimal("0.01"))

        assessed_value = Decimal(str(parcel.valuation or 0)).quantize(Decimal("0.01"))
        
        return {
            "assessed_value": assessed_value,
            "tax_rate_applied": rate,
            "base_tax_amount": base_tax_amount,
            "penalties_amount": Decimal("0.00"),
            "total_amount": total_amount,
            # Backward-compatible keys for older service code.
            "gross_tax": base_tax_amount,
            "exemptions_applied": exemptions_applied,
            "net_tax_due": total_amount,
        }

    async def calculate_with_existing_record(
        self,
        parcel_id: str,
        assessment_year: Union[int, str],
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
            "tax_rate_applied": tax_record.tax_rate_applied,
            "base_tax_amount": tax_record.base_tax_amount,
            "penalties_amount": tax_record.penalties_amount,
            "total_amount": tax_record.total_amount,
        }

    async def get_current_assessment(
        self,
        parcel_id: str,
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
            parcel_id, str(current_year)
        )

    async def _get_tax_rate(
        self,
        land_use_category: LandUseCategory,
        assessment_year: Union[int, str]
    ) -> Decimal:
        """
        Get tax rate for a land use category for a given year.

        Args:
            land_use_category: Land use category entity
            assessment_year: Year for rate determination

        Returns:
            Tax rate as Decimal.
        """
        default_rate = land_use_category.base_tax_rate
        if default_rate is None:
            return Decimal("0.00")
        
        return Decimal(str(default_rate))
