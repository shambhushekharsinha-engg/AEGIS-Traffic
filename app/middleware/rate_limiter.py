"""
AEGIS-Traffic — Rate Limiting Middleware
Uses slowapi (Starlette-compatible limiter) backed by in-memory storage.

Limits:
  General API:    60 requests / minute per IP
  Auth endpoints: 10 requests / minute per IP  (brute-force protection)
"""

import os
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings

settings = get_settings()


# Global limiter instance — import this in main.py
redis_url = os.getenv("REDIS_URL")
if redis_url:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{settings.rate_limit_per_minute}/minute"],
        storage_uri=redis_url,
    )
else:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{settings.rate_limit_per_minute}/minute"],
    )


def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Custom 429 response body."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "RateLimitExceeded",
            "code": "RATE_LIMIT_EXCEEDED",
            "detail": f"Too many requests. Limit: {exc.limit}. Please retry after 60 seconds.",
            "limit": str(exc.limit),
        },
        headers={"Retry-After": "60"},
    )


# Convenience limit strings
AUTH_LIMIT = f"{settings.auth_rate_limit_per_minute}/minute"
DEFAULT_LIMIT = f"{settings.rate_limit_per_minute}/minute"
