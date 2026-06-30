# tests/unit/test_repositories.py
"""
Unit tests for repository layer.
"""
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository


@pytest.fixture
def mock_db():
    """Create a mock AsyncSession."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def repo(mock_db):
    """Create a UserRepository with a mock session."""
    return UserRepository(mock_db)


def _make_user(
    failed_login_attempts: int = 0,
    locked_until=None,
    last_login=None,
    is_active: bool = True,
):
    """Helper to build a minimal User-like object for testing."""
    user = MagicMock(spec=User)
    user.id = "test-user-uuid"
    user.email = "test@example.com"
    user.username = "testuser"
    user.failed_login_attempts = failed_login_attempts
    user.locked_until = locked_until
    user.last_login = last_login
    user.is_active = is_active
    user.role = UserRole.VIEWER
    return user


class TestResetFailedLogin:
    """Regression tests for UserRepository.reset_failed_login()."""

    async def test_resets_fields_and_calls_commit(self, repo, mock_db):
        """
        Verify that reset_failed_login:
        - resets failed_login_attempts to 0
        - clears locked_until
        - sets last_login
        - calls flush(), refresh(), and commit() on the session
        """
        # Arrange — user with prior failed attempts and a lock
        locked_until = datetime.now(timezone.utc) + timedelta(hours=1)
        user = _make_user(
            failed_login_attempts=3,
            locked_until=locked_until,
            last_login=None,
        )

        # repo.get() returns the user
        repo.get = AsyncMock(return_value=user)

        # Act
        result = await repo.reset_failed_login("test-user-uuid")

        # Assert — fields were mutated on the returned object
        assert result is user
        assert result.failed_login_attempts == 0
        assert result.locked_until is None
        assert result.last_login is not None
        assert isinstance(result.last_login, datetime)

        # Assert — session lifecycle methods were called in order
        mock_db.flush.assert_awaited_once()
        mock_db.refresh.assert_awaited_once_with(user)
        mock_db.commit.assert_awaited_once()

    async def test_returns_none_when_user_not_found(self, repo, mock_db):
        """
        Verify that reset_failed_login returns None and does NOT call
        commit when the user does not exist.
        """
        # Arrange
        repo.get = AsyncMock(return_value=None)

        # Act
        result = await repo.reset_failed_login("nonexistent-id")

        # Assert
        assert result is None
        mock_db.flush.assert_not_called()
        mock_db.refresh.assert_not_called()
        mock_db.commit.assert_not_called()

    async def test_commit_is_not_called_by_sibling_methods(self, repo, mock_db):
        """
        Regression: sibling methods (increment_failed_login, lock_user)
        must NOT call commit(), only flush(). This ensures the risk is
        isolated to reset_failed_login.
        """
        user = _make_user(failed_login_attempts=2)
        repo.get = AsyncMock(return_value=user)

        # increment_failed_login
        await repo.increment_failed_login("test-user-uuid")
        mock_db.commit.assert_not_called()
        mock_db.flush.assert_called()
        mock_db.reset_mock()

        # lock_user
        await repo.lock_user("test-user-uuid", lock_minutes=30)
        mock_db.commit.assert_not_called()
        mock_db.flush.assert_called()