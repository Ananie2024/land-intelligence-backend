# app/services/tax/assessment_generator.py
"""
Service module for generating annual assessment documents.

Responsibility: Generates annual assessment documents.
Scope: Phase 3 - Backend API & Services
"""

import asyncio
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from app.models.parcel import Parcel
from app.models.tax_record import TaxRecord
from app.repositories.tax_repository import TaxRepository
from app.services.tax.penalty_engine import PenaltyEngine
from app.services.tax.tax_calculator import TaxCalculator


class AssessmentGenerator:
    """
    Generates annual tax assessment documents for land parcels.
    """

    def __init__(
        self,
        tax_repository: TaxRepository,
        tax_calculator: TaxCalculator,
        penalty_engine: PenaltyEngine
    ):
        """
        Initialize the assessment generator with dependencies.

        Args:
            tax_repository: Repository for tax record operations
            tax_calculator: Calculator for tax liability
            penalty_engine: Engine for penalty calculations
        """
        self.tax_repository = tax_repository
        self.tax_calculator = tax_calculator
        self.penalty_engine = penalty_engine

    async def generate_assessment(
        self,
        parcel: Parcel,
        assessment_year: int,
        exemptions: Optional[Decimal] = None
    ) -> TaxRecord:
        """
        Generate a new tax assessment for a parcel.

        Args:
            parcel: Parcel entity to assess
            assessment_year: Year of assessment
            exemptions: Optional exemption amount

        Returns:
            Created TaxRecord entity
        """
        # Calculate tax liability
        calculation = await self.tax_calculator.calculate_tax(
            parcel=parcel,
            assessment_year=assessment_year,
            exemptions=exemptions
        )

        # Create assessment record
        tax_record = TaxRecord(
            id=uuid4(),
            parcel_id=parcel.id,
            assessment_year=assessment_year,
            assessed_value=calculation["gross_tax"],
            tax_amount=calculation["gross_tax"],
            exemptions=calculation["exemptions_applied"],
            net_tax_due=calculation["net_tax_due"],
            assessment_date=date.today(),
            status="pending"
        )

        return await self.tax_repository.create(tax_record)

    async def generate_assessments_for_parish(
        self,
        parish_id: UUID,
        assessment_year: int,
        exemptions: Optional[Decimal] = None,
        chunk_size: int = 100
    ) -> dict:
        """
        Generate assessments for all parcels in a parish with batch processing.

        Args:
            parish_id: UUID of the parish
            assessment_year: Year of assessment
            exemptions: Optional exemption amount for all parcels
            chunk_size: Number of parcels to process concurrently per chunk

        Returns:
            Dictionary with generation summary
        """
        parcels = await self.tax_repository.get_parcels_by_parish(parish_id)
        
        if not parcels:
            return {
                "parish_id": str(parish_id),
                "assessment_year": assessment_year,
                "generated_count": 0,
                "skipped_count": 0,
                "total_assessed_value": Decimal("0.00"),
                "total_net_due": Decimal("0.00"),
            }

        # Batch fetch existing assessments
        parcel_ids = [p.id for p in parcels]
        existing_map = await self.tax_repository.get_existing_assessments_map(
            parcel_ids, assessment_year
        )

        # Filter parcels needing assessment
        parcels_to_generate = [
            p for p in parcels if p.id not in existing_map
        ]

        generated_count = 0
        skipped_count = len([p for p in parcels if p.id in existing_map])
        total_assessed_value = Decimal("0.00")
        total_net_due = Decimal("0.00")

        # Process in chunks to avoid overwhelming the database
        for i in range(0, len(parcels_to_generate), chunk_size):
            chunk = parcels_to_generate[i:i + chunk_size]
            
            # Generate assessments concurrently for the chunk
            tasks = [
                self.generate_assessment(parcel, assessment_year, exemptions)
                for parcel in chunk
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    # Log exception but continue with other assessments
                    continue
                
                generated_count += 1
                total_assessed_value += result.assessed_value
                total_net_due += result.net_tax_due

        return {
            "parish_id": str(parish_id),
            "assessment_year": assessment_year,
            "generated_count": generated_count,
            "skipped_count": skipped_count,
            "total_assessed_value": total_assessed_value.quantize(Decimal("0.01")),
            "total_net_due": total_net_due.quantize(Decimal("0.01")),
        }

    async def regenerate_assessment(
        self,
        parcel_id: UUID,
        assessment_year: int,
        exemptions: Optional[Decimal] = None
    ) -> Optional[TaxRecord]:
        """
        Regenerate an existing assessment (overwrites) with transaction safety.

        Args:
            parcel_id: UUID of the parcel
            assessment_year: Year of assessment
            exemptions: Optional exemption amount

        Returns:
            Updated TaxRecord or None if parcel not found
        """
        parcel = await self.tax_repository.get_parcel(parcel_id)
        if not parcel:
            return None

        # Use transactional context for safety
        async with self.tax_repository.transaction():
            # Delete existing assessment
            existing = await self.tax_repository.get_by_parcel_and_year(
                parcel_id, assessment_year
            )
            if existing:
                await self.tax_repository.delete(existing.id)

            # Generate new assessment within same transaction
            return await self.generate_assessment(parcel, assessment_year, exemptions)

    async def get_assessment_document(
        self,
        parcel_id: UUID,
        assessment_year: int
    ) -> Optional[dict]:
        """
        Get assessment data formatted for document generation.
        Preserves Decimal precision for financial values.

        Args:
            parcel_id: UUID of the parcel
            assessment_year: Year of assessment

        Returns:
            Dictionary with assessment details or None if not found
        """
        tax_record = await self.tax_repository.get_by_parcel_and_year(
            parcel_id, assessment_year
        )
        
        if not tax_record:
            return None

        parcel = await self.tax_repository.get_parcel(parcel_id)
        
        return {
            "assessment_id": str(tax_record.id),
            "parcel": {
                "id": str(parcel.id),
                "parcel_number": parcel.parcel_number,
                "area_hectares": str(parcel.area_hectares),  # String to preserve precision
            },
            "assessment_year": tax_record.assessment_year,
            "assessment_date": tax_record.assessment_date.isoformat(),
            "assessed_value": str(tax_record.assessed_value),  # String preserves Decimal
            "exemptions": str(tax_record.exemptions),  # String preserves Decimal
            "net_tax_due": str(tax_record.net_tax_due),  # String preserves Decimal
            "status": tax_record.status,
        }