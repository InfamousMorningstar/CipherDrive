import os
import logging
from datetime import datetime, timedelta
from typing import Optional, List

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File as FastAPIFile, Form, Query, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.orm import Session

from .database import get_database, init_database, check_database_connection
from .models import User
from .auth import (
    authenticate_user, create_access_token, create_refresh_token,
    verify_token, get_current_user, get_current_admin_user,
    create_password_reset_token, verify_password_reset_token,
    send_password_reset_email, send_2fa_email, validate_password_strength,
    get_password_hash, get_client_ip
)
from .users import UserService, get_user_service
from .files import FileService, get_file_service
from .utils import log_audit_event
from .security import SecurityHeadersMiddleware, RateLimitMiddleware, CSRFProtectionMiddleware, FileUploadValidationMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Dropbox Lite API",
    description="Secure file sharing and storage solution",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFProtectionMiddleware)
app.add_middleware(FileUploadValidationMiddleware)

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    is_admin: bool = False
    quota_gb: int = 5

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    quota_gb: Optional[int] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class PasswordReset(BaseModel):
    token: str
    new_password: str

class ShareLinkCreate(BaseModel):
    file_id: str
    expires_in_days: Optional[int] = None
    max_downloads: Optional[int] = None
    password: Optional[str] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    is_admin: bool
    quota_gb: int
    used_storage_bytes: int
    must_change_password: bool
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and create admin user"""
    logger.info("Starting up Dropbox Lite API...")
    
    # Check database connection
    if not check_database_connection():
        logger.error("Database connection failed!")
        return
    
    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return
    
    # Create default admin user
    try:
        from .database import SessionLocal
        db = SessionLocal()
        
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "AdminPassword123!")
        
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                username="admin",
                password_hash=get_password_hash(admin_password),
                is_admin=True,
                is_active=True,
                must_change_password=True
            )
            db.add(admin_user)
            db.commit()
            logger.info(f"Created admin user: {admin_email}")
        
        db.close()
    except Exception as e:
        logger.error(f"Admin user creation failed: {e}")

# Health check
@app.get("/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Health check endpoint"""
    db_status = check_database_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "timestamp": datetime.utcnow()
    }

# Authentication endpoints
@app.post("/auth/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_database)
):
    """Login endpoint"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # Log failed login attempt
        client_ip = await get_client_ip(request)
        log_audit_event(
            db, None, "login_failed", "user", None,
            {"email": form_data.username, "ip": client_ip}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    # Update last login
    user_service = UserService(db)
    user_service.update_last_login(user)
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    # Log successful login
    client_ip = await get_client_ip(request)
    log_audit_event(
        db, str(user.id), "login_successful", "user", str(user.id),
        {"ip": client_ip}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "is_admin": user.is_admin,
            "must_change_password": user.must_change_password
        }
    }

@app.post("/auth/refresh", response_model=dict)
@limiter.limit("10/minute")
async def refresh_token(request: Request, refresh_token: str, db: Session = Depends(get_database)):
    """Refresh access token"""
    try:
        payload = verify_token(refresh_token, "refresh")
        user_id = payload.get("sub")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        new_access_token = create_access_token({"sub": str(user.id)})
        return {"access_token": new_access_token, "token_type": "bearer"}
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@app.post("/auth/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(request: Request, email: EmailStr, db: Session = Depends(get_database)):
    """Request password reset"""
    user = db.query(User).filter(User.email == email).first()
    if user:
        reset_token = create_password_reset_token(db, user)
        if send_password_reset_email(email, reset_token):
            # Log password reset request
            log_audit_event(
                db, str(user.id), "password_reset_requested", "user", str(user.id)
            )
            return {"message": "Password reset email sent"}
    
    # Return same message regardless of user existence (security)
    return {"message": "If an account with that email exists, a password reset link has been sent"}

@app.post("/auth/reset-password")
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    reset_data: PasswordReset,
    db: Session = Depends(get_database)
):
    """Reset password with token"""
    user = verify_password_reset_token(db, reset_data.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    if not validate_password_strength(reset_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )
    
    # Update password
    user_service = UserService(db)
    user_service.update_password(user, reset_data.new_password)
    
    # Mark reset token as used
    from .models import PasswordResetToken
    db.query(PasswordResetToken).filter(
        PasswordResetToken.token == reset_data.token
    ).update({"used": True})
    db.commit()
    
    return {"message": "Password reset successfully"}

# User management endpoints
@app.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.post("/users/change-password")
@limiter.limit("5/minute")
async def change_password(
    request: Request,
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Change user password"""
    from .auth import verify_password
    
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    if not validate_password_strength(password_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )
    
    user_service.update_password(current_user, password_data.new_password)
    return {"message": "Password changed successfully"}

@app.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    admin_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get all users (admin only)"""
    users = user_service.get_all_users(skip=skip, limit=limit, search=search)
    return users

@app.post("/admin/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    admin_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service)
):
    """Create new user (admin only)"""
    if not validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )
    
    user = user_service.create_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        is_admin=user_data.is_admin,
        quota_gb=user_data.quota_gb,
        current_admin=admin_user
    )
    return user

@app.put("/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    admin_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service)
):
    """Update user (admin only)"""
    user = user_service.update_user(
        user_id=user_id,
        email=user_data.email,
        username=user_data.username,
        is_active=user_data.is_active,
        is_admin=user_data.is_admin,
        quota_gb=user_data.quota_gb,
        current_admin=admin_user
    )
    return user

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service)
):
    """Delete user (admin only)"""
    user_service.delete_user(user_id, admin_user)
    return {"message": "User deleted successfully"}

@app.get("/admin/stats")
async def get_admin_stats(
    admin_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service)
):
    """Get admin dashboard statistics"""
    return user_service.get_admin_dashboard_stats()

# File management endpoints
@app.post("/files/upload")
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    parent_folder_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """Upload a file"""
    uploaded_file = await file_service.upload_file(file, parent_folder_id, current_user)
    return {
        "id": str(uploaded_file.id),
        "filename": uploaded_file.original_filename,
        "size": uploaded_file.file_size,
        "mime_type": uploaded_file.mime_type,
        "created_at": uploaded_file.created_at
    }

@app.post("/files/folder")
async def create_folder(
    name: str = Form(...),
    parent_folder_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """Create a new folder"""
    folder = await file_service.create_folder(name, parent_folder_id, current_user)
    return {
        "id": str(folder.id),
        "name": folder.filename,
        "created_at": folder.created_at
    }

@app.get("/files")
async def get_files(
    parent_folder_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """Get files in folder"""
    files = await file_service.get_files_in_folder(parent_folder_id, current_user, skip, limit)
    
    result = []
    for file in files:
        result.append({
            "id": str(file.id),
            "filename": file.original_filename,
            "is_folder": file.is_folder,
            "file_size": file.file_size,
            "mime_type": file.mime_type,
            "created_at": file.created_at,
            "updated_at": file.updated_at
        })
    
    return {"files": result}

@app.get("/files/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """Download a file"""
    file_path, file_record = await file_service.download_file(file_id, current_user)
    
    return FileResponse(
        path=file_path,
        filename=file_record.original_filename,
        media_type=file_record.mime_type or 'application/octet-stream'
    )

@app.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """Delete a file or folder"""
    await file_service.delete_file(file_id, current_user)
    return {"message": "File deleted successfully"}

# Share management endpoints
@app.post("/shares")
async def create_share_link(
    share_data: ShareLinkCreate,
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """Create a shareable link"""
    expires_at = None
    if share_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=share_data.expires_in_days)
    
    shared_link = await file_service.create_share_link(
        share_data.file_id,
        current_user,
        expires_at,
        share_data.max_downloads,
        share_data.password
    )
    
    return {
        "id": str(shared_link.id),
        "share_token": shared_link.share_token,
        "share_url": f"http://localhost:3000/shared/{shared_link.share_token}",
        "expires_at": shared_link.expires_at,
        "max_downloads": shared_link.max_downloads,
        "current_downloads": shared_link.current_downloads,
        "created_at": shared_link.created_at
    }

@app.get("/shares")
async def get_user_shares(
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """Get user's shared links"""
    shares = file_service.get_user_shared_links(current_user)
    
    result = []
    for share in shares:
        result.append({
            "id": str(share.id),
            "file_id": str(share.file_id),
            "filename": share.file.original_filename,
            "share_token": share.share_token,
            "share_url": f"http://localhost:3000/shared/{share.share_token}",
            "expires_at": share.expires_at,
            "max_downloads": share.max_downloads,
            "current_downloads": share.current_downloads,
            "is_active": share.is_active,
            "password_protected": bool(share.password_hash),
            "created_at": share.created_at
        })
    
    return {"shares": result}

@app.delete("/shares/{link_id}")
async def delete_share_link(
    link_id: str,
    current_user: User = Depends(get_current_user),
    file_service: FileService = Depends(get_file_service)
):
    """Delete a shared link"""
    await file_service.delete_shared_link(link_id, current_user)
    return {"message": "Shared link deleted successfully"}

# Public shared file access
@app.get("/shared/{share_token}")
@limiter.limit("20/minute")
async def get_shared_file_info(
    request: Request,
    share_token: str,
    password: Optional[str] = Query(None),
    file_service: FileService = Depends(get_file_service)
):
    """Get shared file information"""
    try:
        file_path, file_record = await file_service.get_shared_file(share_token, password)
        return {
            "filename": file_record.original_filename,
            "file_size": file_record.file_size,
            "mime_type": file_record.mime_type,
            "created_at": file_record.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/shared/{share_token}/download")
@limiter.limit("10/minute")
async def download_shared_file(
    request: Request,
    share_token: str,
    password: Optional[str] = Query(None),
    file_service: FileService = Depends(get_file_service)
):
    """Download shared file"""
    file_path, file_record = await file_service.get_shared_file(share_token, password)
    
    return FileResponse(
        path=file_path,
        filename=file_record.original_filename,
        media_type=file_record.mime_type or 'application/octet-stream'
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("ENVIRONMENT") != "production" else False
    )