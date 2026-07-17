"""
Token Blacklist Module
Provides Redis-backed JWT revocation support.

SECURITY NOTE - Fail-Open Behavior:
When Redis is unavailable, is_token_blacklisted() returns False (not blacklisted),
allowing revoked tokens to be treated as valid until they naturally expire.

This is an intentional AVAILABILITY-TRADEOFF design decision:
- Availability is prioritized over immediate revocation enforcement
- During Redis outages, attackers cannot forge new tokens, but logged-out users
  may technically still use their revoked tokens until JWT expiration
- In SECURITY_CRITICAL_MODE, fail-closed behavior is enforced (returns True on Redis failure)

Production deployments should monitor Redis availability and trigger alerts
when the blacklist is in degraded state.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Redis client singleton (lazy initialized)
_redis_client: Optional[redis.Redis] = None

# Track Redis connectivity state for alerting
_redis_blacklist_degraded: bool = False


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
    global _redis_blacklist_degraded
    try:
        client = get_redis_client()
        now = datetime.now(timezone.utc)
        ttl = int((expires_at - now).total_seconds())
        if ttl <= 0:
            return  # Token already expired, no need to blacklist

        key = f"token_blacklist:{jti}"
        await client.set(key, "revoked", ex=ttl)
        # Clear degraded state on successful operation
        _redis_blacklist_degraded = False
        logger.info(f"Token blacklisted: jti={jti}, ttl={ttl}s")
    except Exception as e:
        _redis_blacklist_degraded = True
        logger.error(f"Failed to blacklist token: {str(e)} - Redis outage detected, alerts should be triggered")


async def is_token_blacklisted(jti: str) -> bool:
    """
    Check if a token JTI is in the blacklist.

    SECURITY BEHAVIOR:
    - Normal mode (SECURITY_CRITICAL_MODE=false): Returns False on Redis failure
      This allows revoked tokens to work during outages (availability tradeoff).
    - Security-critical mode (SECURITY_CRITICAL_MODE=true): Returns True on Redis failure
      This blocks all tokens during outages (fail-closed for security).

    Args:
        jti: JWT ID claim from the token

    Returns:
        True if token is blacklisted (or Redis unavailable in security-critical mode),
        False otherwise
    """
    global _redis_blacklist_degraded
    try:
        client = get_redis_client()
        key = f"token_blacklist:{jti}"
        result = await client.get(key)
        # Clear degraded state on successful operation
        _redis_blacklist_degraded = False
        return result is not None
    except Exception as e:
        _redis_blacklist_degraded = True
        # Log at warning level - this indicates an infrastructure issue
        logger.warning(
            f"Redis outage detected during blacklist check: {str(e)}. "
            f"Mode={'fail-closed (security)' if settings.SECURITY_CRITICAL_MODE else 'fail-open (availability)'}"
        )
        # Fail-closed in security-critical mode, fail-open otherwise
        return settings.SECURITY_CRITICAL_MODE


def is_redis_blacklist_degraded() -> bool:
    """
    Check if the Redis blacklist is in a degraded state.

    This function can be used by monitoring/health-check endpoints
    to trigger alerts when Redis is unavailable.

    Returns:
        True if Redis blacklist has experienced recent failures, False otherwise
    """
    return _redis_blacklist_degraded