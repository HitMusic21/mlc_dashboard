"""Security headers middleware for protecting against common web vulnerabilities."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # Content Security Policy - Prevents XSS attacks
        # Adjust based on your needs (especially 'unsafe-inline' for development)
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Adjust for production
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'self'",
            "base-uri 'self'",
            "form-action 'self'",
        ]

        if settings.DEBUG:
            # More permissive CSP for development
            csp_directives.append("connect-src 'self' ws: wss:")

        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Strict Transport Security - Enforces HTTPS
        if not settings.DEBUG:
            # Only enable HSTS in production (requires HTTPS)
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # X-Frame-Options - Prevents clickjacking
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

        # X-Content-Type-Options - Prevents MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection - Additional XSS protection for older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy - Controls referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions-Policy - Restricts browser features
        permissions_policies = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_policies)

        # X-Permitted-Cross-Domain-Policies - Restricts cross-domain policies
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Cache-Control for sensitive endpoints
        if "/api/v1/auth/" in str(request.url.path):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"

        return response
