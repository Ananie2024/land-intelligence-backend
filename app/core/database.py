# app/core/database.py
"""
Database Configuration
Land Intelligence System
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
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


engine = create_async_engine(
    get_async_database_url(),
    # Honour the DATABASE_ECHO setting from .env so developers can
    # toggle SQL statement logging without touching source code.
    echo=settings.DATABASE_ECHO,
    future=True,
    # Connection pool tuning — values mirror the .env.example defaults.
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