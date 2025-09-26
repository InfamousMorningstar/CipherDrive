import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from models import AuditLog, User
from database import get_db
import logging
from pathlib import Path
import aiofiles

# Configure audit logger
AUDIT_LOG_PATH = "/mnt/app-pool/cipherdrive/logs/audit.log"

class AuditLogger:
    def __init__(self):
        self.ensure_log_directory()
        
    def ensure_log_directory(self):
        """Ensure audit log directory exists"""
        try:
            os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
        except Exception as e:
            print(f"Failed to create audit log directory: {e}")
    
    async def log_action(
        self,
        db: Session,
        action: str,
        user: Optional[User] = None,
        username: Optional[str] = None,
        resource_path: Optional[str] = None,
        remote_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log an action to both database and file"""
        timestamp = datetime.now(timezone.utc)
        
        # Prepare log data
        log_data = {
            "timestamp": timestamp.isoformat(),
            "username": username or (user.username if user else "anonymous"),
            "user_id": user.id if user else None,
            "action": action,
            "resource_path": resource_path,
            "remote_ip": remote_ip,
            "user_agent": user_agent,
            "details": details
        }
        
        # Log to database
        try:
            audit_entry = AuditLog(
                user_id=user.id if user else None,
                username=username or (user.username if user else "anonymous"),
                action=action,
                resource_path=resource_path,
                remote_ip=remote_ip,
                user_agent=user_agent,
                details=json.dumps(details) if details else None,
                timestamp=timestamp
            )
            db.add(audit_entry)
            db.commit()
        except Exception as e:
            print(f"Failed to log to database: {e}")
            db.rollback()
        
        # Log to file
        await self._log_to_file(log_data)
    
    async def _log_to_file(self, log_data: Dict[str, Any]):
        """Write log entry to file"""
        try:
            log_line = json.dumps(log_data) + "\n"
            async with aiofiles.open(AUDIT_LOG_PATH, 'a') as f:
                await f.write(log_line)
        except Exception as e:
            print(f"Failed to write audit log to file: {e}")

# Global audit logger instance
audit_logger = AuditLogger()

# Action constants
class AuditActions:
    # Authentication
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_SUCCESS = "password_reset_success"
    TOKEN_REFRESH = "token_refresh"
    
    # File operations
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    FILE_DELETE = "file_delete"
    FILE_MOVE = "file_move"
    FILE_COPY = "file_copy"
    FOLDER_CREATE = "folder_create"
    FOLDER_DELETE = "folder_delete"
    
    # Sharing
    SHARE_CREATE = "share_create"
    SHARE_ACCESS = "share_access"
    SHARE_DELETE = "share_delete"
    SHARE_EXPIRE = "share_expire"
    
    # User management
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_ACTIVATE = "user_activate"
    USER_DEACTIVATE = "user_deactivate"
    QUOTA_UPDATE = "quota_update"
    
    # System
    SYSTEM_ERROR = "system_error"
    SECURITY_VIOLATION = "security_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

async def log_audit(
    action: str,
    db: Session = None,
    user: Optional[User] = None,
    username: Optional[str] = None,
    resource_path: Optional[str] = None,
    remote_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Convenience function to log audit events"""
    if db is None:
        # If no db session provided, create one
        db_gen = get_db()
        db = next(db_gen)
        try:
            await audit_logger.log_action(
                db=db,
                action=action,
                user=user,
                username=username,
                resource_path=resource_path,
                remote_ip=remote_ip,
                user_agent=user_agent,
                details=details
            )
        finally:
            db.close()
    else:
        await audit_logger.log_action(
            db=db,
            action=action,
            user=user,
            username=username,
            resource_path=resource_path,
            remote_ip=remote_ip,
            user_agent=user_agent,
            details=details
        )