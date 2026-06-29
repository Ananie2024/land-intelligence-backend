"""
Security Module
Phase 1 — Section 2.3
Land Intelligence System
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from uuid import uuid4
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from passlib.context import CryptContext
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing contexts
pwd_context = PasswordHasher()
# Fallback for legacy bcrypt hashes during migration
legacy_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    Supports both Argon2 (current) and bcrypt (legacy) hashes.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password matches
    """
    if not hashed_password:
        return False
    
    try:
        # Argon2 hash (current)
        if hashed_password.startswith('$argon2'):
            pwd_context.verify(hashed_password, plain_password)
            return True
        # Bcrypt hash (legacy migration)
        elif hashed_password.startswith('$2b$') or hashed_password.startswith('$2a$'):
            return legacy_context.verify(plain_password, hashed_password)
        else:
            logger.warning(f"Unknown password hash format: {hashed_password[:10]}...")
            return False
    except VerifyMismatchError:
        return False
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using Argon2.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time override
        
    Returns:
        str: JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access", "jti": str(uuid4())})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create access token: {str(e)}")
        raise


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Data to encode in token
        
    Returns:
        str: JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh", "jti": str(uuid4())})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create refresh token: {str(e)}")
        raise


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Optional[Dict[str, Any]]: Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return None
    except InvalidTokenError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        return None


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Create a new access token using a valid refresh token.
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        Optional[str]: New access token if refresh token is valid, None otherwise
    """
    payload = verify_token(refresh_token)
    
    if not payload:
        return None
    
    # Verify this is a refresh token
    if payload.get("type") != "refresh":
        logger.warning("Attempted to use non-refresh token as refresh token")
        return None
    
    # Create new access token with same subject
    user_id = payload.get("sub")
    if not user_id:
        logger.warning("Refresh token missing subject claim")
        return None
    
    return create_access_token(data={"sub": user_id})# app/core/security.py
