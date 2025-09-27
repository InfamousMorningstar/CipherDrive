from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from sqlalchemy import text
from contextlib import asynccontextmanager
import os
import asyncio
import logging
from datetime import datetime, timezone

# Import database and models
from database import get_db, create_tables
from models import User, UserRole, UserQuota
from security import get_password_hash
from utils.directories import startup_directory_check
from utils.ports import get_required_ports, validate_port_configuration
from utils.audit import log_audit, AuditActions
from middleware.security import (
    SecurityHeadersMiddleware, 
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    CSRFMiddleware,
    limiter
)

# Import routers
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.files import router as files_router
from routers.shares import router as shares_router
from routers.admin import router as admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Startup and shutdown handlers
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("CipherDrive backend starting up...")
    
    try:
        # Check and create required directories (optional based on env var)
        if os.getenv("SKIP_DIRECTORY_CHECK", "false").lower() != "true":
            startup_directory_check()
        else:
            logger.info("Directory check skipped (SKIP_DIRECTORY_CHECK=true)")
        
        # Create database tables
        create_tables()
        
        # Initialize default users
        await initialize_default_users()
        
        # Log startup success
        logger.info("CipherDrive backend started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise e
    finally:
        logger.info("CipherDrive backend shutting down...")

# Create FastAPI application
app = FastAPI(
    title="CipherDrive API",
    description="Secure file sharing platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - configured for Cloudflare Tunnel
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cipherdrive.ahmxd.net",
        "http://localhost:8069",  # For development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CSRFMiddleware)

# Rate limiting middleware
redis_url = os.getenv("REDIS_URL")
app.add_middleware(RateLimitMiddleware, redis_url=redis_url)

# Add limiter to app state for slowapi
app.state.limiter = limiter

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(files_router)
app.include_router(shares_router)
app.include_router(admin_router)

async def initialize_default_users():
    """Initialize default admin user and cipher user"""
    db = next(get_db())
    
    try:
        # Check if admin user exists
        admin_email = os.getenv("ADMIN_EMAIL", "admin@cipherdrive.local")
        admin_password = os.getenv("ADMIN_PASSWORD", "changeme123")
        
        admin_user = db.query(User).filter(User.email == admin_email).first()
        
        if not admin_user:
            # Create admin user
            admin_user = User(
                username="admin",
                email=admin_email,
                hashed_password=get_password_hash(admin_password),
                role=UserRole.ADMIN,
                is_active=True,
                force_password_reset=False  # Don't force reset for admin
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            # Create unlimited quota for admin
            admin_quota = UserQuota(
                user_id=admin_user.id,
                quota_bytes=999999999999999,  # Essentially unlimited
                used_bytes=0
            )
            db.add(admin_quota)
            
            logger.info(f"Created admin user: {admin_email}")
        
        # Check if cipher user exists
        cipher_user = db.query(User).filter(User.username == "cipher").first()
        
        if not cipher_user:
            # Create cipher user (download-only)
            cipher_user = User(
                username="cipher",
                email="cipher@cipherdrive.local",
                hashed_password=get_password_hash("download"),
                role=UserRole.DOWNLOAD_ONLY,
                is_active=True,
                force_password_reset=False  # No password reset for cipher user
            )
            
            db.add(cipher_user)
            db.commit()
            db.refresh(cipher_user)
            
            # No quota for download-only user
            logger.info("Created cipher user with download-only access")
        
        db.commit()
        
        # Log initialization
        await log_audit(
            action="system_initialization",
            db=db,
            username="system",
            details={"admin_email": admin_email, "cipher_user_created": True}
        )
        
    except Exception as e:
        logger.error(f"Failed to initialize default users: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Health check endpoint
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CipherDrive API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Custom exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return {
        "error": "Endpoint not found",
        "path": request.url.path,
        "method": request.method
    }

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Get port configuration
    try:
        port_config = get_required_ports()
        backend_port = port_config["backend"]
        logger.info(f"Starting server on port {backend_port}")
        
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=backend_port,
            reload=False,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        exit(1)