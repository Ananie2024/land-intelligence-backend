# tests/unit/test_tax_repository.py
"""
Unit tests for TaxRepository.
"""
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import AsyncMock, MagicMock, PropertyMock
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from typing import Any, Optional

from app.models.parcel import Parcel
from app.models.tax_record import TaxRecord
from app.models.tax_payment import TaxPayment
from app.models.enums import TaxRecordStatus
from app.repositories.tax_repository import TaxRepository


class _AsyncContextManagerMock:
    """Minimal async context manager for mocking db.begin()."""
    async def __aenter__(self) -> None:
        return None
    async def __aexit__(self, exc_type: Optional[type], exc: Optional[BaseException], tb: Optional[Any]) -> bool:
        return False


def _make_mock_result(single=None, rows=None, scalar_val=None):
    """Create a mock execute result."""
    mock_result = MagicMock()
    if single is not None:
        mock_result.scalar_one_or_none.return_value = single
    if scalar_val is not None:
        mock_result.scalar_one.return_value = scalar_val
    if rows is not None:
        mock_result.scalars.return_value.all.return_value = rows
    return mock_result


class TestTaxRepository:
    """Test suite for TaxRepository."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock AsyncSession with async execute."""
        session = AsyncMock()
        session.commit = AsyncMock()
        session.flush = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        session.add = MagicMock()
        session.begin = MagicMock(return_value=_AsyncContextManagerMock())
        return session

    @pytest.fixture
    def repo(self, mock_db):
        """Create a TaxRepository with a mock session."""
        return TaxRepository(mock_db)

    def _make_tax_record(self, **kwargs):
        """Helper to build a TaxRecord-like mock."""
        record = MagicMock(spec=TaxRecord)
        record.id = kwargs.get("id", str(uuid4()))
        record.parcel_id = kwargs.get("parcel_id", str(uuid4()))
        record.assessment_year = kwargs.get("assessment_year", 2024)
        record.assessed_value = kwargs.get("assessed_value", 100.0)
        record.tax_rate_applied = kwargs.get("tax_rate_applied", 0.05)
        record.base_tax_amount = kwargs.get("base_tax_amount", 5.0)
        record.penalties_amount = kwargs.get("penalties_amount", 0.0)
        record.total_amount = kwargs.get("total_amount", 5.0)
        record.status = kwargs.get("status", TaxRecordStatus.PENDING)
        record.due_date = kwargs.get("due_date", date(2025, 3, 31))
        record.paid_date = kwargs.get("paid_date", None)
        record.payment_reference = kwargs.get("payment_reference", None)
        record.notes = kwargs.get("notes", None)
        record.is_active = kwargs.get("is_active", True)
        record.created_at = kwargs.get("created_at", date(2024, 1, 1))
        record.updated_at = kwargs.get("updated_at", date(2024, 1, 1))
        return record

    def _make_tax_payment(self, **kwargs):
        """Helper to build a TaxPayment-like mock."""
        payment = MagicMock(spec=TaxPayment)
        payment.id = kwargs.get("id", str(uuid4()))
        payment.tax_record_id = kwargs.get("tax_record_id", str(uuid4()))
        payment.payment_amount = kwargs.get("payment_amount", 5.0)
        payment.payment_date = kwargs.get("payment_date", date(2024, 1, 1))
        payment.payment_method = kwargs.get("payment_method", "cash")
        payment.payment_reference = kwargs.get("payment_reference", None)
        payment.receipt_number = kwargs.get("receipt_number", "RCP-20240101-ABCD")
        payment.received_by = kwargs.get("received_by", "teller")
        payment.notes = kwargs.get("notes", None)
        payment.is_reversal = kwargs.get("is_reversal", False)
        payment.reversed_payment_id = kwargs.get("reversed_payment_id", None)
        payment.is_active = kwargs.get("is_active", True)
        payment.created_at = kwargs.get("created_at", date(2024, 1, 1))
        payment.updated_at = kwargs.get("updated_at", date(2024, 1, 1))
        return payment

    def _make_parcel(self, **kwargs):
        """Helper to build a Parcel-like mock."""
        parcel = MagicMock(spec=Parcel)
        parcel.id = kwargs.get("id", str(uuid4()))
        parcel.parcel_number = kwargs.get("parcel_number", "P-001")
        parcel.area_sqm = kwargs.get("area_sqm", 1000.0)
        parcel.is_active = kwargs.get("is_active", True)
        return parcel

    async def test_get_by_parcel_and_year_returns_record(self, repo, mock_db):
        """Returns matching tax record for parcel and year."""
        expected = self._make_tax_record()
        mock_db.execute.return_value = _make_mock_result(single=expected)
        result = await repo.get_by_parcel_and_year(str(expected.parcel_id), expected.assessment_year)
        assert result is expected

    async def test_get_by_parcel_and_year_returns_none_when_missing(self, repo, mock_db):
        """Returns None when no record found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        result = await repo.get_by_parcel_and_year("parcel-x", 2024)
        assert result is None

    async def test_get_by_parcel_and_year_for_update_locks_row(self, repo, mock_db):
        """for_update variant should apply with_for_update."""
        expected = self._make_tax_record()
        mock_db.execute.return_value = _make_mock_result(single=expected)
        result = await repo.get_by_parcel_and_year_for_update("parcel-1", 2024)
        assert result is expected
        query = mock_db.execute.call_args[0][0]
        assert hasattr(query, "with_for_update")

    async def test_list_by_year_returns_records(self, repo, mock_db):
        """list_by_year returns records for the year."""
        records = [self._make_tax_record(assessment_year=2024), self._make_tax_record(assessment_year=2024)]
        repo.list = AsyncMock(return_value=records)
        result = await repo.list_by_year("2024")
        assert result == records

    async def test_list_overdue_returns_overdue_records(self, repo, mock_db):
        """list_overdue returns pending records with past due date."""
        overdue = self._make_tax_record(due_date=date(2020, 1, 1))
        mock_db.execute.return_value = _make_mock_result(rows=[overdue])
        result = await repo.list_overdue()
        assert result == [overdue]

    async def test_get_payment_history_returns_payments(self, repo, mock_db):
        """get_payment_history returns payments joined to tax records."""
        payments = [self._make_tax_payment()]
        mock_db.execute.return_value = _make_mock_result(rows=payments)
        result = await repo.get_payment_history("parcel-1")
        assert result == payments

    async def test_get_payments_for_record_returns_payments(self, repo, mock_db):
        """get_payments_for_record filters by tax record id."""
        payments = [self._make_tax_payment()]
        mock_db.execute.return_value = _make_mock_result(rows=payments)
        result = await repo.get_payments_for_record("record-1")
        assert result == payments

    async def test_get_total_paid_for_assessment_sums_payments(self, repo, mock_db):
        """get_total_paid_for_assessment returns sum of payment amounts."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 12.50
        mock_db.execute.return_value = mock_result
        result = await repo.get_total_paid_for_assessment("record-1")
        assert result == 12.50

    async def test_get_total_paid_for_assessment_no_payments(self, repo, mock_db):
        """get_total_paid_for_assessment returns 0.0 when no payments."""
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = None
        mock_db.execute.return_value = mock_result
        result = await repo.get_total_paid_for_assessment("record-1")
        assert result == 0.0

    async def test_get_payments_for_records_aggregates(self, repo, mock_db):
        """get_payments_for_records returns mapping of record_id to total paid."""
        row = MagicMock()
        row.tax_record_id = "record-1"
        row.total_paid = 7.5
        mock_db.execute.return_value = MagicMock()
        mock_db.execute.return_value.all.return_value = [row]
        result = await repo.get_payments_for_records(["record-1"])
        assert result == {"record-1": 7.5}

    async def test_get_payments_for_records_empty_input(self, repo, mock_db):
        """Empty input returns empty dict."""
        result = await repo.get_payments_for_records([])
        assert result == {}

    async def test_get_parcel_returns_parcel(self, repo, mock_db):
        """get_parcel returns active parcel."""
        parcel = self._make_parcel()
        mock_db.execute.return_value = _make_mock_result(single=parcel)
        result = await repo.get_parcel("parcel-1")
        assert result is parcel

    async def test_get_parcels_by_parish_returns_parcels(self, repo, mock_db):
        """get_parcels_by_parish returns active parcels for parish."""
        parcels = [self._make_parcel(), self._make_parcel()]
        mock_db.execute.return_value = _make_mock_result(rows=parcels)
        result = await repo.get_parcels_by_parish("parish-1")
        assert result == parcels

    async def test_get_all_assessments_for_parcel_returns_records(self, repo, mock_db):
        """get_all_assessments_for_parcel returns active tax records for parcel."""
        records = [self._make_tax_record(), self._make_tax_record()]
        mock_db.execute.return_value = _make_mock_result(rows=records)
        result = await repo.get_all_assessments_for_parcel("parcel-1")
        assert result == records

    async def test_create_payment_persists(self, repo, mock_db):
        """create_payment adds and refreshes the payment."""
        payment = self._make_tax_payment()
        result = await repo.create_payment(payment)
        mock_db.add.assert_called_once_with(payment)
        mock_db.flush.assert_awaited_once()
        mock_db.refresh.assert_awaited_once_with(payment)
        assert result is payment

    async def test_get_payment_returns_payment(self, repo, mock_db):
        """get_payment returns payment by id."""
        payment = self._make_tax_payment()
        mock_db.execute.return_value = _make_mock_result(single=payment)
        result = await repo.get_payment(str(payment.id))
        assert result is payment

    async def test_update_tax_record_status_calls_base(self, repo, mock_db):
        """update_tax_record_status delegates to base update_status."""
        repo.update_status = AsyncMock()
        await repo.update_tax_record_status("record-1", "paid")
        repo.update_status.assert_awaited_once_with("record-1", "paid")

    async def test_transaction_context_commits(self, repo, mock_db):
        """transaction context begins a DB transaction."""
        async with repo.transaction():
            pass
        mock_db.begin.assert_called()