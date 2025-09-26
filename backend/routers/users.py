from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timezone
import asyncio

from database import get_db
from models import User, UserRole, UserQuota, AuditLog
from auth import get_current_user, get_admin_user, get_client_ip, get_user_agent
from security import get_password_hash, verify_password, create_password_reset_token, verify_password_reset_token
from utils.audit import log_audit, AuditActions
from utils.directories import initialize_user_directory
from utils.email import send_password_reset_email, send_welcome_email

from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/users", tags=["users"])

# Pydantic models for request/response
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER
    quota_gb: Optional[float] = 5.0

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    quota_gb: Optional[float] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    force_password_reset: bool
    last_login: Optional[datetime]
    created_at: datetime
    quota_gb: Optional[float] = None
    used_gb: Optional[float] = None

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new user (admin only)"""
    
    # Check if username or email already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=user_data.role,
        force_password_reset=True  # Force password reset on first login
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create user quota
    quota_bytes = int(user_data.quota_gb * 1024 ** 3)  # Convert GB to bytes
    user_quota = UserQuota(
        user_id=new_user.id,
        quota_bytes=quota_bytes,
        used_bytes=0
    )
    
    db.add(user_quota)
    db.commit()
    
    # Initialize user directory (if not download-only user)
    if new_user.role != UserRole.DOWNLOAD_ONLY:
        initialize_user_directory(new_user.username)
    
    # Send welcome email
    try:
        await send_welcome_email(new_user.email, new_user.username, user_data.password)
    except Exception as e:
        # Log error but don't fail user creation
        print(f"Failed to send welcome email: {e}")
    
    # Audit log
    await log_audit(
        action=AuditActions.USER_CREATE,
        db=db,
        user=current_user,
        resource_path=f"/users/{new_user.username}",
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"new_user_id": new_user.id, "new_user_role": new_user.role}
    )
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        is_active=new_user.is_active,
        force_password_reset=new_user.force_password_reset,
        last_login=new_user.last_login,
        created_at=new_user.created_at,
        quota_gb=user_data.quota_gb,
        used_gb=0.0
    )

@router.get("/", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 100
):
    """List all users (admin only)"""
    
    users = db.query(User).offset(skip).limit(limit).all()
    
    user_responses = []
    for user in users:
        quota = db.query(UserQuota).filter(UserQuota.user_id == user.id).first()
        quota_gb = quota.quota_bytes / (1024 ** 3) if quota else None
        used_gb = quota.used_bytes / (1024 ** 3) if quota else None
        
        user_responses.append(UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            force_password_reset=user.force_password_reset,
            last_login=user.last_login,
            created_at=user.created_at,
            quota_gb=quota_gb,
            used_gb=used_gb
        ))
    
    return user_responses

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    
    quota = db.query(UserQuota).filter(UserQuota.user_id == current_user.id).first()
    quota_gb = quota.quota_bytes / (1024 ** 3) if quota else None
    used_gb = quota.used_bytes / (1024 ** 3) if quota else None
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        force_password_reset=current_user.force_password_reset,
        last_login=current_user.last_login,
        created_at=current_user.created_at,
        quota_gb=quota_gb,
        used_gb=used_gb
    )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update user (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    if user_data.username is not None:
        # Check if new username is available
        existing_user = db.query(User).filter(
            User.username == user_data.username,
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        user.username = user_data.username
    
    if user_data.email is not None:
        # Check if new email is available
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user.email = user_data.email
    
    if user_data.role is not None:
        user.role = user_data.role
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    # Update quota if specified
    if user_data.quota_gb is not None:
        quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
        if quota:
            quota.quota_bytes = int(user_data.quota_gb * 1024 ** 3)
        else:
            # Create quota if it doesn't exist
            new_quota = UserQuota(
                user_id=user_id,
                quota_bytes=int(user_data.quota_gb * 1024 ** 3),
                used_bytes=0
            )
            db.add(new_quota)
    
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    
    # Audit log
    await log_audit(
        action=AuditActions.USER_UPDATE,
        db=db,
        user=current_user,
        resource_path=f"/users/{user.username}",
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"updated_user_id": user_id, "changes": user_data.dict(exclude_unset=True)}
    )
    
    # Get updated quota info
    quota = db.query(UserQuota).filter(UserQuota.user_id == user.id).first()
    quota_gb = quota.quota_bytes / (1024 ** 3) if quota else None
    used_gb = quota.used_bytes / (1024 ** 3) if quota else None
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        force_password_reset=user.force_password_reset,
        last_login=user.last_login,
        created_at=user.created_at,
        quota_gb=quota_gb,
        used_gb=used_gb
    )

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete user (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Cannot delete yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Store username for audit log before deletion
    deleted_username = user.username
    
    # Delete user (cascading deletes will handle related records)
    db.delete(user)
    db.commit()
    
    # Audit log
    await log_audit(
        action=AuditActions.USER_DELETE,
        db=db,
        user=current_user,
        username=deleted_username,
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"deleted_user_id": user_id}
    )
    
    return {"message": "User deleted successfully"}

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change current user's password"""
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.force_password_reset = False  # Clear forced reset flag
    current_user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    # Audit log
    await log_audit(
        action=AuditActions.PASSWORD_RESET_SUCCESS,
        db=db,
        user=current_user,
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return {"message": "Password changed successfully"}

@router.post("/forgot-password")
async def forgot_password(
    password_reset: PasswordReset,
    request: Request,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    
    user = db.query(User).filter(User.email == password_reset.email).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return {"message": "Password reset email sent if account exists"}
    
    # Generate reset token
    reset_token = create_password_reset_token(user.id)
    
    # Send reset email
    try:
        await send_password_reset_email(user.email, user.username, reset_token)
    except Exception as e:
        # Log error but don't reveal failure to prevent information disclosure
        print(f"Failed to send password reset email: {e}")
    
    # Audit log
    await log_audit(
        action=AuditActions.PASSWORD_RESET_REQUEST,
        db=db,
        user=user,
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return {"message": "Password reset email sent if account exists"}

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    request: Request,
    db: Session = Depends(get_db)
):
    """Confirm password reset"""
    
    user_id = verify_password_reset_token(reset_data.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = get_password_hash(reset_data.new_password)
    user.force_password_reset = False
    user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    # Audit log
    await log_audit(
        action=AuditActions.PASSWORD_RESET_SUCCESS,
        db=db,
        user=user,
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"reset_via_token": True}
    )
    
    return {"message": "Password reset successfully"}