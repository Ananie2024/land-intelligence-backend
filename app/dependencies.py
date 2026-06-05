# app/dependencies.py
# app/dependencies.py

"""
Common FastAPI Dependencies
Land Intelligence System
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.middleware.authentication import get_current_user


async def get_database() -> AsyncSession:
    """
    Database dependency wrapper.
    """
    async for db in get_db():
        yield db


CurrentUser = Depends(get_current_user)
DatabaseSession = Depends(get_database)