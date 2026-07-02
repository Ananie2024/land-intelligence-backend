# tests/unit/test_tax_calculator.py
"""
Unit tests for TaxCalculator.
"""
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from app.models.land_use_category import LandUseCategory
from app.models.parcel import Parcel
from app.models.tax_record import TaxRecord
from app.repositories.tax_repository import TaxRepository
from app.services.tax.tax_calculator import TaxCalculator


class TestTaxCalculator:
    """Test suite for TaxCalculator."""

    @pytest.fixture
    def mock_repo(self):
        """Create a mock TaxRepository."""
        return AsyncMock(spec=TaxRepository)

    @pytest.fixture
    def calculator(self, mock_repo):
        """Create a TaxCalculator with mock repository."""
        return TaxCalculator(mock_repo)

    @pytest.fixture
    def mock_parcel(self):
        """Create a mock Parcel."""
        parcel = MagicMock(spec=Parcel)
        parcel.id = "parcel-1"
        parcel.area_sqm = 1000.0
        parcel.valuation = 500000.0
        parcel.land_use_category = None
        return parcel

    @pytest.fixture
    def mock_category(self):
        """Create a mock LandUseCategory."""
        category = MagicMock(spec=LandUseCategory)
        category.id = "category-1"
        category.name = "Residential"
        category.base_tax_rate = Decimal("0.05")
        return category

    async def test_calculate_tax_no_category_returns_zero(self, calculator, mock_parcel):
        """When no land use category, should return zero amounts."""
        result = await calculator.calculate_tax(
            parcel=mock_parcel,
            assessment_year=2024,
        )
        assert result["base_tax_amount"] == Decimal("0.00")
        assert result["total_amount"] == Decimal("0.00")

    async def test_calculate_tax_with_category(self, calculator, mock_parcel, mock_category):
        """Standard tax calculation with valid category."""
        result = await calculator.calculate_tax(
            parcel=mock_parcel,
            assessment_year=2024,
            land_use_category=mock_category,
        )
        assert result["tax_rate_applied"] == Decimal("0.05")
        assert result["assessed_value"] == Decimal("500000.00")
        expected_base = Decimal("1000.0") * Decimal("0.05")
        assert result["base_tax_amount"] == expected_base.quantize(Decimal("0.01"))
        assert result["exemptions_applied"] == Decimal("0.00")
        assert result["net_tax_due"] == result["base_tax_amount"]

    async def test_calculate_tax_with_category_none_rate(self, calculator, mock_parcel):
        """Category with None base_tax_rate should return zero tax."""
        category = MagicMock(spec=LandUseCategory)
        category.base_tax_rate = None
        result = await calculator.calculate_tax(
            parcel=mock_parcel,
            assessment_year=2024,
            land_use_category=category,
        )
        assert result["tax_rate_applied"] == Decimal("0.00")
        assert result["base_tax_amount"] == Decimal("0.00")

    async def test_calculate_tax_with_exemptions(self, calculator, mock_parcel, mock_category):
        """Exemptions reduce base tax amount."""
        result = await calculator.calculate_tax(
            parcel=mock_parcel,
            assessment_year=2024,
            land_use_category=mock_category,
            exemptions=Decimal("10.00"),
        )
        assert result["exemptions_applied"] == Decimal("10.00")
        base = Decimal("1000.0") * Decimal("0.05")
        expected_total = (base - Decimal("10.00")).quantize(Decimal("0.01"))
        assert result["total_amount"] == expected_total

    async def test_calculate_tax_exemptions_exceed_base_sets_zero(self, calculator, mock_parcel, mock_category):
        """If exemptions exceed base tax, total should be zero not negative."""
        result = await calculator.calculate_tax(
            parcel=mock_parcel,
            assessment_year=2024,
            land_use_category=mock_category,
            exemptions=Decimal("999999.00"),
        )
        assert result["total_amount"] == Decimal("0.00")
        assert result["net_tax_due"] == Decimal("0.00")

    async def test_calculate_tax_parcel_valuation_none(self, calculator, mock_parcel, mock_category):
        """Parcel with None valuation should default to 0."""
        mock_parcel.valuation = None
        result = await calculator.calculate_tax(
            parcel=mock_parcel,
            assessment_year=2024,
            land_use_category=mock_category,
        )
        assert result["assessed_value"] == Decimal("0.00")

    async def test_calculate_with_existing_record_returns_none_when_no_record(self, calculator, mock_repo):
        """When no tax record exists, return None."""
        mock_repo.get_by_parcel_and_year.return_value = None
        result = await calculator.calculate_with_existing_record("parcel-1", 2024)
        assert result is None

    async def test_calculate_with_existing_record_returns_record_data(self, calculator, mock_repo):
        """When tax record exists, return record details."""
        mock_record = MagicMock(spec=TaxRecord)
        mock_record.id = "record-1"
        mock_record.parcel_id = "parcel-1"
        mock_record.assessment_year = 2024
        mock_record.assessed_value = 100.0
        mock_record.tax_rate_applied = 0.05
        mock_record.base_tax_amount = 5.0
        mock_record.penalties_amount = 0.0
        mock_record.total_amount = 5.0
        mock_repo.get_by_parcel_and_year.return_value = mock_record
        result = await calculator.calculate_with_existing_record("parcel-1", 2024)
        assert result["tax_record_id"] == "record-1"
        assert result["base_tax_amount"] == 5.0

    async def test_get_current_assessment_returns_none_when_no_record(self, calculator, mock_repo):
        """get_current_assessment returns None when no current year record."""
        mock_repo.get_by_parcel_and_year.return_value = None
        result = await calculator.get_current_assessment("parcel-1")
        assert result is None

    async def test_get_current_assessment_uses_current_year(self, calculator, mock_repo):
        """get_current_assessment defaults to current year."""
        mock_repo.get_by_parcel_and_year.return_value = None
        await calculator.get_current_assessment("parcel-1")
        called_year = mock_repo.get_by_parcel_and_year.call_args[0][1]
        assert called_year == str(date.today().year)

    async def test_get_current_assessment_with_override(self, calculator, mock_repo):
        """get_current_assessment respects current_year override."""
        mock_repo.get_by_parcel_and_year.return_value = None
        await calculator.get_current_assessment("parcel-1", current_year=2020)
        called_year = mock_repo.get_by_parcel_and_year.call_args[0][1]
        assert called_year == "2020"

    async def test_calculate_tax_string_year(self, calculator, mock_parcel, mock_category):
        """assessment_year can be a string."""
        result = await calculator.calculate_tax(
            parcel=mock_parcel,
            assessment_year="2024",
            land_use_category=mock_category,
        )
        assert result["tax_rate_applied"] == Decimal("0.05")