# tests/unit/test_tax_service.py
"""
Unit tests for TaxService.
"""
import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.models.parcel import Parcel
from app.models.tax_record import TaxRecord
from app.models.enums import TaxRecordStatus
from app.services.tax.tax_service import TaxService


class TestTaxService:
    """Test suite for TaxService."""

    @pytest.fixture
    def mock_db(self):
        db = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.begin = AsyncMock()
        return db

    @pytest.fixture
    def service(self, mock_db):
        return TaxService(mock_db)

    @pytest.fixture
    def mock_parcel(self):
        parcel = MagicMock(spec=Parcel)
        parcel.id = str(uuid4())
        parcel.upi = "UPI-001"
        parcel.area_sqm = 1000.0
        parcel.valuation = 500000.0
        parcel.land_use_category_id = None
        parcel.land_use_category = None
        return parcel

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

    async def test_calculate_tax_parcel_not_found_raises(self, service):
        """Raises ValueError when parcel not found."""
        service.parcel_repo.get_by_upi = AsyncMock(return_value=None)
        with pytest.raises(ValueError):
            await service.calculate_tax(parcel_upi="missing", assessment_year=2024)

    async def test_calculate_tax_success(self, service, mock_parcel):
        """Returns calculated tax details."""
        service.parcel_repo.get_by_upi = AsyncMock(return_value=mock_parcel)
        service.tax_calculator.calculate_tax = AsyncMock(return_value={
            "assessed_value": Decimal("500000.00"),
            "tax_rate_applied": Decimal("0.05"),
            "base_tax_amount": Decimal("50.00"),
            "penalties_amount": Decimal("0.00"),
            "total_amount": Decimal("50.00"),
            "gross_tax": Decimal("50.00"),
            "exemptions_applied": Decimal("0.00"),
            "net_tax_due": Decimal("50.00"),
        })
        service.penalty_engine.calculate_penalty_on_balance = AsyncMock(return_value={
            "base_penalty": Decimal("0.00"),
            "interest_accrued": Decimal("0.00"),
            "total_due": Decimal("0.00"),
        })
        result = await service.calculate_tax(mock_parcel.upi, 2024, include_penalties=False)
        assert result["assessment_year"] == 2024
        assert result["total_amount"] == 50.0

    async def test_generate_assessment_parcel_not_found_raises(self, service):
        """Raises ValueError when parcel not found."""
        service.parcel_repo.get_by_upi = AsyncMock(return_value=None)
        with pytest.raises(ValueError):
            await service.generate_assessment(parcel_upi="missing", assessment_year=2024, user_id="u-1")

    async def test_generate_assessment_duplicate_raises(self, service, mock_parcel):
        """Raises ValueError when assessment already exists."""
        service.parcel_repo.get_by_upi = AsyncMock(return_value=mock_parcel)
        service.repo.get_by_parcel_and_year = AsyncMock(return_value=MagicMock(spec=TaxRecord))
        with pytest.raises(ValueError):
            await service.generate_assessment(parcel_upi=mock_parcel.upi, assessment_year=2024, user_id="u-1")

    async def test_generate_assessment_success(self, service, mock_parcel):
        """Creates a new assessment record."""
        service.parcel_repo.get_by_upi = AsyncMock(return_value=mock_parcel)
        service.repo.get_by_parcel_and_year = AsyncMock(return_value=None)
        service.assessment_generator.generate_assessment = AsyncMock(return_value=MagicMock(spec=TaxRecord))
        result = await service.generate_assessment(parcel_upi=mock_parcel.upi, assessment_year=2024, user_id="u-1")
        assert result is not None

    async def test_generate_parish_assessments_parish_not_found_raises(self, service):
        """Raises ValueError when parish not found."""
        service.parish_repo.get = AsyncMock(return_value=None)
        with pytest.raises(ValueError):
            await service.generate_parish_assessments(parish_id="missing", assessment_year=2024, user_id="u-1")

    async def test_record_tax_payment_tax_record_not_found_raises(self, service):
        """Raises ValueError when tax record not found."""
        service.repo.get = AsyncMock(return_value=None)
        with pytest.raises(ValueError):
            await service.record_tax_payment(
                tax_record_id="missing",
                payment_amount=50.0,
                payment_method="cash",
                payment_reference="REF-1",
                payment_date=date(2024, 1, 1),
                user_id="u-1",
            )

    async def test_record_tax_payment_success(self, service, mock_tax_record):
        """Records a payment successfully."""
        service.repo.get = AsyncMock(return_value=mock_tax_record)
        service.payment_processor.record_payment = AsyncMock(return_value={
            "success": True,
            "payment_id": str(uuid4()),
            "amount_applied": Decimal("100.00"),
            "principal_portion": Decimal("100.00"),
            "penalty_portion": Decimal("0.00"),
            "remaining_principal": Decimal("0.00"),
            "remaining_penalty": Decimal("0.00"),
            "total_remaining": Decimal("0.00"),
            "is_fully_paid": True,
        })
        result = await service.record_tax_payment(
            tax_record_id=str(mock_tax_record.id),
            payment_amount=100.0,
            payment_method="cash",
            payment_reference="REF-1",
            payment_date=date(2024, 1, 1),
            user_id="u-1",
        )
        assert result["success"] is True
        service.db.commit.assert_awaited()

    async def test_get_outstanding_tax_parcel_not_found_raises(self, service):
        """Raises ValueError when parcel not found."""
        service.parcel_repo.get_by_upi = AsyncMock(return_value=None)
        with pytest.raises(ValueError):
            await service.get_outstanding_tax(parcel_upi="missing", user_id="u-1")

    async def test_get_payment_history_parcel_not_found_raises(self, service):
        """Raises ValueError when parcel not found."""
        service.parcel_repo.get_by_upi = AsyncMock(return_value=None)
        with pytest.raises(ValueError):
            await service.get_payment_history(parcel_upi="missing", user_id="u-1")

    async def test_get_tax_record_returns_record(self, service):
        """Fetch tax record by id."""
        record = MagicMock(spec=TaxRecord)
        service.repo.get = AsyncMock(return_value=record)
        result = await service.get_tax_record(str(record.id))
        assert result is record