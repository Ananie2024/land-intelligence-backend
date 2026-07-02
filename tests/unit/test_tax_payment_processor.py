# tests/unit/test_tax_payment_processor.py
"""
Unit tests for PaymentProcessor.
"""
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.models.tax_record import TaxRecord
from app.models.tax_payment import TaxPayment
from app.models.enums import TaxRecordStatus
from app.repositories.tax_repository import TaxRepository
from app.services.tax.penalty_engine import PenaltyEngine
from app.services.tax.payment_processor import PaymentProcessor


class _FakeTaxPayment:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestPaymentProcessor:
    """Test suite for PaymentProcessor."""

    @pytest.fixture
    def mock_repo(self):
        return AsyncMock(spec=TaxRepository)

    @pytest.fixture
    def mock_penalty_engine(self):
        return AsyncMock(spec=PenaltyEngine)

    @pytest.fixture
    def processor(self, mock_repo, mock_penalty_engine):
        return PaymentProcessor(mock_repo, mock_penalty_engine)

    @pytest.fixture
    def mock_tax_record(self):
        record = MagicMock(spec=TaxRecord)
        record.id = str(uuid4())
        record.parcel_id = str(uuid4())
        record.assessment_year = 2024
        record.total_amount = 100.0
        record.status = TaxRecordStatus.PENDING
        record.due_date = date(2025, 3, 31)
        return record

    async def test_record_payment_zero_amount_rejected(self, processor):
        result = await processor.record_payment(
            parcel_id=uuid4(),
            assessment_year=2024,
            amount_paid=Decimal("0.00"),
            payment_method="cash",
            reference_number="REF-1",
            payment_date=date(2024, 1, 1),
            received_by="teller",
        )
        assert result["success"] is False
        assert "Payment amount must be greater than zero" in result["error"]

    async def test_record_payment_no_tax_record_returns_failure(self, processor):
        processor.tax_repository.get_by_parcel_and_year_for_update.return_value = None
        result = await processor.record_payment(
            parcel_id=uuid4(),
            assessment_year=2024,
            amount_paid=Decimal("50.00"),
            payment_method="cash",
            reference_number="REF-1",
            payment_date=date(2024, 1, 1),
            received_by="teller",
        )
        assert result["success"] is False

    @patch("app.services.tax.payment_processor.TaxPayment", MagicMock())
    async def test_record_payment_full_payment_updates_status(self, processor, mock_tax_record):
        processor.tax_repository.get_by_parcel_and_year_for_update.return_value = mock_tax_record
        processor.tax_repository.get_total_paid_for_assessment.return_value = 0.0
        fake_payment = MagicMock(spec=TaxPayment)
        fake_payment.id = uuid4()
        processor.tax_repository.create_payment.return_value = fake_payment
        processor.penalty_engine.calculate_penalty_on_balance.return_value = {
            "base_penalty": Decimal("0.00"),
            "interest_accrued": Decimal("0.00"),
            "total_due": Decimal("0.00"),
        }
        result = await processor.record_payment(
            parcel_id=mock_tax_record.parcel_id,
            assessment_year=mock_tax_record.assessment_year,
            amount_paid=Decimal("100.00"),
            payment_method="cash",
            reference_number="REF-1",
            payment_date=date(2024, 1, 1),
            received_by="teller",
        )
        assert result["success"] is True
        processor.tax_repository.update_tax_record_status.assert_called_with(mock_tax_record.id, "paid")

    @patch("app.services.tax.payment_processor.TaxPayment", MagicMock())
    async def test_record_payment_partial_sets_partial_status(self, processor, mock_tax_record):
        processor.tax_repository.get_by_parcel_and_year_for_update.return_value = mock_tax_record
        processor.tax_repository.get_total_paid_for_assessment.return_value = 0.0
        fake_payment = MagicMock(spec=TaxPayment)
        fake_payment.id = uuid4()
        processor.tax_repository.create_payment.return_value = fake_payment
        processor.penalty_engine.calculate_penalty_on_balance.return_value = {
            "base_penalty": Decimal("0.00"),
            "interest_accrued": Decimal("0.00"),
            "total_due": Decimal("0.00"),
        }
        await processor.record_payment(
            parcel_id=mock_tax_record.parcel_id,
            assessment_year=mock_tax_record.assessment_year,
            amount_paid=Decimal("50.00"),
            payment_method="cash",
            reference_number="REF-1",
            payment_date=date(2026, 1, 1),
            received_by="teller",
        )
        processor.tax_repository.update_tax_record_status.assert_called_with(mock_tax_record.id, "partial")

    async def test_record_payment_overpayment_rejected(self, processor, mock_tax_record):
        processor.tax_repository.get_by_parcel_and_year_for_update.return_value = mock_tax_record
        processor.tax_repository.get_total_paid_for_assessment.return_value = 0.0
        processor.penalty_engine.calculate_penalty_on_balance.return_value = {
            "base_penalty": Decimal("0.00"),
            "interest_accrued": Decimal("0.00"),
            "total_due": Decimal("100.00"),
        }
        result = await processor.record_payment(
            parcel_id=mock_tax_record.parcel_id,
            assessment_year=mock_tax_record.assessment_year,
            amount_paid=Decimal("150.00"),
            payment_method="cash",
            reference_number="REF-1",
            payment_date=date(2024, 1, 1),
            received_by="teller",
        )
        assert result["success"] is False
        assert "exceeds total outstanding" in result["error"]

    async def test_issue_receipt_returns_none_when_missing(self, processor):
        processor.tax_repository.get_payment.return_value = None
        result = await processor.issue_receipt(uuid4())
        assert result is None

    async def test_issue_receipt_returns_receipt_data(self, processor, mock_tax_record):
        payment = MagicMock(spec=TaxPayment)
        payment.id = uuid4()
        payment.tax_record_id = mock_tax_record.id
        payment.payment_amount = 100.0
        payment.payment_date = date(2024, 1, 1)
        payment.payment_method = "cash"
        payment.payment_reference = "REF-1"
        payment.receipt_number = "RCP-20240101-ABCD"
        payment.is_reversal = False
        processor.tax_repository.get_payment.return_value = payment
        processor.tax_repository.get.return_value = mock_tax_record
        parcel = MagicMock()
        parcel.id = mock_tax_record.parcel_id
        parcel.parcel_number = "P-001"
        processor.tax_repository.get_parcel.return_value = parcel
        result = await processor.issue_receipt(payment.id)
        assert result["receipt_id"] == str(payment.id)
        assert result["receipt_number"] == payment.receipt_number

    async def test_get_payment_history_returns_history(self, processor):
        payments = [MagicMock(spec=TaxPayment), MagicMock(spec=TaxPayment)]
        processor.tax_repository.get_payments_by_parcel.return_value = payments
        result = await processor.get_payment_history(uuid4())
        assert len(result) == 2

    def test_get_due_date_for_year(self, processor):
        assert processor._get_due_date_for_year(2024) == date(2025, 3, 31)

    @patch("app.services.tax.payment_processor.TaxPayment", _FakeTaxPayment)
    async def test_apply_to_penalties_first_prioritizes_penalties(self, processor, mock_tax_record):
        processor.tax_repository.get_by_parcel_and_year_for_update.return_value = mock_tax_record
        processor.tax_repository.get_total_paid_for_assessment.return_value = 0.0
        processor.tax_repository.create_payment.return_value = _FakeTaxPayment(id=uuid4())
        processor.penalty_engine.calculate_penalty_on_balance.return_value = {
            "base_penalty": Decimal("10.00"),
            "interest_accrued": Decimal("5.00"),
            "total_due": Decimal("115.00"),
        }
        await processor.record_payment(
            parcel_id=mock_tax_record.parcel_id,
            assessment_year=mock_tax_record.assessment_year,
            amount_paid=Decimal("50.00"),
            payment_method="cash",
            reference_number="REF-1",
            payment_date=date(2024, 1, 1),
            received_by="teller",
            apply_to_penalties_first=True,
        )
        created_payment = processor.tax_repository.create_payment.call_args[0][0]
        assert "Principal:" in created_payment.notes
        assert "Penalty:" in created_payment.notes
