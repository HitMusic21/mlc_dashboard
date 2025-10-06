"""Rate limiting middleware using slowapi."""

from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.requests import Request
from starlette.responses import JSONResponse

# Create limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],  # Default rate limit for all endpoints
    storage_uri="memory://",  # Use in-memory storage (replace with Redis in production)
    strategy="fixed-window",
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": exc.detail.split("Retry after ")[1] if "Retry after" in exc.detail else "60 seconds"
        },
        headers={
            "Retry-After": "60",
            "X-RateLimit-Limit": str(exc.detail.split("/")[0] if "/" in exc.detail else "100"),
            "X-RateLimit-Remaining": "0",
        }
    )
