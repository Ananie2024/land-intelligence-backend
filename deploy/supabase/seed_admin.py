# =============================================================================
# Seed Admin User for Supabase
# Land Intelligence System
#
# Inserts (or verifies) an ADMIN user directly into the configured database.
# Uses the same SQLAlchemy models + Argon2 hashing as the application, so the
# seeded credentials are valid for the login endpoint.
#
# Usage (from repo root, with env pointing at the target DB):
#   $env:DATABASE_HOST=aws-1-eu-west-1.pooler.supabase.com ; $env:DATABASE_PORT=5432
#   $env:DATABASE_NAME=postgres ; $env:DATABASE_USER=...
#   $env:DATABASE_PASSWORD=... ; $env:SECRET_KEY=...
#   .\venv\Scripts\python.exe deploy/supabase/seed_admin.py
#
# You can override email/username/password via env:
#   SEED_ADMIN_EMAIL / SEED_ADMIN_USERNAME / SEED_ADMIN_PASSWORD
# =============================================================================

import asyncio
import os
import sys

from sqlalchemy import select

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.core.security import get_password_hash  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402

SEED_ADMIN_EMAIL = os.environ.get("SEED_ADMIN_EMAIL", "admin@landintelligence.org")
SEED_ADMIN_USERNAME = os.environ.get("SEED_ADMIN_USERNAME", "admin")
SEED_ADMIN_FULL_NAME = os.environ.get("SEED_ADMIN_FULL_NAME", "System Administrator")
# Must satisfy the app policy: length >= 8, contains a digit and a letter.
SEED_ADMIN_PASSWORD = os.environ.get(
    "SEED_ADMIN_PASSWORD", "Admin@Land2026"
)


async def main() -> int:
    async with AsyncSessionLocal() as db:
        existing = (
            await db.execute(
                select(User).where(
                    (User.email == SEED_ADMIN_EMAIL)
                    | (User.username == SEED_ADMIN_USERNAME)
                )
            )
        ).scalars().first()

        if existing:
            print(
                f"Admin already exists: id={existing.id} "
                f"email={existing.email} username={existing.username} "
                f"role={existing.role.value} active={existing.is_active}"
            )
            return 0

        user = User(
            email=SEED_ADMIN_EMAIL,
            username=SEED_ADMIN_USERNAME,
            full_name=SEED_ADMIN_FULL_NAME,
            hashed_password=get_password_hash(SEED_ADMIN_PASSWORD),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            failed_login_attempts=0,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(
            f"Created admin: id={user.id} email={user.email} "
            f"username={user.username} role={user.role.value} active={user.is_active}"
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
