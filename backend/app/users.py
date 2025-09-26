from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from .database import get_database
from .models import User, File, AuditLog
from .auth import get_password_hash, get_current_admin_user, get_current_user
from .utils import log_audit_event, calculate_storage_usage

class UserService:
    """Service class for user management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(
        self,
        email: str,
        username: str,
        password: str,
        is_admin: bool = False,
        quota_gb: int = 5,
        current_admin: Optional[User] = None
    ) -> User:
        """Create a new user (admin only)"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            or_(User.email == email, User.username == username)
        ).first()
        
        if existing_user:
            if existing_user.email == email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Create new user
        user = User(
            email=email,
            username=username,
            password_hash=get_password_hash(password),
            is_admin=is_admin,
            quota_gb=quota_gb,
            must_change_password=True,
            is_active=True
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Log audit event
        if current_admin:
            log_audit_event(
                self.db,
                str(current_admin.id),
                "user_created",
                "user",
                str(user.id),
                {"created_user_email": email, "is_admin": is_admin},
            )
        
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_all_users(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        active_only: bool = True
    ) -> List[User]:
        """Get all users (admin only)"""
        query = self.db.query(User)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    User.email.ilike(search_pattern),
                    User.username.ilike(search_pattern)
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    def update_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        username: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_admin: Optional[bool] = None,
        quota_gb: Optional[int] = None,
        current_admin: Optional[User] = None
    ) -> User:
        """Update user information (admin only)"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check for email/username conflicts
        if email and email != user.email:
            existing = self.db.query(User).filter(
                and_(User.email == email, User.id != user.id)
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            user.email = email
        
        if username and username != user.username:
            existing = self.db.query(User).filter(
                and_(User.username == username, User.id != user.id)
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            user.username = username
        
        # Update other fields
        if is_active is not None:
            user.is_active = is_active
        if is_admin is not None:
            user.is_admin = is_admin
        if quota_gb is not None:
            user.quota_gb = quota_gb
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        # Log audit event
        if current_admin:
            log_audit_event(
                self.db,
                str(current_admin.id),
                "user_updated",
                "user",
                str(user.id),
                {
                    "updated_fields": {
                        "email": email,
                        "username": username,
                        "is_active": is_active,
                        "is_admin": is_admin,
                        "quota_gb": quota_gb
                    }
                }
            )
        
        return user
    
    def delete_user(self, user_id: str, current_admin: User) -> bool:
        """Delete user (admin only)"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent admin from deleting themselves
        if user.id == current_admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Log audit event before deletion
        log_audit_event(
            self.db,
            str(current_admin.id),
            "user_deleted",
            "user",
            str(user.id),
            {"deleted_user_email": user.email}
        )
        
        self.db.delete(user)
        self.db.commit()
        
        return True
    
    def update_password(self, user: User, new_password: str, mark_changed: bool = True) -> User:
        """Update user password"""
        user.password_hash = get_password_hash(new_password)
        if mark_changed:
            user.must_change_password = False
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        # Log audit event
        log_audit_event(
            self.db,
            str(user.id),
            "password_changed",
            "user",
            str(user.id)
        )
        
        return user
    
    def update_last_login(self, user: User) -> User:
        """Update user's last login timestamp"""
        user.last_login = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_statistics(self, user: User, upload_path: str) -> dict:
        """Get user statistics"""
        # Calculate storage usage
        used_storage = calculate_storage_usage(str(user.id), upload_path)
        
        # Update user's storage usage in database
        if user.used_storage_bytes != used_storage:
            user.used_storage_bytes = used_storage
            self.db.commit()
        
        # Count files and folders
        total_files = self.db.query(File).filter(
            and_(File.owner_id == user.id, File.is_folder == False)
        ).count()
        
        total_folders = self.db.query(File).filter(
            and_(File.owner_id == user.id, File.is_folder == True)
        ).count()
        
        # Calculate quota usage percentage
        quota_bytes = user.quota_gb * 1024 * 1024 * 1024
        usage_percentage = (used_storage / quota_bytes * 100) if quota_bytes > 0 else 0
        
        return {
            "total_files": total_files,
            "total_folders": total_folders,
            "used_storage_bytes": used_storage,
            "quota_bytes": quota_bytes,
            "usage_percentage": round(usage_percentage, 2),
            "last_login": user.last_login,
            "account_created": user.created_at
        }
    
    def get_admin_dashboard_stats(self) -> dict:
        """Get admin dashboard statistics"""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        admin_users = self.db.query(User).filter(User.is_admin == True).count()
        
        total_files = self.db.query(File).filter(File.is_folder == False).count()
        total_folders = self.db.query(File).filter(File.is_folder == True).count()
        
        # Calculate total storage usage
        total_storage = self.db.query(func.sum(User.used_storage_bytes)).scalar() or 0
        
        # Recent logins (last 24 hours)
        yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_logins = self.db.query(User).filter(
            User.last_login >= yesterday
        ).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "total_files": total_files,
            "total_folders": total_folders,
            "total_storage_bytes": total_storage,
            "recent_logins_24h": recent_logins
        }

# Dependency functions
def get_user_service(db: Session = Depends(get_database)) -> UserService:
    """Get user service instance"""
    return UserService(db)