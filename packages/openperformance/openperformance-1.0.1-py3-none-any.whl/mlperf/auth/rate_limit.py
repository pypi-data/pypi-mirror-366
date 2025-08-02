"""Rate limiting for API endpoints."""

import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from mlperf.auth.models import ApiKey
from mlperf.utils.cache import get_redis_client


def get_identifier(request: Request) -> str:
    """Get identifier for rate limiting."""
    # Check for API key
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"
    
    # Check for authenticated user
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"
    
    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


# Create limiter instance
limiter = Limiter(
    key_func=get_identifier,
    default_limits=["1000 per hour", "100 per minute"],
    headers_enabled=True,
    swallow_errors=False,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Custom rate limiting middleware with Redis backend."""
    
    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis_client = redis_client or get_redis_client()
        self.window_size = 60  # 1 minute window
        
        # Default limits per identifier type
        self.default_limits = {
            "api_key": (5000, 3600),  # 5000 requests per hour
            "user": (1000, 3600),      # 1000 requests per hour
            "ip": (100, 3600),         # 100 requests per hour
        }
        
        # Burst limits (shorter window)
        self.burst_limits = {
            "api_key": (100, 60),      # 100 requests per minute
            "user": (50, 60),          # 50 requests per minute
            "ip": (20, 60),            # 20 requests per minute
        }
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limits before processing request."""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        # Get identifier
        identifier = get_identifier(request)
        identifier_type = identifier.split(":")[0]
        
        # Check rate limits
        try:
            # Check both regular and burst limits
            await self._check_rate_limit(
                identifier,
                identifier_type,
                self.default_limits.get(identifier_type, (100, 3600))
            )
            await self._check_rate_limit(
                f"{identifier}:burst",
                identifier_type,
                self.burst_limits.get(identifier_type, (20, 60))
            )
        except RateLimitExceeded as e:
            return self._rate_limit_exceeded_response(e)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        await self._add_rate_limit_headers(response, identifier, identifier_type)
        
        return response
    
    async def _check_rate_limit(
        self,
        identifier: str,
        identifier_type: str,
        limits: Tuple[int, int]
    ) -> None:
        """Check if rate limit is exceeded."""
        limit, window = limits
        
        # Special handling for API keys - check custom limits
        if identifier_type == "api_key":
            api_key_limit = await self._get_api_key_limit(identifier.split(":")[1])
            if api_key_limit:
                limit = api_key_limit
        
        # Use Redis to track requests
        key = f"rate_limit:{identifier}"
        
        try:
            # Get current count
            current = await self.redis_client.incr(key)
            
            # Set expiry on first request
            if current == 1:
                await self.redis_client.expire(key, window)
            
            # Check limit
            if current > limit:
                # Get remaining time
                ttl = await self.redis_client.ttl(key)
                raise RateLimitExceeded(
                    f"Rate limit exceeded: {current}/{limit} requests in {window}s window. "
                    f"Reset in {ttl}s."
                )
        except Exception as e:
            # If Redis fails, use in-memory fallback
            if not isinstance(e, RateLimitExceeded):
                await self._check_rate_limit_memory(identifier, limit, window)
    
    async def _check_rate_limit_memory(
        self,
        identifier: str,
        limit: int,
        window: int
    ) -> None:
        """In-memory rate limit check (fallback)."""
        current_time = time.time()
        
        # Clean old entries
        if hasattr(self, "_rate_limit_memory"):
            self._rate_limit_memory = {
                k: [t for t in v if current_time - t < window]
                for k, v in self._rate_limit_memory.items()
            }
        else:
            self._rate_limit_memory = defaultdict(list)
        
        # Add current request
        if identifier not in self._rate_limit_memory:
            self._rate_limit_memory[identifier] = []
        self._rate_limit_memory[identifier].append(current_time)
        
        # Check limit
        if len(self._rate_limit_memory[identifier]) > limit:
            raise RateLimitExceeded(
                f"Rate limit exceeded: {len(self._rate_limit_memory[identifier])}/{limit} "
                f"requests in {window}s window."
            )
    
    async def _get_api_key_limit(self, api_key: str) -> Optional[int]:
        """Get custom rate limit for API key."""
        try:
            # Check cache first
            cached = await self.redis_client.get(f"api_key_limit:{api_key}")
            if cached:
                return int(cached)
            
            # Would need to query database here
            # For now, return None to use default
            return None
        except Exception:
            return None
    
    async def _add_rate_limit_headers(
        self,
        response,
        identifier: str,
        identifier_type: str
    ) -> None:
        """Add rate limit headers to response."""
        try:
            # Get limits
            limit, window = self.default_limits.get(identifier_type, (100, 3600))
            
            # Get current count
            key = f"rate_limit:{identifier}"
            current = await self.redis_client.get(key)
            current = int(current) if current else 0
            
            # Get reset time
            ttl = await self.redis_client.ttl(key)
            reset_time = int(time.time() + ttl) if ttl > 0 else int(time.time() + window)
            
            # Add headers
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current))
            response.headers["X-RateLimit-Reset"] = str(reset_time)
            response.headers["X-RateLimit-Window"] = f"{window}s"
        except Exception:
            # Don't fail the request if we can't add headers
            pass
    
    def _rate_limit_exceeded_response(self, exc: RateLimitExceeded) -> JSONResponse:
        """Create rate limit exceeded response."""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": str(exc),
                "type": "rate_limit_exceeded"
            },
            headers={
                "Retry-After": "60",  # Default retry after 60 seconds
            }
        )


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP whitelist middleware for admin endpoints."""
    
    def __init__(self, app, whitelist: Optional[list] = None):
        super().__init__(app)
        self.whitelist = set(whitelist or [])
        self.admin_paths = ["/admin", "/auth/users", "/metrics/detailed"]
    
    async def dispatch(self, request: Request, call_next):
        """Check IP whitelist for admin endpoints."""
        # Check if path requires whitelisting
        requires_whitelist = any(
            request.url.path.startswith(path)
            for path in self.admin_paths
        )
        
        if requires_whitelist and self.whitelist:
            client_ip = get_remote_address(request)
            
            if client_ip not in self.whitelist:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "Access denied from this IP address",
                        "type": "ip_not_whitelisted"
                    }
                )
        
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS (only for HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # CSP
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        return response


def setup_rate_limiting(app):
    """Setup rate limiting for the application."""
    # Add error handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Add middleware
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Return limiter for use with decorators
    return limiter