# app/core/database.py
"""
Database Configuration
Land Intelligence System
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

from app.models.base import Base  # ← single source of truth, used by alembic too
from app.core.config import settings


def get_async_database_url() -> str:
    db_url = settings.DATABASE_URL
    if db_url.startswith("mysql://"):
        return db_url.replace("mysql://", "mysql+aiomysql://", 1)
    return db_url


engine = create_async_engine(
    get_async_database_url(),
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# ← REMOVED: Base = declarative_base() — this was overwriting the import above


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()