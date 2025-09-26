import os
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import AuditLog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_audit_event(
    db: Session,
    user_id: Optional[str],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Log an audit event"""
    try:
        audit_log = AuditLog(
            user_id=uuid.UUID(user_id) if user_id else None,
            action=action,
            resource_type=resource_type,
            resource_id=uuid.UUID(resource_id) if resource_id else None,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_log)
        db.commit()
        logger.info(f"Audit event logged: {action} by user {user_id}")
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")
        db.rollback()

def generate_secure_filename(original_filename: str) -> str:
    """Generate a secure filename with UUID"""
    file_extension = os.path.splitext(original_filename)[1]
    secure_name = f"{uuid.uuid4()}{file_extension}"
    return secure_name

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()

def is_image_file(mime_type: str) -> bool:
    """Check if file is an image"""
    return mime_type.startswith('image/')

def is_video_file(mime_type: str) -> bool:
    """Check if file is a video"""
    return mime_type.startswith('video/')

def is_document_file(mime_type: str) -> bool:
    """Check if file is a document"""
    document_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'text/plain',
        'text/html',
        'text/css',
        'text/javascript',
        'application/javascript',
        'application/json',
        'application/xml',
        'text/xml'
    ]
    return mime_type in document_types

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def validate_file_size(file_size: int, max_size_mb: int = 100) -> bool:
    """Validate file size against maximum allowed size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal and other issues"""
    import re
    # Remove any path components
    filename = os.path.basename(filename)
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    return filename

def get_mime_type(file_path: str) -> str:
    """Get MIME type of a file"""
    try:
        import magic
        return magic.from_file(file_path, mime=True)
    except ImportError:
        # Fallback to basic detection
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'

def ensure_directory_exists(directory_path: str):
    """Ensure a directory exists, create if it doesn't"""
    os.makedirs(directory_path, exist_ok=True)

def calculate_storage_usage(user_id: str, upload_path: str) -> int:
    """Calculate total storage usage for a user"""
    user_path = os.path.join(upload_path, str(user_id))
    total_size = 0
    
    if os.path.exists(user_path):
        for dirpath, dirnames, filenames in os.walk(user_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    # Handle cases where file might be deleted during calculation
                    continue
    
    return total_size

def cleanup_expired_tokens(db: Session):
    """Clean up expired password reset tokens"""
    from .models import PasswordResetToken
    try:
        expired_tokens = db.query(PasswordResetToken).filter(
            PasswordResetToken.expires_at < datetime.utcnow()
        )
        count = expired_tokens.count()
        expired_tokens.delete()
        db.commit()
        logger.info(f"Cleaned up {count} expired password reset tokens")
    except Exception as e:
        logger.error(f"Error cleaning up expired tokens: {e}")
        db.rollback()