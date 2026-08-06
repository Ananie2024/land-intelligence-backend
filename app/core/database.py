# app/core/database.py
"""
Database Configuration
Land Intelligence System

Supports:
- Local PostgreSQL + PostGIS
- Supabase (direct connection or Supavisor pooler)
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator

from app.core.config import settings
from app.models.base import Base


def get_async_database_url() -> str:
    """
    Convert the standard postgresql:// DSN to the asyncpg driver URL
    that SQLAlchemy requires for async operation.
    """
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if db_url.startswith("postgres://"):
        # Some environments emit the shorter form
        return db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    return db_url


def _is_supabase_pooler(url: str) -> bool:
    """Detect Supabase transaction-mode pooler (port 6543)."""
    return ":6543/" in url or "pooler.supabase.com" in url


# ---------------------------------------------------------------------------
# Engine configuration
# ---------------------------------------------------------------------------
# When using Supabase Transaction Mode pooler (port 6543):
#   - Use NullPool so the external pooler manages connections
#   - Disable prepared statement caching (required by Supavisor)
# When using Direct connection (port 5432) or local Postgres:
#   - Use normal connection pooling
# ---------------------------------------------------------------------------

_async_url = get_async_database_url()
_use_pooler = _is_supabase_pooler(_async_url)

if _use_pooler:
    engine = create_async_engine(
        _async_url,
        echo=settings.DATABASE_ECHO,
        future=True,
        poolclass=NullPool,
        connect_args={
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        },
    )
else:
    engine = create_async_engine(
        _async_url,
        echo=settings.DATABASE_ECHO,
        future=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=3600,
    )

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
