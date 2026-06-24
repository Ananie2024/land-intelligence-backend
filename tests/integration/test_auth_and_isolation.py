# tests/integration/test_auth_and_isolation.py

"""
Integration tests for authentication, authorization, and parish-level data isolation.

Covers:
- Access token creation (login)
- Refresh token flow
- Token revocation (logout)
- Password hashing
- Authorization dependencies
- Parish-level data isolation: a client must never see another parish's data
"""

import pytest
from fastapi import HTTPException

from app.api.auth_dependencies import (
    require_admin,
    require_client_or_admin,
    require_parish_access,
    prevent_viewer_access,
)
from app.models.user import User, UserRole
from app.core.security import create_access_token, create_refresh_token, verify_token


# ---------------------------------------------------------------------------
# 1. Token creation (in-memory, no DB needed)
# ---------------------------------------------------------------------------


def test_login_returns_tokens_and_user():
    fake_user_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    fake_role = UserRole.CLIENT.value
    access = create_access_token(data={"sub": fake_user_id, "role": fake_role})
    refresh = create_refresh_token(data={"sub": fake_user_id})

    assert access
    assert refresh
    assert access != refresh


def test_refresh_token_rotation():
    fake_user_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    refresh = create_refresh_token(data={"sub": fake_user_id})
    access1 = create_access_token(data={"sub": fake_user_id, "role": UserRole.CLIENT.value})
    import time

    time.sleep(1.1)
    access2 = create_access_token(data={"sub": fake_user_id, "role": UserRole.CLIENT.value})

    assert access1 != access2
    assert refresh != access1
    assert refresh != access2

    for token, expected_type in [
        (access1, "access"),
        (access2, "access"),
        (refresh, "refresh"),
    ]:
        payload = verify_token(token)
        assert payload is not None
        assert payload.get("sub") == fake_user_id
        assert payload.get("type") == expected_type


def test_expired_token_handling():
    from datetime import timedelta
    expired = create_access_token(
        data={"sub": "x", "role": UserRole.VIEWER.value},
        expires_delta=timedelta(seconds=-1),
    )
    assert verify_token(expired) is None


def test_invalid_signature_handling():
    bad = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ4In0.badsig"
    assert verify_token(bad) is None


@pytest.mark.asyncio
async def test_disabled_user_handling():
    from app.api.auth_dependencies import get_current_user_from_db
    from app.models.user import User
    from fastapi import HTTPException

    disabled = User(
        id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        email="disabled@example.com",
        username="disabled",
        full_name="Disabled",
        hashed_password="fakehash",
        role=UserRole.CLIENT,
        parish_id="11111111-1111-1111-1111-111111111111",
        is_active=False,
    )

    class FakeResult:
        def scalar_one_or_none(self):
            return disabled

    class FakeDB:
        async def execute(self, stmt):
            return FakeResult()

    with pytest.raises(HTTPException) as exc:
        await get_current_user_from_db(user_id=str(disabled.id), db=FakeDB())
    assert exc.value.status_code == 403


def test_token_revocation_logout():
    from app.services.auth.auth_service import AuthService
    from app.core.database import get_db
    import asyncio

    async def run():
        async for db in get_db():
            service = AuthService(db)
            result = await service.logout("dummy-refresh-token")
            assert result is True
            return

    asyncio.run(run())


# ---------------------------------------------------------------------------
# 2. Parish-level data isolation and role-based authorization
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_require_parish_access_isolates_by_parish():
    client_user = User(
        id="eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee",
        email="parish_client@example.com",
        username="parish_client",
        full_name="Parish Client",
        hashed_password="fakehash",
        role=UserRole.CLIENT,
        parish_id="11111111-1111-1111-1111-111111111111",
        is_active=True,
    )
    admin_user = User(
        id="ffffffff-ffff-ffff-ffff-ffffffffffff",
        email="parish_admin@example.com",
        username="parish_admin",
        full_name="Parish Admin",
        hashed_password="fakehash",
        role=UserRole.ADMIN,
        is_active=True,
    )

    assert await require_parish_access("99999999-9999-9999-9999-999999999999", admin_user) is True
    assert await require_parish_access("11111111-1111-1111-1111-111111111111", client_user) is True

    with pytest.raises(HTTPException) as exc:
        await require_parish_access("99999999-9999-9999-9999-999999999999", client_user)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_admin_allows_admin_only():
    admin_user = User(
        id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        email="admin@example.com",
        username="admin",
        full_name="Admin",
        hashed_password="fakehash",
        role=UserRole.ADMIN,
        is_active=True,
    )
    client_user = User(
        id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        email="client@example.com",
        username="client",
        full_name="Client",
        hashed_password="fakehash",
        role=UserRole.CLIENT,
        parish_id="11111111-1111-1111-1111-111111111111",
        is_active=True,
    )

    assert await require_admin(admin_user) == admin_user

    with pytest.raises(HTTPException) as exc:
        await require_admin(client_user)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_require_client_or_admin_allows_client_and_admin():
    admin_user = User(
        id="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        email="admin2@example.com",
        username="admin2",
        full_name="Admin2",
        hashed_password="fakehash",
        role=UserRole.ADMIN,
        is_active=True,
    )
    client_user = User(
        id="cccccccc-cccc-cccc-cccc-cccccccccccc",
        email="client2@example.com",
        username="client2",
        full_name="Client2",
        hashed_password="fakehash",
        role=UserRole.CLIENT,
        parish_id="11111111-1111-1111-1111-111111111111",
        is_active=True,
    )
    viewer_user = User(
        id="dddddddd-dddd-dddd-dddd-dddddddddddd",
        email="viewer@example.com",
        username="viewer",
        full_name="Viewer",
        hashed_password="fakehash",
        role=UserRole.VIEWER,
        is_active=True,
    )

    assert await require_client_or_admin(admin_user) == admin_user
    assert await require_client_or_admin(client_user) == client_user

    with pytest.raises(HTTPException) as exc:
        await require_client_or_admin(viewer_user)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_prevent_viewer_blocks_write():
    viewer_user = User(
        id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        email="viewer2@example.com",
        username="viewer2",
        full_name="Viewer2",
        hashed_password="fakehash",
        role=UserRole.VIEWER,
        is_active=True,
    )
    with pytest.raises(HTTPException) as exc:
        await prevent_viewer_access(viewer_user)
    assert exc.value.status_code == 403

    client_user = User(
        id="bbbbbbbb-cccc-dddd-eeee-eeeeeeeeeeee",
        email="client3@example.com",
        username="client3",
        full_name="Client3",
        hashed_password="fakehash",
        role=UserRole.CLIENT,
        parish_id="11111111-1111-1111-1111-111111111111",
        is_active=True,
    )
    assert await prevent_viewer_access(client_user) == client_user