# tests/integration/test_parcel_service.py
"""
Integration tests for ParcelService — exercises the full service → repository
→ model layer flow with a mocked AsyncSession.
"""
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import all models upfront so SQLAlchemy mappers configure properly
# before any service code touches relationships on Parcel / AuditLog.
from app.models import import_all_models
import_all_models()

from app.models.parish import Parish
from app.models.parcel_ownership_history import ParcelOwnershipHistory
from app.services.parcel.parcel_service import ParcelService
from app.schemas.parcel_schema import ParcelCreate, ParcelUpdate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_parcel(**overrides) -> MagicMock:
    """Build a minimal Parcel-like object for testing.
    
    NOTE: extra_data (aliased as "metadata") must be explicitly set to None
    to prevent MagicMock from auto-creating a mock object that Pydantic
    will reject as not-a-dict.
    """
    # NOTE: we do NOT pass spec=Parcel here because the model has a
    # ``metadata`` column (aliased to ``extra_data`` in Python) which
    # MagicMock auto-creates as a MagicMock object, causing Pydantic
    # to reject it with "Input should be a valid dictionary".
    p = MagicMock()
    p.id = overrides.get("id", "parcel-uuid-001")
    p.parcel_number = overrides.get("parcel_number", "PLC-001")
    p.parish_id = overrides.get("parish_id", "parish-uuid-001")
    p.land_use_category_id = overrides.get("land_use_category_id", None)
    p.area_sqm = overrides.get("area_sqm", 500.0)
    p.title_deed_number = overrides.get("title_deed_number", None)
    p.owner_name = overrides.get("owner_name", "John Doe")
    p.owner_contact = overrides.get("owner_contact", None)
    p.location_description = overrides.get("location_description", None)
    p.valuation = overrides.get("valuation", None)
    p.valuation_date = overrides.get("valuation_date", None)
    p.is_active = overrides.get("is_active", True)
    p.metadata = overrides.get("extra_data", None)
    # ParcelResponse schema reads these optional display-name fields.
    p.parish_name = overrides.get("parish_name", None)
    p.land_use_category_name = overrides.get("land_use_category_name", None)
    return p


def _make_parish(**overrides) -> MagicMock:
    """Build a minimal Parish-like object for testing."""
    p = MagicMock(spec=Parish)
    p.id = overrides.get("id", "parish-uuid-001")
    p.name = overrides.get("name", "St. Michael's")
    p.code = overrides.get("code", "PAR-001")
    p.parcel_count = overrides.get("parcel_count", 0)
    p.is_active = overrides.get("is_active", True)
    return p


def _make_ownership_entry(**overrides) -> MagicMock:
    """Build a minimal ParcelOwnershipHistory-like object for testing."""
    e = MagicMock(spec=ParcelOwnershipHistory)
    e.id = overrides.get("id", "history-uuid-001")
    e.parcel_id = overrides.get("parcel_id", "parcel-uuid-001")
    e.owner_name = overrides.get("owner_name", "John Doe")
    e.owner_contact = overrides.get("owner_contact", None)
    e.transfer_date = overrides.get("transfer_date", date.today())
    e.document_reference = overrides.get("document_reference", None)
    e.notes = overrides.get("notes", None)
    return e


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db():
    """Create a mock AsyncSession."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def service(mock_db):
    """Create a ParcelService with a mocked session."""
    return ParcelService(mock_db)


# ---------------------------------------------------------------------------
# Tests — list_parcels
# ---------------------------------------------------------------------------

class TestListParcels:
    """Integration tests for ParcelService.list_parcels()."""

    async def test_list_without_filters(self, service):
        """Returns paginated results when no filters are supplied."""
        parcels = [_make_parcel(id=f"p-{i}") for i in range(3)]
        service.parcel_repo.count = AsyncMock(return_value=3)
        service.parcel_repo.list = AsyncMock(return_value=parcels)

        result = await service.list_parcels(page=1, size=10)

        assert result.total == 3
        assert len(result.items) == 3
        assert result.page == 1
        assert result.size == 10
        assert result.pages == 1
        service.parcel_repo.count.assert_awaited_once()
        service.parcel_repo.list.assert_awaited_once_with(
            skip=0, limit=10, order_by="created_at", descending=True
        )

    async def test_list_with_filters(self, service):
        """Filters results when filter parameters are supplied."""
        parcels = [_make_parcel(id="p-1", owner_name="Jane")]
        service.parcel_repo.search = AsyncMock(return_value=parcels)
        service.parcel_repo.count = AsyncMock(return_value=1)

        result = await service.list_parcels(
            page=1, size=20,
            filters={"owner_name": "Jane", "parish_id": "parish-1"}
        )

        assert result.total == 1
        assert len(result.items) == 1
        service.parcel_repo.search.assert_awaited_once_with(
            owner_name="Jane",
            parcel_number=None,
            parish_id="parish-1",
            land_use_category_id=None,
            min_area_sqm=None,
            max_area_sqm=None,
            skip=0,
            limit=20,
        )

    async def test_list_empty(self, service):
        """Returns empty items list when no parcels exist."""
        service.parcel_repo.count = AsyncMock(return_value=0)
        service.parcel_repo.list = AsyncMock(return_value=[])

        result = await service.list_parcels(page=1, size=20)

        assert result.total == 0
        assert result.items == []


# ---------------------------------------------------------------------------
# Tests — create_parcel
# ---------------------------------------------------------------------------

class TestCreateParcel:
    """Integration tests for ParcelService.create_parcel()."""

    async def test_create_success(self, service, mock_db):
        """Creates a parcel successfully with ownership history and commits."""
        payload = ParcelCreate(
            parcel_number="PLC-099",
            parish_id="parish-uuid-001",
            area_sqm=1000.0,
            owner_name="Jane Smith",
            title_deed_number="TD-099",
        )
        parish = _make_parish(id="parish-uuid-001")
        created = _make_parcel(
            id="new-parcel-uuid",
            parcel_number="PLC-099",
            parish_id="parish-uuid-001",
            owner_name="Jane Smith",
        )

        service.parish_repo.get = AsyncMock(return_value=parish)
        service.parcel_repo.get_by_parcel_number = AsyncMock(return_value=None)
        service.parcel_repo.get_by_title_deed = AsyncMock(return_value=None)
        service.parcel_repo.create = AsyncMock(return_value=created)
        service.ownership_repo.add_entry = AsyncMock(return_value=_make_ownership_entry())
        service.parish_repo.update_parcel_count = AsyncMock(return_value=parish)

        result = await service.create_parcel(payload, user_id="user-1")

        assert result is created
        service.parish_repo.get.assert_awaited_once_with("parish-uuid-001")
        service.parcel_repo.get_by_parcel_number.assert_awaited_once_with("PLC-099")
        service.parcel_repo.get_by_title_deed.assert_awaited_once_with("TD-099")
        service.parcel_repo.create.assert_awaited_once_with(payload)
        service.ownership_repo.add_entry.assert_awaited_once()
        service.parish_repo.update_parcel_count.assert_awaited_once_with("parish-uuid-001")
        mock_db.commit.assert_awaited_once()
        mock_db.refresh.assert_awaited_once_with(created)

    async def test_create_parish_not_found_raises(self, service, mock_db):
        """Raises ValueError when the referenced parish does not exist."""
        service.parish_repo.get = AsyncMock(return_value=None)

        payload = ParcelCreate(
            parcel_number="PLC-099",
            parish_id="nonexistent-parish",
            area_sqm=500.0,
            owner_name="Test",
        )

        with pytest.raises(ValueError, match="Parish 'nonexistent-parish' not found"):
            await service.create_parcel(payload, user_id="user-1")

        mock_db.commit.assert_not_called()

    async def test_create_duplicate_parcel_number_raises(self, service, mock_db):
        """Raises ValueError when the parcel number already exists."""
        parish = _make_parish(id="parish-uuid-001")
        existing = _make_parcel(parcel_number="PLC-099")

        service.parish_repo.get = AsyncMock(return_value=parish)
        service.parcel_repo.get_by_parcel_number = AsyncMock(return_value=existing)

        payload = ParcelCreate(
            parcel_number="PLC-099",
            parish_id="parish-uuid-001",
            area_sqm=500.0,
            owner_name="Test",
        )

        with pytest.raises(ValueError, match="Parcel number 'PLC-099' already exists"):
            await service.create_parcel(payload, user_id="user-1")

        mock_db.commit.assert_not_called()

    async def test_create_duplicate_title_deed_raises(self, service, mock_db):
        """Raises ValueError when the title deed number is already registered."""
        parish = _make_parish(id="parish-uuid-001")
        conflict = _make_parcel(title_deed_number="TD-099")

        service.parish_repo.get = AsyncMock(return_value=parish)
        service.parcel_repo.get_by_parcel_number = AsyncMock(return_value=None)
        service.parcel_repo.get_by_title_deed = AsyncMock(return_value=conflict)

        payload = ParcelCreate(
            parcel_number="PLC-100",
            parish_id="parish-uuid-001",
            area_sqm=500.0,
            owner_name="Test",
            title_deed_number="TD-099",
        )

        with pytest.raises(ValueError, match="Title deed 'TD-099' is already registered"):
            await service.create_parcel(payload, user_id="user-1")

        mock_db.commit.assert_not_called()


# ---------------------------------------------------------------------------
# Tests — get_parcel
# ---------------------------------------------------------------------------

class TestGetParcel:
    """Integration tests for ParcelService.get_parcel()."""

    async def test_get_parcel_found(self, service):
        """Returns the parcel when it exists."""
        parcel = _make_parcel(id="parcel-1")
        service.parcel_repo.get = AsyncMock(return_value=parcel)

        result = await service.get_parcel("parcel-1")

        assert result is parcel
        service.parcel_repo.get.assert_awaited_once_with("parcel-1")

    async def test_get_parcel_not_found(self, service):
        """Returns None when the parcel does not exist."""
        service.parcel_repo.get = AsyncMock(return_value=None)

        result = await service.get_parcel("nonexistent")

        assert result is None


# ---------------------------------------------------------------------------
# Tests — get_parcel_by_number / get_parcel_by_deed
# ---------------------------------------------------------------------------

class TestGetParcelByLookup:
    """Integration tests for lookup methods."""

    async def test_get_by_number_found(self, service):
        parcel = _make_parcel(parcel_number="PLC-001")
        service.parcel_repo.get_by_parcel_number = AsyncMock(return_value=parcel)

        result = await service.get_parcel_by_number("PLC-001")

        assert result is parcel
        service.parcel_repo.get_by_parcel_number.assert_awaited_once_with("PLC-001")

    async def test_get_by_number_not_found(self, service):
        service.parcel_repo.get_by_parcel_number = AsyncMock(return_value=None)

        result = await service.get_parcel_by_number("NONEXISTENT")

        assert result is None

    async def test_get_by_deed_found(self, service):
        parcel = _make_parcel(title_deed_number="TD-001")
        service.parcel_repo.get_by_title_deed = AsyncMock(return_value=parcel)

        result = await service.get_parcel_by_deed("TD-001")

        assert result is parcel
        service.parcel_repo.get_by_title_deed.assert_awaited_once_with("TD-001")

    async def test_get_by_deed_not_found(self, service):
        service.parcel_repo.get_by_title_deed = AsyncMock(return_value=None)

        result = await service.get_parcel_by_deed("NONEXISTENT")

        assert result is None


# ---------------------------------------------------------------------------
# Tests — list_parcels_by_parish
# ---------------------------------------------------------------------------

class TestListParcelsByParish:
    """Integration tests for ParcelService.list_parcels_by_parish()."""

    async def test_list_by_parish_success(self, service):
        """Returns paginated parcels for a valid parish."""
        parish = _make_parish(id="parish-1")
        parcels = [_make_parcel(id=f"p-{i}", parish_id="parish-1") for i in range(2)]

        service.parish_repo.get = AsyncMock(return_value=parish)
        service.parcel_repo.get_by_parish = AsyncMock(return_value=parcels)
        service.parcel_repo.count_by_parish = AsyncMock(return_value=2)

        result = await service.list_parcels_by_parish("parish-1", page=1, size=20)

        assert result.total == 2
        assert len(result.items) == 2
        service.parish_repo.get.assert_awaited_once_with("parish-1")
        service.parcel_repo.get_by_parish.assert_awaited_once_with(
            "parish-1", skip=0, limit=20
        )
        service.parcel_repo.count_by_parish.assert_awaited_once_with("parish-1")

    async def test_list_by_parish_not_found_raises(self, service):
        """Raises ValueError when the parish does not exist."""
        service.parish_repo.get = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Parish 'nonexistent' not found"):
            await service.list_parcels_by_parish("nonexistent")


# ---------------------------------------------------------------------------
# Tests — update_parcel
# ---------------------------------------------------------------------------

class TestUpdateParcel:
    """Integration tests for ParcelService.update_parcel()."""

    async def test_update_success(self, service, mock_db):
        """Updates a parcel successfully and commits."""
        existing = _make_parcel(
            id="parcel-1",
            parcel_number="PLC-001",
            owner_name="John Doe",
            owner_contact="john@example.com",
        )
        updated = _make_parcel(
            id="parcel-1",
            parcel_number="PLC-001",
            owner_name="John Doe Updated",
            owner_contact="john@example.com",
        )

        payload = ParcelUpdate(owner_name="John Doe Updated")
        service.parcel_repo.get = AsyncMock(return_value=existing)
        service.parcel_repo.update = AsyncMock(return_value=updated)
        service.ownership_repo.add_entry = AsyncMock(return_value=_make_ownership_entry())

        result = await service.update_parcel("parcel-1", payload, user_id="user-1")

        assert result.owner_name == "John Doe Updated"
        service.ownership_repo.add_entry.assert_awaited_once()  # owner changed
        mock_db.commit.assert_awaited_once()
        mock_db.refresh.assert_awaited_once_with(updated)

    async def test_update_not_found_returns_none(self, service, mock_db):
        """Returns None when the parcel does not exist."""
        service.parcel_repo.get = AsyncMock(return_value=None)

        payload = ParcelUpdate(owner_name="New Owner")
        result = await service.update_parcel("nonexistent", payload, "user-1")

        assert result is None
        mock_db.commit.assert_not_called()

    async def test_update_duplicate_parcel_number_raises(self, service, mock_db):
        """Raises ValueError when updating to a parcel number already in use."""
        existing = _make_parcel(id="parcel-1", parcel_number="PLC-001")
        conflict = _make_parcel(id="parcel-2", parcel_number="PLC-002")

        service.parcel_repo.get = AsyncMock(return_value=existing)
        service.parcel_repo.get_by_parcel_number = AsyncMock(return_value=conflict)

        payload = ParcelUpdate(parcel_number="PLC-002")

        with pytest.raises(ValueError, match="Parcel number 'PLC-002' is already in use"):
            await service.update_parcel("parcel-1", payload, "user-1")

        mock_db.commit.assert_not_called()

    async def test_update_duplicate_title_deed_raises(self, service, mock_db):
        """Raises ValueError when updating to a title deed already in use."""
        existing = _make_parcel(id="parcel-1", title_deed_number="TD-001")
        conflict = _make_parcel(id="parcel-2", title_deed_number="TD-002")

        service.parcel_repo.get = AsyncMock(return_value=existing)
        service.parcel_repo.get_by_title_deed = AsyncMock(return_value=conflict)

        payload = ParcelUpdate(title_deed_number="TD-002")

        with pytest.raises(ValueError, match="Title deed 'TD-002' is already registered"):
            await service.update_parcel("parcel-1", payload, "user-1")

        mock_db.commit.assert_not_called()

    async def test_update_owner_unchanged_no_history_entry(self, service, mock_db):
        """Does not create an ownership history entry when owner_name is unchanged."""
        existing = _make_parcel(id="parcel-1", owner_name="John Doe")
        updated = _make_parcel(id="parcel-1", owner_name="John Doe", location_description="New location")

        service.parcel_repo.get = AsyncMock(return_value=existing)
        service.parcel_repo.update = AsyncMock(return_value=updated)
        service.ownership_repo.add_entry = AsyncMock()

        payload = ParcelUpdate(location_description="New location")
        result = await service.update_parcel("parcel-1", payload, "user-1")

        assert result.location_description == "New location"
        service.ownership_repo.add_entry.assert_not_called()
        mock_db.commit.assert_awaited_once()


# ---------------------------------------------------------------------------
# Tests — delete_parcel
# ---------------------------------------------------------------------------

class TestDeleteParcel:
    """Integration tests for ParcelService.delete_parcel()."""

    async def test_delete_success(self, service, mock_db):
        """Soft-deletes a parcel, updates parish count, and commits."""
        parcel = _make_parcel(id="parcel-1", parish_id="parish-1")
        parish = _make_parish(id="parish-1")

        service.parcel_repo.get = AsyncMock(return_value=parcel)
        service.parcel_repo.soft_delete = AsyncMock(return_value=True)
        service.parish_repo.update_parcel_count = AsyncMock(return_value=parish)

        result = await service.delete_parcel("parcel-1", user_id="user-1")

        assert result is True
        service.parcel_repo.soft_delete.assert_awaited_once_with("parcel-1")
        service.parish_repo.update_parcel_count.assert_awaited_once_with("parish-1")
        mock_db.commit.assert_awaited_once()

    async def test_delete_not_found_returns_false(self, service, mock_db):
        """Returns False when the parcel does not exist."""
        service.parcel_repo.get = AsyncMock(return_value=None)

        result = await service.delete_parcel("nonexistent", "user-1")

        assert result is False
        mock_db.commit.assert_not_called()


# ---------------------------------------------------------------------------
# Tests — get_ownership_history
# ---------------------------------------------------------------------------

class TestGetOwnershipHistory:
    """Integration tests for ParcelService.get_ownership_history()."""

    async def test_returns_history_entries(self, service):
        """Returns ownership history entries for a parcel."""
        entries = [
            _make_ownership_entry(id="h-1", owner_name="First Owner"),
            _make_ownership_entry(id="h-2", owner_name="Second Owner"),
        ]
        service.ownership_repo.list_by_parcel = AsyncMock(return_value=entries)

        result = await service.get_ownership_history("parcel-1", skip=0, limit=100)

        assert len(result) == 2
        assert result[0].owner_name == "First Owner"
        service.ownership_repo.list_by_parcel.assert_awaited_once_with(
            "parcel-1", skip=0, limit=100
        )

    async def test_returns_empty_list_when_no_history(self, service):
        """Returns empty list when no ownership history exists."""
        service.ownership_repo.list_by_parcel = AsyncMock(return_value=[])

        result = await service.get_ownership_history("parcel-1")

        assert result == []