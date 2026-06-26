# app/repositories/user_repository.py
"""
User Repository
Land Intelligence System
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User, None, None]):
    """
    Repository for User entity with extended functionality.
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email_or_username(self, identifier: str) -> Optional[User]:
        """Get user by email or username"""
        result = await self.db.execute(
            select(User).where(
                (User.email == identifier) | (User.username == identifier)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_role(self, role: UserRole) -> List[User]:
        """Get all users with specific role"""
        return await self.list(filters={"role": role})
    
    async def get_active_users(self) -> List[User]:
        """Get all active users"""
        return await self.list(filters={"is_active": True})
    
    async def increment_failed_login(self, user_id: str) -> Optional[User]:
        """Increment failed login attempts counter"""
        user = await self.get(user_id)
        if user:
            user.failed_login_attempts = int(user.failed_login_attempts) + 1
            await self.db.flush()
            await self.db.refresh(user)
        return user
    
    async def reset_failed_login(self, user_id: str) -> Optional[User]:
        """Reset failed login attempts counter"""
        user = await self.get(user_id)
        if user:
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(user)
        return user
    
    async def lock_user(self, user_id: str, lock_minutes: int = 30) -> Optional[User]:
        """Lock user account for specified minutes"""
        from datetime import timedelta
        user = await self.get(user_id)
        if user:
            user.locked_until = datetime.utcnow() + timedelta(minutes=lock_minutes)
            await self.db.flush()
            await self.db.refresh(user)
        return user
    
    async def is_locked(self, user_id: str) -> bool:
        """Check if user account is locked"""
        user = await self.get(user_id)
        if not user or not user.locked_until:
            return False
        return user.locked_until > datetime.utcnow()