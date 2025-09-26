from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import logging
from typing import Dict, Optional
import redis.asyncio as redis
from datetime import datetime, timezone, timedelta
import asyncio

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # HTTPS enforcement for production
        if request.headers.get("X-Forwarded-Proto") == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # CORS headers for Cloudflare Tunnel
        if request.method == "OPTIONS":
            response.headers["Access-Control-Allow-Origin"] = "https://cipherdrive.ahmxd.net"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With"
            response.headers["Access-Control-Max-Age"] = "86400"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis or in-memory storage"""
    
    def __init__(self, app, redis_url: Optional[str] = None):
        super().__init__(app)
        self.redis_url = redis_url
        self.redis_client = None
        self.memory_store = {}  # Fallback to in-memory if Redis unavailable
        self.use_redis = False
        
    async def setup_redis(self):
        """Setup Redis connection"""
        if self.redis_url:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                await self.redis_client.ping()
                self.use_redis = True
                logger.info("Redis connected for rate limiting")
            except Exception as e:
                logger.warning(f"Redis connection failed, using in-memory storage: {e}")
                self.use_redis = False
        else:
            logger.info("No Redis URL provided, using in-memory rate limiting")
    
    async def get_rate_limit_key(self, identifier: str, window: str) -> str:
        """Generate rate limit key"""
        return f"rate_limit:{identifier}:{window}"
    
    async def check_rate_limit(self, key: str, limit: int, window_seconds: int) -> tuple[bool, int, int]:
        """
        Check rate limit for a key
        Returns (is_allowed, current_count, reset_time)
        """
        now = int(time.time())
        window_start = now - (now % window_seconds)
        reset_time = window_start + window_seconds
        
        if self.use_redis and self.redis_client:
            try:
                # Use Redis sliding window
                pipe = self.redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, now - window_seconds)
                pipe.zadd(key, {str(now): now})
                pipe.zcard(key)
                pipe.expire(key, window_seconds)
                results = await pipe.execute()
                
                current_count = results[2]
                is_allowed = current_count <= limit
                
                return is_allowed, current_count, reset_time
                
            except Exception as e:
                logger.error(f"Redis rate limit check failed: {e}")
                # Fallback to in-memory
                pass
        
        # In-memory fallback
        if key not in self.memory_store:
            self.memory_store[key] = []
        
        # Clean old entries
        self.memory_store[key] = [
            timestamp for timestamp in self.memory_store[key]
            if timestamp > now - window_seconds
        ]
        
        # Add current request
        self.memory_store[key].append(now)
        
        current_count = len(self.memory_store[key])
        is_allowed = current_count <= limit
        
        return is_allowed, current_count, reset_time
    
    async def dispatch(self, request: Request, call_next):
        # Initialize Redis on first request
        if not hasattr(self, '_redis_initialized'):
            await self.setup_redis()
            self._redis_initialized = True
        
        # Rate limiting rules
        client_ip = get_remote_address(request)
        path = request.url.path
        
        # Define rate limits for different endpoints
        limits = self.get_rate_limits(path, request.method)
        
        if limits:
            limit, window_seconds = limits
            key = await self.get_rate_limit_key(client_ip, f"{path}:{request.method}")
            
            is_allowed, current_count, reset_time = await self.check_rate_limit(
                key, limit, window_seconds
            )
            
            if not is_allowed:
                logger.warning(f"Rate limit exceeded for {client_ip} on {path}")
                
                # Add rate limit headers
                response = Response(
                    content='{"error": "Rate limit exceeded"}',
                    status_code=429,
                    media_type="application/json"
                )
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current_count))
                response.headers["X-RateLimit-Reset"] = str(reset_time)
                response.headers["Retry-After"] = str(window_seconds)
                
                return response
        
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        if limits:
            limit, _ = limits
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, limit - current_count))
        
        return response
    
    def get_rate_limits(self, path: str, method: str) -> Optional[tuple[int, int]]:
        """Get rate limits for specific endpoints (requests_per_window, window_seconds)"""
        
        # Authentication endpoints - strict limits
        if "/auth/login" in path:
            return (5, 300)  # 5 attempts per 5 minutes
        
        if "/auth/refresh" in path:
            return (10, 60)  # 10 refreshes per minute
        
        if "/users/forgot-password" in path:
            return (3, 3600)  # 3 attempts per hour
        
        if "/users/reset-password" in path:
            return (5, 3600)  # 5 attempts per hour
        
        # File upload - moderate limits
        if "/files/upload" in path and method == "POST":
            return (10, 60)  # 10 uploads per minute
        
        # Share creation - moderate limits
        if "/shares" in path and method == "POST":
            return (20, 3600)  # 20 shares per hour
        
        # Public share access - generous limits
        if "/shares/public" in path:
            return (100, 3600)  # 100 downloads per hour
        
        # General API - generous limits
        if path.startswith("/api/"):
            return (1000, 3600)  # 1000 requests per hour
        
        # No rate limit for other endpoints
        return None

class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP whitelist middleware for admin endpoints"""
    
    def __init__(self, app, whitelist: list = None):
        super().__init__(app)
        self.whitelist = whitelist or []
    
    async def dispatch(self, request: Request, call_next):
        # Only apply to admin endpoints
        if not request.url.path.startswith("/api/admin/"):
            return await call_next(request)
        
        if not self.whitelist:
            # No whitelist configured, allow all
            return await call_next(request)
        
        client_ip = get_remote_address(request)
        
        # Check X-Forwarded-For for proxied requests
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
        
        if client_ip not in self.whitelist:
            logger.warning(f"IP {client_ip} blocked from admin endpoint {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied from this IP address"
            )
        
        return await call_next(request)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for monitoring"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get client info
        client_ip = get_remote_address(request)
        user_agent = request.headers.get("User-Agent", "unknown")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"IP: {client_ip} - "
            f"Time: {process_time:.3f}s - "
            f"UA: {user_agent[:100]}"
        )
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

# Limiter instance for additional endpoints
limiter = Limiter(key_func=get_remote_address)

# Rate limiting decorators for specific endpoints
def rate_limit_strict(rate: str):
    """Strict rate limiting decorator"""
    return limiter.limit(rate)

def rate_limit_moderate(rate: str):
    """Moderate rate limiting decorator"""  
    return limiter.limit(rate)

def rate_limit_generous(rate: str):
    """Generous rate limiting decorator"""
    return limiter.limit(rate)

# CSRF protection
class CSRFMiddleware(BaseHTTPMiddleware):
    """Basic CSRF protection"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF for GET, HEAD, OPTIONS
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)
        
        # Skip for API endpoints with proper authentication
        if request.url.path.startswith("/api/"):
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                return await call_next(request)
        
        # Check Origin header
        origin = request.headers.get("Origin")
        host = request.headers.get("Host")
        
        if origin:
            # Allow requests from same origin or whitelisted origins
            allowed_origins = [
                "https://cipherdrive.ahmxd.net",
                f"https://{host}" if host else None
            ]
            
            if origin not in allowed_origins:
                logger.warning(f"CSRF: Blocked request from origin {origin}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF validation failed"
                )
        
        return await call_next(request)

# Security utilities
def get_client_real_ip(request: Request) -> str:
    """Get the real client IP, respecting proxy headers"""
    # Check Cloudflare headers first
    cf_connecting_ip = request.headers.get("CF-Connecting-IP")
    if cf_connecting_ip:
        return cf_connecting_ip
    
    # Check X-Forwarded-For
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    # Check X-Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"

def is_https_request(request: Request) -> bool:
    """Check if request is HTTPS, considering proxy headers"""
    # Check X-Forwarded-Proto
    proto = request.headers.get("X-Forwarded-Proto")
    if proto:
        return proto.lower() == "https"
    
    # Check URL scheme
    return request.url.scheme == "https"