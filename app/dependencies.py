# app/dependencies.py
# app/dependencies.py

"""
Common FastAPI Dependencies
Land Intelligence System
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth_dependencies import get_current_user_data


async def get_database() -> AsyncSession:
    """
    Database dependency wrapper.
    """
    async for db in get_db():
        yield db


CurrentUser = Depends(get_current_user_data)
DatabaseSession = Depends(get_database)