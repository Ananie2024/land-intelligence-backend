"""
Database Configuration
Phase 1 — Section 2.3
Land Intelligence System
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from app.core.config import settings

# Convert standard DATABASE_URL to async format if needed
# MySQL async driver requires mysql+aiomysql:// or mysql+asyncmy://
def get_async_database_url() -> str:
    """
    Convert standard DATABASE_URL to async-compatible format.
    Assumes mysql:// becomes mysql+aiomysql://
    """
    db_url = settings.DATABASE_URL
    if db_url.startswith("mysql://"):
        return db_url.replace("mysql://", "mysql+aiomysql://", 1)
    return db_url

# Create async engine
engine = create_async_engine(
    get_async_database_url(),
    echo=False,  # Set to True for SQL logging during development
    future=True,  # Use SQLAlchemy 2.0 style
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for declarative models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()# app/core/database.py
