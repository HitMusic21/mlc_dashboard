"""Middleware for automatic activity logging of API requests."""

import time
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.crud import activity as activity_crud
from app.db.session import AsyncSessionLocal
from app.models.activity_log import ActivityStatus


class ActivityLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log user activities and API requests.

    Logs significant API requests to the activity_logs table for audit trail,
    security monitoring, and user activity tracking.
    """

    # Paths to skip logging (health checks, static files, docs)
    SKIP_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/api/openapi.json"}

    # HTTP methods to log (exclude OPTIONS for CORS preflight)
    LOG_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log activity if applicable.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response from downstream handler
        """
        # Skip logging for certain paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        # Only log certain HTTP methods (mutations, not reads)
        if request.method not in self.LOG_METHODS:
            return await call_next(request)

        # Get user from request state (set by auth dependency)
        user = getattr(request.state, "user", None)
        user_id: Optional[int] = user.id if user else None

        # Extract action from path
        action = self._extract_action(request)

        # Track request timing
        start_time = time.time()

        # Execute request
        try:
            response = await call_next(request)
            status = (
                ActivityStatus.SUCCESS
                if 200 <= response.status_code < 400
                else ActivityStatus.FAILURE
            )
            duration_ms = int((time.time() - start_time) * 1000)

            # Log activity asynchronously
            await self._log_activity(
                user_id=user_id,
                action=action,
                description=f"{request.method} {request.url.path}",
                status=status,
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                metadata={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )

            return response

        except Exception as e:
            # Log failed request
            duration_ms = int((time.time() - start_time) * 1000)
            await self._log_activity(
                user_id=user_id,
                action=action,
                description=f"{request.method} {request.url.path} - Error: {str(e)[:100]}",
                status=ActivityStatus.FAILURE,
                ip_address=self._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                metadata={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e)[:200],
                    "duration_ms": duration_ms,
                },
            )
            raise

    def _extract_action(self, request: Request) -> str:
        """Extract action name from request path.

        Args:
            request: HTTP request

        Returns:
            Action string in format "entity.verb"
        """
        path = request.url.path
        method = request.method

        # Map common patterns to actions
        if "/auth/login" in path:
            return "user.login"
        elif "/auth/logout" in path:
            return "user.logout"
        elif "/auth/refresh" in path:
            return "user.refresh_token"
        elif "/catalog" in path and method == "POST":
            return "catalog.upload"
        elif "/catalog" in path and method == "DELETE":
            return "catalog.delete"
        elif "/works" in path and method == "POST":
            return "work.create"
        elif "/works" in path and method == "PUT":
            return "work.update"
        elif "/works" in path and method == "DELETE":
            return "work.delete"
        elif "/preferences" in path and method == "PUT":
            return "preferences.update"
        elif "/preferences/layout" in path:
            return "preferences.update_layout"
        elif "/preferences/searches" in path and method == "POST":
            return "preferences.save_search"
        elif "/preferences/searches" in path and method == "DELETE":
            return "preferences.delete_search"
        elif "/notifications" in path and "read" in path:
            return "notification.mark_read"
        elif "/notifications" in path and method == "DELETE":
            return "notification.delete"
        else:
            # Generic action based on method and path segment
            entity = path.split("/")[3] if len(path.split("/")) > 3 else "api"
            verb = {
                "POST": "create",
                "PUT": "update",
                "PATCH": "update",
                "DELETE": "delete",
            }.get(method, "action")
            return f"{entity}.{verb}"

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request.

        Args:
            request: HTTP request

        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (from proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct client
        return request.client.host if request.client else "unknown"

    async def _log_activity(
        self,
        action: str,
        description: str,
        status: ActivityStatus,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        """Log activity to database.

        Args:
            action: Action identifier
            description: Human-readable description
            status: Activity status
            user_id: Optional user ID
            ip_address: Optional client IP
            user_agent: Optional user agent string
            metadata: Optional additional metadata
        """
        try:
            async with AsyncSessionLocal() as session:
                await activity_crud.log_activity(
                    session,
                    {
                        "user_id": user_id,
                        "action": action,
                        "description": description,
                        "status": status,
                        "ip_address": ip_address,
                        "user_agent": user_agent,
                        "metadata": metadata,
                    },
                )
        except Exception as e:
            # Don't fail the request if logging fails
            # Just log the error (could use proper logging here)
            print(f"Failed to log activity: {e}")
