# tests/unit/test_tax_assessment_generator.py
"""
Unit tests for AssessmentGenerator.
"""
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.models.parcel import Parcel
from app.models.tax_record import TaxRecord
from app.repositories.tax_repository import TaxRepository
from app.services.tax.assessment_generator import AssessmentGenerator
from app.services.tax.tax_calculator import TaxCalculator
from app.services.tax.penalty_engine import PenaltyEngine


class TestAssessmentGenerator:
    """Test suite for AssessmentGenerator."""

    @pytest.fixture
    def mock_repo(self):
        return AsyncMock(spec=TaxRepository)

    @pytest.fixture
    def mock_calculator(self):
        return AsyncMock(spec=TaxCalculator)

    @pytest.fixture
    def mock_penalty_engine(self):
        return AsyncMock(spec=PenaltyEngine)

    @pytest.fixture
    def generator(self, mock_repo, mock_calculator, mock_penalty_engine):
        return AssessmentGenerator(mock_repo, mock_calculator, mock_penalty_engine)

    @pytest.fixture
    def mock_parcel(self):
        parcel = MagicMock(spec=Parcel)
        parcel.id = str(uuid4())
        parcel.upi = "UPI-001"
        parcel.area_sqm = 1000.0
        parcel.valuation = 500000.0
        return parcel

    async def test_generate_assessment_creates_record(self, generator, mock_repo, mock_calculator, mock_parcel):
        """Generate a single assessment and persist it."""
        mock_calculator.calculate_tax.return_value = {
            "assessed_value": Decimal("500000.00"),
            "tax_rate_applied": Decimal("0.05"),
            "base_tax_amount": Decimal("50.00"),
            "penalties_amount": Decimal("0.00"),
            "total_amount": Decimal("50.00"),
        }
        mock_repo.create.return_value = MagicMock(spec=TaxRecord, id=uuid4())
        result = await generator.generate_assessment(
            parcel=mock_parcel,
            assessment_year=2024,
        )
        assert result is not None
        mock_calculator.calculate_tax.assert_awaited_once()

    async def test_generate_assessments_for_parish_empty(self, generator, mock_repo):
        """Empty parish returns zero counts."""
        mock_repo.get_parcels_by_parish.return_value = []
        result = await generator.generate_assessments_for_parish(str(uuid4()), 2024)
        assert result["generated_count"] == 0
        assert result["skipped_count"] == 0

    async def test_generate_assessments_for_parish_skips_existing(self, generator, mock_repo, mock_parcel):
        """Existing assessments are skipped."""
        mock_repo.get_parcels_by_parish.return_value = [mock_parcel]
        mock_repo.get_existing_assessments_map.return_value = {str(mock_parcel.id): MagicMock(spec=TaxRecord)}
        result = await generator.generate_assessments_for_parish(str(uuid4()), 2024)
        assert result["skipped_count"] == 1
        assert result["generated_count"] == 0

    async def test_generate_assessments_for_parish_generates_new(self, generator, mock_repo, mock_parcel):
        """Generates assessments for parcels without existing records."""
        mock_repo.get_parcels_by_parish.return_value = [mock_parcel]
        mock_repo.get_existing_assessments_map.return_value = {}
        created_record = MagicMock(spec=TaxRecord)
        created_record.assessed_value = 500000.0
        created_record.total_amount = 50.0
        mock_repo.create.return_value = created_record
        result = await generator.generate_assessments_for_parish(str(uuid4()), 2024)
        assert result["generated_count"] == 1
        assert result["skipped_count"] == 0

    async def test_regenerate_assessment_deletes_existing(self, generator, mock_repo, mock_parcel):
        """Regenerate overwrites existing assessment by soft delete."""
        mock_repo.get_parcel.return_value = mock_parcel
        existing = MagicMock(spec=TaxRecord)
        existing.id = str(uuid4())
        mock_repo.get_by_parcel_and_year.return_value = existing
        mock_repo.create.return_value = MagicMock(spec=TaxRecord)
        result = await generator.regenerate_assessment(mock_parcel.id, 2024)
        assert result is not None
        mock_repo.soft_delete.assert_awaited_once_with(existing.id)

    async def test_regenerate_assessment_returns_none_when_parcel_missing(self, generator, mock_repo):
        """Returns None when parcel not found."""
        mock_repo.get_parcel.return_value = None
        result = await generator.regenerate_assessment(str(uuid4()), 2024)
        assert result is None

    async def test_get_assessment_document_returns_none_when_missing(self, generator, mock_repo):
        """Returns None when assessment does not exist."""
        mock_repo.get_by_parcel_and_year.return_value = None
        result = await generator.get_assessment_document(str(uuid4()), 2024)
        assert result is None

    async def test_get_assessment_document_returns_formatted(self, generator, mock_repo, mock_parcel):
        """Returns formatted assessment document data."""
        record = MagicMock(spec=TaxRecord)
        record.assessment_year = 2024
        record.due_date = date(2025, 3, 31)
        record.assessed_value = 500000.0
        record.tax_rate_applied = 0.05
        record.base_tax_amount = 50.0
        record.penalties_amount = 0.0
        record.total_amount = 50.0
        record.status = "pending"
        mock_repo.get_by_parcel_and_year.return_value = record
        mock_repo.get_parcel.return_value = mock_parcel
        result = await generator.get_assessment_document(mock_parcel.id, 2024)
        assert result["assessment_id"] == str(record.id)
        assert result["parcel"]["upi"] == mock_parcel.upi

    def test_get_due_date_for_year(self, generator):
        """Due date is March 31 of the following year."""
        assert generator._get_due_date_for_year(2024) == date(2025, 3, 31)