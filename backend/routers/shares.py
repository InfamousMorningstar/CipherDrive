from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone, timedelta
import os
import mimetypes

from database import get_db
from models import User, UserRole, Share, ShareStatus
from auth import get_current_user, get_normal_or_admin_user, get_client_ip, get_user_agent
from security import generate_secure_token
from utils.audit import log_audit, AuditActions
from routers.files import validate_file_path

from pydantic import BaseModel

router = APIRouter(prefix="/api/shares", tags=["shares"])

class ShareCreate(BaseModel):
    file_path: str
    expires_in_hours: Optional[int] = 24
    max_downloads: Optional[int] = None
    description: Optional[str] = None

class ShareResponse(BaseModel):
    id: int
    share_token: str
    file_path: str
    expires_at: Optional[datetime]
    max_downloads: Optional[int]
    download_count: int
    status: ShareStatus
    created_at: datetime
    share_url: str

class ShareStats(BaseModel):
    total_shares: int
    active_shares: int
    expired_shares: int
    total_downloads: int

@router.post("/", response_model=ShareResponse)
async def create_share(
    share_data: ShareCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_normal_or_admin_user)
):
    """Create a shareable link"""
    
    # Cipher user cannot create shares
    if current_user.role == UserRole.DOWNLOAD_ONLY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Download-only users cannot create shares"
        )
    
    try:
        full_path = validate_file_path(current_user, share_data.file_path)
    except HTTPException:
        raise
    
    # Check if file exists
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if os.path.isdir(full_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot share directories"
        )
    
    # Generate unique share token
    share_token = generate_secure_token(32)
    
    # Calculate expiry
    expires_at = None
    if share_data.expires_in_hours and share_data.expires_in_hours > 0:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=share_data.expires_in_hours)
    
    # Create share
    share = Share(
        share_token=share_token,
        file_path=full_path,
        user_id=current_user.id,
        expires_at=expires_at,
        max_downloads=share_data.max_downloads,
        status=ShareStatus.ACTIVE
    )
    
    db.add(share)
    db.commit()
    db.refresh(share)
    
    # Audit log
    await log_audit(
        action=AuditActions.SHARE_CREATE,
        db=db,
        user=current_user,
        resource_path=full_path,
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={
            "share_token": share_token,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "max_downloads": share_data.max_downloads
        }
    )
    
    # Generate share URL
    base_url = request.headers.get("Origin", "https://cipherdrive.ahmxd.net")
    share_url = f"{base_url}/share/{share_token}"
    
    return ShareResponse(
        id=share.id,
        share_token=share_token,
        file_path=share_data.file_path,
        expires_at=expires_at,
        max_downloads=share_data.max_downloads,
        download_count=0,
        status=ShareStatus.ACTIVE,
        created_at=share.created_at,
        share_url=share_url
    )

@router.get("/", response_model=List[ShareResponse])
async def list_shares(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[ShareStatus] = None
):
    """List user's shares"""
    
    query = db.query(Share).filter(Share.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Share.status == status_filter)
    
    shares = query.offset(skip).limit(limit).all()
    
    base_url = "https://cipherdrive.ahmxd.net"  # Default base URL
    
    response_shares = []
    for share in shares:
        # Convert absolute path back to relative path for display
        relative_path = share.file_path
        if current_user.role != UserRole.DOWNLOAD_ONLY:
            user_base = f"/data/users/{current_user.username}"
            if share.file_path.startswith(user_base):
                relative_path = share.file_path[len(user_base):]
        
        response_shares.append(ShareResponse(
            id=share.id,
            share_token=share.share_token,
            file_path=relative_path,
            expires_at=share.expires_at,
            max_downloads=share.max_downloads,
            download_count=share.download_count,
            status=share.status,
            created_at=share.created_at,
            share_url=f"{base_url}/share/{share.share_token}"
        ))
    
    return response_shares

@router.get("/stats", response_model=ShareStats)
async def get_share_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's share statistics"""
    
    # Count shares by status
    total_shares = db.query(Share).filter(Share.user_id == current_user.id).count()
    active_shares = db.query(Share).filter(
        Share.user_id == current_user.id,
        Share.status == ShareStatus.ACTIVE
    ).count()
    expired_shares = db.query(Share).filter(
        Share.user_id == current_user.id,
        Share.status == ShareStatus.EXPIRED
    ).count()
    
    # Total downloads across all shares
    total_downloads = db.query(Share).filter(Share.user_id == current_user.id).with_entities(
        db.func.sum(Share.download_count)
    ).scalar() or 0
    
    return ShareStats(
        total_shares=total_shares,
        active_shares=active_shares,
        expired_shares=expired_shares,
        total_downloads=total_downloads
    )

@router.delete("/{share_id}")
async def delete_share(
    share_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a share"""
    
    share = db.query(Share).filter(
        Share.id == share_id,
        Share.user_id == current_user.id
    ).first()
    
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    # Store token for audit log before deletion
    share_token = share.share_token
    file_path = share.file_path
    
    db.delete(share)
    db.commit()
    
    # Audit log
    await log_audit(
        action=AuditActions.SHARE_DELETE,
        db=db,
        user=current_user,
        resource_path=file_path,
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"share_token": share_token}
    )
    
    return {"message": "Share deleted successfully"}

@router.get("/public/{share_token}")
async def get_share_info(
    share_token: str,
    db: Session = Depends(get_db)
):
    """Get public share information (no auth required)"""
    
    share = db.query(Share).filter(Share.share_token == share_token).first()
    
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    # Check if share is expired
    if share.expires_at and datetime.now(timezone.utc) > share.expires_at:
        share.status = ShareStatus.EXPIRED
        db.commit()
    
    # Check if share is disabled
    if share.status != ShareStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Share is no longer available"
        )
    
    # Check download limit
    if share.max_downloads and share.download_count >= share.max_downloads:
        share.status = ShareStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Download limit reached"
        )
    
    # Check if file still exists
    if not os.path.exists(share.file_path):
        share.status = ShareStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared file no longer exists"
        )
    
    filename = os.path.basename(share.file_path)
    file_size = os.path.getsize(share.file_path)
    
    # Get owner info (just username)
    owner = db.query(User).filter(User.id == share.user_id).first()
    owner_username = owner.username if owner else "Unknown"
    
    return {
        "filename": filename,
        "file_size": file_size,
        "created_at": share.created_at,
        "expires_at": share.expires_at,
        "download_count": share.download_count,
        "max_downloads": share.max_downloads,
        "owner": owner_username
    }

@router.get("/public/{share_token}/download")
async def download_shared_file(
    share_token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Download a shared file (no auth required)"""
    
    share = db.query(Share).filter(Share.share_token == share_token).first()
    
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    # Check if share is expired
    if share.expires_at and datetime.now(timezone.utc) > share.expires_at:
        share.status = ShareStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Share has expired"
        )
    
    # Check if share is disabled
    if share.status != ShareStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Share is no longer available"
        )
    
    # Check download limit before incrementing
    if share.max_downloads and share.download_count >= share.max_downloads:
        share.status = ShareStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Download limit reached"
        )
    
    # Check if file still exists
    if not os.path.exists(share.file_path):
        share.status = ShareStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared file no longer exists"
        )
    
    # Increment download count
    share.download_count += 1
    
    # Check if this download reaches the limit
    if share.max_downloads and share.download_count >= share.max_downloads:
        share.status = ShareStatus.EXPIRED
    
    db.commit()
    
    # Audit log (no user, so use anonymous)
    await log_audit(
        action=AuditActions.SHARE_ACCESS,
        db=db,
        username="anonymous",
        resource_path=share.file_path,
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={
            "share_token": share_token,
            "download_count": share.download_count,
            "file_size": os.path.getsize(share.file_path)
        }
    )
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(share.file_path)
    if not content_type:
        content_type = "application/octet-stream"
    
    filename = os.path.basename(share.file_path)
    
    return FileResponse(
        path=share.file_path,
        filename=filename,
        media_type=content_type
    )

# Background task to clean up expired shares
async def cleanup_expired_shares(db: Session):
    """Mark expired shares as expired"""
    now = datetime.now(timezone.utc)
    
    expired_shares = db.query(Share).filter(
        Share.status == ShareStatus.ACTIVE,
        Share.expires_at < now
    ).all()
    
    for share in expired_shares:
        share.status = ShareStatus.EXPIRED
        
        # Audit log for expiry
        await log_audit(
            action=AuditActions.SHARE_EXPIRE,
            db=db,
            username="system",
            resource_path=share.file_path,
            details={"share_token": share.share_token, "expired_at": now.isoformat()}
        )
    
    if expired_shares:
        db.commit()
        return len(expired_shares)
    
    return 0