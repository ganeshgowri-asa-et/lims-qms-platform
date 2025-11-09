"""
API Gateway Middleware
Rate limiting, request logging, versioning, authentication
"""
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers
from typing import Callable, Dict, Optional
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
import logging
from backend.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware
    Implements token bucket algorithm for API rate limiting
    """

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Number of calls allowed
        self.period = period  # Time period in seconds
        self.clients: Dict[str, Dict] = defaultdict(lambda: {
            'tokens': calls,
            'last_update': time.time()
        })

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting"""

        # Get client identifier (IP or API key)
        client_id = self._get_client_id(request)

        # Check rate limit
        if not self._check_rate_limit(client_id):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": self.period
                },
                headers={
                    "X-RateLimit-Limit": str(self.calls),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + self.period))
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        client_data = self.clients[client_id]
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(int(client_data['tokens']))
        response.headers["X-RateLimit-Reset"] = str(int(client_data['last_update'] + self.period))

        return response

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key:{api_key}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"

        return f"ip:{request.client.host}"

    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        client_data = self.clients[client_id]
        current_time = time.time()

        # Refill tokens based on time elapsed
        time_elapsed = current_time - client_data['last_update']
        tokens_to_add = (time_elapsed / self.period) * self.calls
        client_data['tokens'] = min(
            self.calls,
            client_data['tokens'] + tokens_to_add
        )
        client_data['last_update'] = current_time

        # Check if tokens available
        if client_data['tokens'] >= 1:
            client_data['tokens'] -= 1
            return True

        return False


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Request/Response logging middleware
    Logs all API requests and responses for monitoring and debugging
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response"""

        # Start timer
        start_time = time.time()

        # Get request details
        request_id = request.headers.get("X-Request-ID", f"{time.time()}")
        request_body = None

        # Read request body for logging (if applicable)
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    request_body = body_bytes.decode()
                # Re-populate request body for downstream processing
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive
            except:
                pass

        # Log request
        logger.info(f"Request: {request.method} {request.url.path} [ID: {request_id}]")

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"[ID: {request_id}] [Status: {response.status_code}] "
                f"[Duration: {duration:.3f}s]"
            )

            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration:.3f}"

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"[ID: {request_id}] [Duration: {duration:.3f}s] "
                f"[Error: {str(e)}]"
            )
            raise


class APIVersioningMiddleware(BaseHTTPMiddleware):
    """
    API versioning middleware
    Handles multiple API versions (v1, v2, etc.)
    """

    def __init__(self, app, default_version: str = "v1"):
        super().__init__(app)
        self.default_version = default_version

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with versioning"""

        # Get API version from header or URL
        api_version = request.headers.get("X-API-Version")

        if not api_version:
            # Extract from URL path if present
            path_parts = request.url.path.split('/')
            if len(path_parts) > 2 and path_parts[2].startswith('v'):
                api_version = path_parts[2]
            else:
                api_version = self.default_version

        # Add version to request state
        request.state.api_version = api_version

        # Process request
        response = await call_next(request)

        # Add version header to response
        response.headers["X-API-Version"] = api_version

        return response


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS and security middleware
    Adds security headers and validates CORS requests
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response"""

        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
        )

        return response


class RequestThrottlingMiddleware(BaseHTTPMiddleware):
    """
    Request throttling middleware
    Prevents abuse by limiting concurrent requests per client
    """

    def __init__(self, app, max_concurrent: int = 10):
        super().__init__(app)
        self.max_concurrent = max_concurrent
        self.active_requests: Dict[str, int] = defaultdict(int)
        self.lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Throttle concurrent requests"""

        client_id = self._get_client_id(request)

        async with self.lock:
            # Check concurrent requests
            if self.active_requests[client_id] >= self.max_concurrent:
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={
                        "detail": "Too many concurrent requests. Please try again later.",
                        "max_concurrent": self.max_concurrent
                    }
                )

            # Increment counter
            self.active_requests[client_id] += 1

        try:
            # Process request
            response = await call_next(request)
            return response

        finally:
            # Decrement counter
            async with self.lock:
                self.active_requests[client_id] -= 1

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key:{api_key}"

        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"

        return f"ip:{request.client.host}"
