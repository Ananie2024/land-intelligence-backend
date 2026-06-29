# app/core/rate_limit.py
"""
Rate Limiting Limiter Setup
Land Intelligence System
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
