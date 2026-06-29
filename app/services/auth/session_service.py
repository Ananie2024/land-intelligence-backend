# app/services/auth/session_service.py
"""
Session and Token Caching Service
Land Intelligence System
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import hashlib
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class SessionService:
    """
    Session management and token caching service.
    """
    
    def __init__(self):
        # In-memory cache for development
        # In production, use Redis or similar
        self._token_cache: Dict[str, Dict[str, Any]] = {}
        self._refresh_tokens: Dict[str, str] = {}  # refresh_token -> user_id
    
    def store_access_token(self, token: str, user_id: str, expires_in: int) -> None:
        """
        Store access token in cache.
        """
        token_hash = self._hash_token(token)
        self._token_cache[token_hash] = {
            "user_id": user_id,
            "expires_at": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            "created_at": datetime.now(timezone.utc)
        }
    
    def store_refresh_token(self, refresh_token: str, user_id: str) -> None:
        """
        Store refresh token mapping.
        """
        self._refresh_tokens[refresh_token] = user_id
    
    def validate_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Check if access token is valid in cache.
        """
        token_hash = self._hash_token(token)
        cached = self._token_cache.get(token_hash)
        
        if not cached:
            return None
        
        # Check expiration
        if cached["expires_at"] < datetime.now(timezone.utc):
            del self._token_cache[token_hash]
            return None
        
        return cached
    
    def invalidate_access_token(self, token: str) -> None:
        """
        Remove access token from cache (logout).
        """
        token_hash = self._hash_token(token)
        self._token_cache.pop(token_hash, None)
    
    def validate_refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        Validate refresh token and return associated user_id.
        """
        return self._refresh_tokens.get(refresh_token)
    
    def invalidate_refresh_token(self, refresh_token: str) -> None:
        """
        Remove refresh token (logout).
        """
        self._refresh_tokens.pop(refresh_token, None)
    
    def invalidate_all_user_tokens(self, user_id: str) -> None:
        """
        Invalidate all tokens for a user (password change, account lock, etc.).
        """
        # Remove access tokens
        tokens_to_remove = []
        for token_hash, data in self._token_cache.items():
            if data["user_id"] == user_id:
                tokens_to_remove.append(token_hash)
        
        for token_hash in tokens_to_remove:
            del self._token_cache[token_hash]
        
        # Remove refresh tokens
        refresh_to_remove = []
        for refresh_token, uid in self._refresh_tokens.items():
            if uid == user_id:
                refresh_to_remove.append(refresh_token)
        
        for token in refresh_to_remove:
            del self._refresh_tokens[token]
        
        logger.info(f"Invalidated all tokens for user: {user_id}")
    
    def get_user_sessions(self, user_id: str) -> list:
        """
        Get all active sessions for a user.
        """
        sessions = []
        for token_hash, data in self._token_cache.items():
            if data["user_id"] == user_id and data["expires_at"] > datetime.now(timezone.utc):
                sessions.append({
                    "token_hash": token_hash,
                    "created_at": data["created_at"],
                    "expires_at": data["expires_at"]
                })
        return sessions
    
    def _hash_token(self, token: str) -> str:
        """
        Hash token for storage (don't store raw tokens).
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    def cleanup_expired_tokens(self) -> None:
        """
        Remove expired tokens from cache.
        """
        now = datetime.now(timezone.utc)
        expired_access = []
        
        for token_hash, data in self._token_cache.items():
            if data["expires_at"] < now:
                expired_access.append(token_hash)
        
        for token_hash in expired_access:
            del self._token_cache[token_hash]
        
        if expired_access:
            logger.info(f"Cleaned up {len(expired_access)} expired access tokens")


# Global session service instance
session_service = SessionService()