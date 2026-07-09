# tests/conftest.py
"""Shared pytest fixtures for all tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import UserRole


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def client():
    """Create a TestClient for the FastAPI application."""
    return TestClient(app)


def _make_auth_headers(role: str = "viewer") -> dict:
    """Helper to create auth headers with specified role."""
    role_map = {
        "admin": UserRole.ADMIN,
        "client": UserRole.CLIENT,
        "viewer": UserRole.VIEWER,
    }
    user_role = role_map.get(role, UserRole.VIEWER)
    token_payload = {
        "sub": f"{role}-user-uuid",
        "username": role,
        "role": user_role.value,
        "jti": f"test-jti-{role}",
        "exp": 9999999999,
    }
    return token_payload


@pytest.fixture
def admin_auth_headers():
    """Create headers for admin user authentication."""
    token_payload = _make_auth_headers("admin")
    with patch("app.core.security.verify_token") as mock_verify:
        mock_verify.return_value = token_payload
        with patch("app.core.token_blacklist.is_token_blacklisted") as mock_blacklist:
            mock_blacklist.return_value = False
            yield {"Authorization": "Bearer test-admin-token"}


@pytest.fixture
def client_auth_headers():
    """Create headers for client user authentication."""
    token_payload = _make_auth_headers("client")
    with patch("app.core.security.verify_token") as mock_verify:
        mock_verify.return_value = token_payload
        with patch("app.core.token_blacklist.is_token_blacklisted") as mock_blacklist:
            mock_blacklist.return_value = False
            yield {"Authorization": "Bearer test-client-token"}


@pytest.fixture
def viewer_auth_headers():
    """Create headers for viewer user authentication."""
    token_payload = _make_auth_headers("viewer")
    with patch("app.core.security.verify_token") as mock_verify:
        mock_verify.return_value = token_payload
        with patch("app.core.token_blacklist.is_token_blacklisted") as mock_blacklist:
            mock_blacklist.return_value = False
            yield {"Authorization": "Bearer test-viewer-token"}
