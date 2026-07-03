"""
Token Blacklist Module
Provides Redis-backed JWT revocation support.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis client singleton (lazy initialized)
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Get or create Redis client singleton for blacklist."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def blacklist_token(jti: str, expires_at: datetime) -> None:
    """
    Add a token JTI to the blacklist with TTL matching remaining token lifetime.

    Args:
        jti: JWT ID claim from the token
        expires_at: UTC datetime when the token expires
    """
    try:
        client = get_redis_client()
        now = datetime.now(timezone.utc)
        ttl = int((expires_at - now).total_seconds())
        if ttl <= 0:
            return  # Token already expired, no need to blacklist

        key = f"token_blacklist:{jti}"
        await client.set(key, "revoked", ex=ttl)
        logger.info(f"Token blacklisted: jti={jti}, ttl={ttl}s")
    except Exception as e:
        logger.error(f"Failed to blacklist token: {str(e)}")
        pass  # Gracefully handle Redis connection failures


async def is_token_blacklisted(jti: str) -> bool:
    """
    Check if a token JTI is in the blacklist.

    Args:
        jti: JWT ID claim from the token

    Returns:
        True if token is blacklisted, False otherwise
    """
    try:
        client = get_redis_client()
        key = f"token_blacklist:{jti}"
        result = await client.get(key)
        return result is not None
    except Exception as e:
        logger.error(f"Failed to check token blacklist: {str(e)}")
        return False
