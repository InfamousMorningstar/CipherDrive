from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from database import get_db
from models import User, UserRole
from security import verify_password, create_access_token, create_refresh_token, verify_token
from auth import get_current_user, get_client_ip, get_user_agent
from utils.audit import log_audit, AuditActions

from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/auth", tags=["authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == login_data.username) | (User.email == login_data.username)
    ).first()
    
    # Check credentials
    if not user or not verify_password(login_data.password, user.hashed_password):
        # Audit failed login
        await log_audit(
            action=AuditActions.LOGIN_FAILURE,
            db=db,
            username=login_data.username,
            remote_ip=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={"reason": "invalid_credentials"}
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if user is active
    if not user.is_active:
        await log_audit(
            action=AuditActions.LOGIN_FAILURE,
            db=db,
            user=user,
            remote_ip=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={"reason": "account_disabled"}
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    # Create tokens
    token_data = {"sub": str(user.id), "username": user.username, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Audit successful login
    await log_audit(
        action=AuditActions.LOGIN_SUCCESS,
        db=db,
        user=user,
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "force_password_reset": user.force_password_reset,
            "last_login": user.last_login
        }
    )

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    refresh_data: RefreshRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    # Verify refresh token
    payload = verify_token(refresh_data.refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new access token
    token_data = {"sub": str(user.id), "username": user.username, "role": user.role}
    new_access_token = create_access_token(token_data)
    
    # Audit token refresh
    await log_audit(
        action=AuditActions.TOKEN_REFRESH,
        db=db,
        user=user,
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return RefreshResponse(access_token=new_access_token)

@router.post("/logout")
async def logout(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Logout user (mainly for audit purposes)"""
    
    # Audit logout
    await log_audit(
        action=AuditActions.LOGOUT,
        db=db,
        user=current_user,
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request)
    )
    
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "force_password_reset": current_user.force_password_reset,
        "last_login": current_user.last_login,
        "created_at": current_user.created_at
    }

@router.post("/check-token")
async def check_token_validity(
    current_user: User = Depends(get_current_user)
):
    """Check if current token is valid"""
    
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role
    }