from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from database import get_db
from models import User, UserRole, UserQuota, AuditLog, Share, FileMetadata
from auth import get_admin_user, get_client_ip, get_user_agent
from utils.audit import log_audit, AuditActions

from pydantic import BaseModel

router = APIRouter(prefix="/api/admin", tags=["admin"])

class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_files: int
    total_storage_used: int
    total_shares: int
    active_shares: int
    total_downloads: int

class UserStats(BaseModel):
    user_id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    last_login: Optional[datetime]
    storage_used: int
    storage_quota: int
    total_files: int
    total_shares: int
    total_downloads: int

class AuditLogEntry(BaseModel):
    id: int
    username: Optional[str]
    action: str
    resource_path: Optional[str]
    remote_ip: Optional[str]
    user_agent: Optional[str]
    details: Optional[str]
    timestamp: datetime

class DiskUsage(BaseModel):
    path: str
    total_bytes: int
    used_bytes: int
    available_bytes: int
    usage_percentage: float

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get system statistics (admin only)"""
    
    # User statistics
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # File statistics
    total_files = db.query(FileMetadata).filter(FileMetadata.is_directory == False).count()
    total_storage_used = db.query(func.sum(UserQuota.used_bytes)).scalar() or 0
    
    # Share statistics
    total_shares = db.query(Share).count()
    active_shares = db.query(Share).filter(Share.status == "active").count()
    total_downloads = db.query(func.sum(Share.download_count)).scalar() or 0
    
    return SystemStats(
        total_users=total_users,
        active_users=active_users,
        total_files=total_files,
        total_storage_used=total_storage_used,
        total_shares=total_shares,
        active_shares=active_shares,
        total_downloads=total_downloads
    )

@router.get("/users/stats", response_model=List[UserStats])
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 100
):
    """Get detailed user statistics (admin only)"""
    
    users = db.query(User).offset(skip).limit(limit).all()
    user_stats = []
    
    for user in users:
        # Get quota info
        quota = db.query(UserQuota).filter(UserQuota.user_id == user.id).first()
        storage_used = quota.used_bytes if quota else 0
        storage_quota = quota.quota_bytes if quota else 0
        
        # Get file count
        total_files = db.query(FileMetadata).filter(
            FileMetadata.owner_id == user.id,
            FileMetadata.is_directory == False
        ).count()
        
        # Get share count
        total_shares = db.query(Share).filter(Share.user_id == user.id).count()
        
        # Get total downloads
        total_downloads = db.query(func.sum(Share.download_count)).filter(
            Share.user_id == user.id
        ).scalar() or 0
        
        user_stats.append(UserStats(
            user_id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
            last_login=user.last_login,
            storage_used=storage_used,
            storage_quota=storage_quota,
            total_files=total_files,
            total_shares=total_shares,
            total_downloads=total_downloads
        ))
    
    return user_stats

@router.get("/audit-logs", response_model=List[AuditLogEntry])
async def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None,
    username: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get audit logs with filtering (admin only)"""
    
    query = db.query(AuditLog).order_by(desc(AuditLog.timestamp))
    
    # Apply filters
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    
    if username:
        query = query.filter(AuditLog.username.ilike(f"%{username}%"))
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    logs = query.offset(skip).limit(limit).all()
    
    return [
        AuditLogEntry(
            id=log.id,
            username=log.username,
            action=log.action,
            resource_path=log.resource_path,
            remote_ip=log.remote_ip,
            user_agent=log.user_agent,
            details=log.details,
            timestamp=log.timestamp
        )
        for log in logs
    ]

@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Activate a user account (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_active:
        return {"message": "User is already active"}
    
    user.is_active = True
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    # Audit log
    await log_audit(
        action=AuditActions.USER_ACTIVATE,
        db=db,
        user=current_user,
        resource_path=f"/users/{user.username}",
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"activated_user_id": user_id}
    )
    
    return {"message": "User activated successfully"}

@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Deactivate a user account (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Cannot deactivate yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    if not user.is_active:
        return {"message": "User is already inactive"}
    
    user.is_active = False
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    # Audit log
    await log_audit(
        action=AuditActions.USER_DEACTIVATE,
        db=db,
        user=current_user,
        resource_path=f"/users/{user.username}",
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"deactivated_user_id": user_id}
    )
    
    return {"message": "User deactivated successfully"}

@router.put("/users/{user_id}/quota")
async def update_user_quota(
    user_id: int,
    quota_gb: float,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update user's storage quota (admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    quota_bytes = int(quota_gb * 1024 ** 3)  # Convert GB to bytes
    
    quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
    if quota:
        old_quota = quota.quota_bytes
        quota.quota_bytes = quota_bytes
        quota.updated_at = datetime.now(timezone.utc)
    else:
        old_quota = 0
        quota = UserQuota(
            user_id=user_id,
            quota_bytes=quota_bytes,
            used_bytes=0
        )
        db.add(quota)
    
    db.commit()
    
    # Audit log
    await log_audit(
        action=AuditActions.QUOTA_UPDATE,
        db=db,
        user=current_user,
        resource_path=f"/users/{user.username}",
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={
            "user_id": user_id,
            "old_quota_bytes": old_quota,
            "new_quota_bytes": quota_bytes
        }
    )
    
    return {
        "message": "Quota updated successfully",
        "user": user.username,
        "new_quota_gb": quota_gb
    }

@router.get("/disk-usage", response_model=List[DiskUsage])
async def get_disk_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get disk usage information for key paths (admin only)"""
    
    import shutil
    
    key_paths = [
        "/mnt/app-pool/cipherdrive",
        "/mnt/Centauri/cipherdrive",
        "/data"
    ]
    
    disk_usage = []
    
    for path in key_paths:
        try:
            if os.path.exists(path):
                total, used, free = shutil.disk_usage(path)
                usage_percentage = (used / total * 100) if total > 0 else 0
                
                disk_usage.append(DiskUsage(
                    path=path,
                    total_bytes=total,
                    used_bytes=used,
                    available_bytes=free,
                    usage_percentage=usage_percentage
                ))
        except Exception as e:
            # Add entry with error info
            disk_usage.append(DiskUsage(
                path=path,
                total_bytes=0,
                used_bytes=0,
                available_bytes=0,
                usage_percentage=0
            ))
    
    return disk_usage

@router.delete("/audit-logs/cleanup")
async def cleanup_audit_logs(
    days: int = 90,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Clean up old audit logs (admin only)"""
    
    if days < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete audit logs newer than 30 days"
        )
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Count logs to be deleted
    logs_to_delete = db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).count()
    
    # Delete old logs
    db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).delete()
    db.commit()
    
    # Audit log for cleanup
    await log_audit(
        action="audit_log_cleanup",
        db=db,
        user=current_user,
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={
            "cutoff_date": cutoff_date.isoformat(),
            "logs_deleted": logs_to_delete
        }
    )
    
    return {
        "message": "Audit logs cleaned up successfully",
        "logs_deleted": logs_to_delete,
        "cutoff_date": cutoff_date
    }

@router.get("/shares/all", response_model=List[dict])
async def get_all_shares(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 100
):
    """Get all shares across all users (admin only)"""
    
    shares = db.query(Share).join(User).offset(skip).limit(limit).all()
    
    result = []
    for share in shares:
        result.append({
            "id": share.id,
            "share_token": share.share_token,
            "file_path": share.file_path,
            "owner": share.user.username,
            "owner_email": share.user.email,
            "expires_at": share.expires_at,
            "max_downloads": share.max_downloads,
            "download_count": share.download_count,
            "status": share.status,
            "created_at": share.created_at
        })
    
    return result

@router.delete("/shares/{share_id}")
async def delete_any_share(
    share_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete any share (admin only)"""
    
    share = db.query(Share).filter(Share.id == share_id).first()
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found"
        )
    
    # Get owner info before deletion
    owner = db.query(User).filter(User.id == share.user_id).first()
    owner_username = owner.username if owner else "unknown"
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
        details={
            "share_token": share_token,
            "original_owner": owner_username,
            "admin_action": True
        }
    )
    
    return {"message": "Share deleted successfully"}