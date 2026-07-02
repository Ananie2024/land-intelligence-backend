# tests/unit/test_tax_penalty_engine.py
"""
Unit tests for PenaltyEngine.
"""
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from app.models.tax_record import TaxRecord
from app.repositories.tax_repository import TaxRepository
from app.services.tax.penalty_engine import PenaltyEngine


class TestPenaltyEngine:
    """Test suite for PenaltyEngine."""

    @pytest.fixture
    def mock_repo(self):
        return AsyncMock(spec=TaxRepository)

    @pytest.fixture
    def engine(self, mock_repo):
        return PenaltyEngine(mock_repo)

    @pytest.fixture
    def mock_tax_record(self):
        record = MagicMock(spec=TaxRecord)
        record.id = "record-1"
        record.parcel_id = "parcel-1"
        record.assessment_year = 2024
        record.total_amount = 100.0
        record.due_date = date(2024, 12, 31)
        record.status = "pending"
        return record

    async def test_calculate_penalty_not_overdue(self, engine, mock_tax_record):
        """No penalty when current date <= due date."""
        result = await engine.calculate_penalty(
            tax_record=mock_tax_record,
            due_date=date(2099, 12, 31),
            current_date=date(2024, 6, 1),
        )
        assert result["base_penalty"] == Decimal("0.00")
        assert result["interest_accrued"] == Decimal("0.00")
        assert result["total_due"] == Decimal(str(mock_tax_record.total_amount))

    async def test_calculate_penalty_zero_principal(self, engine):
        """No penalty on zero balance."""
        record = MagicMock(spec=TaxRecord)
        record.total_amount = 0.0
        record.due_date = date(2020, 1, 1)
        result = await engine.calculate_penalty(
            tax_record=record,
            due_date=date(2020, 1, 1),
            current_date=date(2024, 6, 1),
        )
        assert result["base_penalty"] == Decimal("0.00")
        assert result["interest_accrued"] == Decimal("0.00")
        assert result["total_due"] == Decimal("0.00")

    async def test_calculate_penalty_overdue(self, engine, mock_tax_record):
        """Penalty and interest accrue when overdue."""
        result = await engine.calculate_penalty(
            tax_record=mock_tax_record,
            due_date=date(2024, 1, 1),
            current_date=date(2024, 4, 1),
        )
        assert result["base_penalty"] > Decimal("0.00")
        assert result["interest_accrued"] > Decimal("0.00")
        assert result["total_due"] == Decimal(str(mock_tax_record.total_amount)) + result["base_penalty"] + result["interest_accrued"]

    async def test_calculate_penalty_uses_remaining_balance(self, engine, mock_tax_record):
        """When remaining_balance is provided, it is used as principal."""
        result = await engine.calculate_penalty(
            tax_record=mock_tax_record,
            due_date=date(2024, 1, 1),
            current_date=date(2024, 4, 1),
            remaining_balance=Decimal("50.00"),
        )
        assert result["base_penalty"] == (Decimal("50.00") * Decimal("0.10")).quantize(Decimal("0.01"))

    async def test_calculate_penalty_for_parcel_returns_none_when_missing(self, engine, mock_repo):
        """Returns None when no tax record exists."""
        mock_repo.get_by_parcel_and_year.return_value = None
        result = await engine.calculate_penalty_for_parcel(
            parcel_id="parcel-1",
            assessment_year=2024,
            due_date=date(2024, 12, 31),
        )
        assert result is None

    async def test_calculate_penalty_for_parcel_computes_remaining(self, engine, mock_repo, mock_tax_record):
        """Computes remaining balance via repository when not provided."""
        mock_repo.get_by_parcel_and_year.return_value = mock_tax_record
        mock_repo.get_total_paid_for_assessment.return_value = 20.0
        result = await engine.calculate_penalty_for_parcel(
            parcel_id="parcel-1",
            assessment_year=2024,
            due_date=date(2024, 1, 1),
            current_date=date(2024, 4, 1),
        )
        assert result is not None
        assert result["base_penalty"] > Decimal("0.00")

    async def test_calculate_penalty_on_balance_zero(self, engine):
        """Zero balance returns zero penalties."""
        engine.calculate_penalty_on_balance = AsyncMock(return_value={
            "base_penalty": Decimal("0.00"),
            "interest_accrued": Decimal("0.00"),
            "total_due": Decimal("0.00"),
        })
        result = await engine.calculate_penalty_on_balance(
            remaining_balance=Decimal("0.00"),
            due_date=date(2024, 1, 1),
            current_date=date(2024, 6, 1),
        )
        assert result["total_due"] == Decimal("0.00")

    async def test_calculate_penalty_on_balance_overdue(self, engine):
        """Overdue balance produces penalty and interest."""
        engine.calculate_penalty_on_balance = AsyncMock(return_value={
            "base_penalty": Decimal("10.00"),
            "interest_accrued": Decimal("2.00"),
            "total_due": Decimal("112.00"),
        })
        result = await engine.calculate_penalty_on_balance(
            remaining_balance=Decimal("100.00"),
            due_date=date(2024, 1, 1),
            current_date=date(2024, 4, 1),
        )
        assert result["base_penalty"] > Decimal("0.00")
        assert result["interest_accrued"] > Decimal("0.00")

    async def test_calculate_outstanding_penalty_empty_assessments(self, engine, mock_repo):
        """Returns zero totals when no assessments."""
        mock_repo.get_all_assessments_for_parcel.return_value = []
        result = await engine.calculate_outstanding_penalty("parcel-1")
        assert result["total_net_due"] == Decimal("0.00")
        assert result["overdue_assessments_count"] == 0

    async def test_calculate_outstanding_penalty_with_assessments(self, engine, mock_repo, mock_tax_record):
        """Aggregates totals across assessments."""
        mock_repo.get_all_assessments_for_parcel.return_value = [mock_tax_record]
        mock_repo.get_total_paid_for_assessment.return_value = 0.0
        result = await engine.calculate_outstanding_penalty("parcel-1", current_date=date(2024, 6, 1))
        assert result["total_assessments_count"] == 1
        assert result["total_net_due"] == Decimal(str(mock_tax_record.total_amount))

    async def test_get_due_date_for_year(self, engine):
        """Due date is March 31 of the following year."""
        assert engine._get_due_date_for_year(2024) == date(2025, 3, 31)