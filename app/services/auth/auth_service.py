# app/services/auth/auth_service.py
"""
Authentication Service
Land Intelligence System
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.schemas.user_schema import UserLogin, TokenResponse, UserResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """
    Business logic layer for authentication and authorization.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register_user(self, user_data: Dict[str, Any]) -> User:
        """
        Register a new user account.
        """
        # Check if user already exists
        existing = await self.user_repo.get_by_email_or_username(str(user_data.get("email", "")))
        if existing:
            raise ValueError(f"User with email '{user_data.get('email')}' or username '{user_data.get('username')}' already exists.")
        
        # Hash password
        password = user_data.pop("password", None)
        if not password:
            raise ValueError("Password is required")
        
        hashed_password = get_password_hash(password)
        user_data["hashed_password"] = hashed_password
        
        # Ensure role is proper enum
        if "role" in user_data and isinstance(user_data["role"], str):
            user_data["role"] = UserRole(user_data["role"])
        
        # Create user using repository
        user = await self.user_repo.create_by_dict(user_data)
        
        logger.info(f"User registered: {user.email} with role {user.role.value}")
        return user

    async def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """
        Authenticate user with username/email and password.
        """
        # Find user by email or username
        user = await self.user_repo.get_by_email_or_username(login_data.username)
        
        if not user:
            logger.warning(f"Login attempt with non-existent user: {login_data.username}")
            return None
        
        # Check if account is locked
        if await self.user_repo.is_locked(str(user.id)):
            logger.warning(f"Login attempt on locked account: {login_data.username}")
            return None
        
        # Verify password - extract string values from columns
        hashed_pw = str(user.hashed_password) if user.hashed_password else ""
        if not verify_password(login_data.password, hashed_pw):
            # Increment failed login attempts
            await self.user_repo.increment_failed_login(str(user.id))
            
            # Lock account after 5 failed attempts
            failed_attempts = int(str(user.failed_login_attempts)) if user.failed_login_attempts else 0
            if failed_attempts + 1 >= 5:
                await self.user_repo.lock_user(str(user.id), lock_minutes=30)
                logger.warning(f"Account locked due to multiple failed attempts: {login_data.username}")
            
            return None
        
        # Reset failed login attempts on successful login
        await self.user_repo.reset_failed_login(str(user.id))
        
        logger.info(f"User authenticated: {login_data.username}")
        return user

    async def login(self, login_data: UserLogin) -> TokenResponse:
        """
        Authenticate user and generate JWT tokens.
        """
        user = await self.authenticate_user(login_data)
        
        if not user:
            raise ValueError("Invalid credentials")
        
        if not user.is_active:
            raise ValueError("Account is deactivated")
        
        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        # Convert to response schema
        user_response = self._user_to_response(user)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )

    async def refresh_token(self, refresh_token: str) -> Optional[TokenResponse]:
        """
        Generate new access token from refresh token.
        """
        # Verify refresh token
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            logger.warning("Invalid refresh token used")
            return None
        
        # Get user
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = await self.user_repo.get(user_id)
        if not user or not user.is_active:
            return None
        
        # Generate new access token
        new_access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        
        user_response = self._user_to_response(user)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )

    async def logout(self, token: str) -> bool:
        """
        Invalidate token by adding to blacklist.
        TODO: Implement token blacklist using Redis
        """
        logger.info(f"Logout requested for token: {token[:20]}...")
        return True

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change user password.
        """
        user = await self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        hashed_pw = str(user.hashed_password) if user.hashed_password else ""
        if not verify_password(current_password, hashed_pw):
            raise ValueError("Current password is incorrect")
        
        # Hash new password
        new_hashed = get_password_hash(new_password)
        user.hashed_password = new_hashed
        await self.db.flush()
        await self.db.refresh(user)
        
        logger.info(f"Password changed for user: {user.email}")
        return True

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return await self.user_repo.get(user_id)

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user information"""
        # Handle role enum conversion
        if "role" in update_data and isinstance(update_data["role"], str):
            update_data["role"] = UserRole(update_data["role"])
        
        user = await self.user_repo.update_by_dict(user_id, update_data)
        if user:
            logger.info(f"User updated: {user.email}")
        return user

    async def delete_user(self, user_id: str) -> bool:
        """Soft delete user"""
        result = await self.user_repo.soft_delete(user_id)
        if result:
            logger.info(f"User deleted: {user_id}")
        return result

    async def list_users(self, role: Optional[UserRole] = None, skip: int = 0, limit: int = 100) -> list:
        """List users with optional role filter"""
        filters = {"is_active": True}
        if role:
            filters["role"] = role.value
        return await self.user_repo.list(filters=filters, skip=skip, limit=limit)

    def _user_to_response(self, user: User) -> UserResponse:
        """Convert User model to UserResponse schema"""
        return UserResponse(
            id=str(user.id),
            email=str(user.email),
            username=str(user.username),
            full_name=str(user.full_name) if user.full_name else None,
            role=user.role,
            parish_id=str(user.parish_id) if user.parish_id else None,
            is_active=bool(user.is_active),
            is_verified=bool(user.is_verified),
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )