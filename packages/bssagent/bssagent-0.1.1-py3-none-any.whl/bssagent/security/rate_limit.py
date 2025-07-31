from typing import List, Sequence
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.extension import StrOrCallableStr
from slowapi.util import get_remote_address
import os
import logging


def get_limiter() -> Limiter:
    logger = logging.getLogger(__name__) 
    # Get redis server config from .env
    storage_uri = os.getenv("REDIS_URL")
    if storage_uri is None:
        logger.warning("REDIS_URL is not set, using default redis://localhost:6379")
        storage_uri = "redis://localhost:6379"

    default_limits_env = os.getenv("RATE_LIMIT_DEFAULT_LIMITS")
    default_limits: List[StrOrCallableStr] = ["200/day", "50/hour"]
    if default_limits_env is None:
        logger.warning("RATE_LIMIT_DEFAULT_LIMITS is not set, using default 200 per day, 50 per hour")
        
    else:
        logger.warning(f"RATE_LIMIT_DEFAULT_LIMITS is set to {default_limits_env}")
        default_limits = [x for x in default_limits_env.split(",")]

    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=storage_uri,
        default_limits=default_limits
    )
    return limiter

def get_rate_limit_by_path(path: str) -> str:
    # Get from database
    # If not found, return default
    # If found, return the rate limit
    return "200 per day"
    

def rate_limit_exceeded_handler(request: Request, exc: Exception) -> JSONResponse:
    """Custom rate limit exceeded handler for FastAPI."""
    if isinstance(exc, RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": str(exc),
                "retry_after": getattr(exc, 'retry_after', None)
            }
        )
    # Fallback for other exceptions
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )