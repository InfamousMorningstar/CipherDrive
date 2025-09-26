import os
import time
import hashlib
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
import logging

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
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS header for production
        if os.getenv("ENVIRONMENT") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # CSP header
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "media-src 'self'; "
            "object-src 'none'; "
            "frame-src 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.clients = {}  # {client_ip: {'requests': count, 'window_start': timestamp}}
        self.window_size = 60  # 1 minute window
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self.get_client_ip(request)
        current_time = time.time()
        
        # Clean up old entries
        self.cleanup_old_entries(current_time)
        
        # Check rate limit for this client
        if self.is_rate_limited(client_ip, current_time):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Record this request
        self.record_request(client_ip, current_time)
        
        response = await call_next(request)
        return response
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def cleanup_old_entries(self, current_time: float):
        """Remove entries older than the window"""
        cutoff_time = current_time - self.window_size
        self.clients = {
            ip: data for ip, data in self.clients.items()
            if data['window_start'] > cutoff_time
        }
    
    def is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client is rate limited"""
        if client_ip not in self.clients:
            return False
        
        client_data = self.clients[client_ip]
        
        # If window has passed, reset
        if current_time - client_data['window_start'] >= self.window_size:
            return False
        
        return client_data['requests'] >= self.requests_per_minute
    
    def record_request(self, client_ip: str, current_time: float):
        """Record a request for the client"""
        if client_ip not in self.clients or \
           current_time - self.clients[client_ip]['window_start'] >= self.window_size:
            # New window
            self.clients[client_ip] = {
                'requests': 1,
                'window_start': current_time
            }
        else:
            # Increment counter
            self.clients[client_ip]['requests'] += 1

class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection middleware"""
    
    def __init__(self, app, secret_key: Optional[str] = None):
        super().__init__(app)
        self.secret_key = secret_key or os.getenv("JWT_SECRET", "fallback-secret")
        self.safe_methods = {"GET", "HEAD", "OPTIONS"}
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF protection for safe methods and API endpoints
        if request.method in self.safe_methods or request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # Skip for certain endpoints
        skip_paths = ["/auth/login", "/auth/refresh", "/shared/"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # For now, we'll rely on JWT tokens for CSRF protection
        # In a full implementation, you'd validate CSRF tokens here
        
        return await call_next(request)

class FileUploadValidationMiddleware(BaseHTTPMiddleware):
    """Validate file uploads for security"""
    
    ALLOWED_EXTENSIONS = {
        '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp',
        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
        '.mp3', '.wav', '.flac', '.aac', '.ogg',
        '.zip', '.rar', '.7z', '.tar', '.gz',
        '.json', '.xml', '.csv', '.html', '.css', '.js'
    }
    
    DANGEROUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.scr', '.com', '.pif', '.vbs', '.js', '.jar',
        '.sh', '.ps1', '.msi', '.dll', '.app', '.deb', '.rpm'
    }
    
    def __init__(self, app, max_file_size: int = 100 * 1024 * 1024):  # 100MB
        super().__init__(app)
        self.max_file_size = max_file_size
    
    async def dispatch(self, request: Request, call_next):
        # Only validate file upload endpoints
        if not (request.method == "POST" and "/files/upload" in request.url.path):
            return await call_next(request)
        
        # File validation will be handled in the upload endpoint
        # This middleware could be extended to scan file contents
        
        return await call_next(request)
    
    def is_safe_filename(self, filename: str) -> bool:
        """Check if filename is safe"""
        import os
        
        # Get file extension
        _, ext = os.path.splitext(filename.lower())
        
        # Check for dangerous extensions
        if ext in self.DANGEROUS_EXTENSIONS:
            return False
        
        # Check for path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            return False
        
        return True

def add_security_middleware(app):
    """Add all security middleware to the app"""
    
    # Rate limiting (adjust based on needs)
    rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    app.add_middleware(RateLimitMiddleware, requests_per_minute=rate_limit_requests)
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # CSRF protection
    app.add_middleware(CSRFProtectionMiddleware)
    
    # File upload validation
    app.add_middleware(FileUploadValidationMiddleware)
    
    # Gzip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Trusted host middleware for production
    if os.getenv("ENVIRONMENT") == "production":
        allowed_hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    
    logger.info("Security middleware initialized")