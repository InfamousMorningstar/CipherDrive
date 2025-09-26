from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Response
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pathlib import Path
import os
import shutil
import mimetypes
import aiofiles
from datetime import datetime, timezone
import magic

from database import get_db
from models import User, UserRole, UserQuota, FileMetadata
from auth import get_current_user, get_normal_or_admin_user, get_client_ip, get_user_agent
from security import check_user_permissions
from utils.audit import log_audit, AuditActions
from utils.directories import initialize_user_directory

from pydantic import BaseModel

router = APIRouter(prefix="/api/files", tags=["files"])

class FileResponse(BaseModel):
    filename: str
    filepath: str
    file_size: int
    content_type: Optional[str]
    is_directory: bool
    created_at: datetime
    updated_at: datetime

class DirectoryResponse(BaseModel):
    files: List[FileResponse]
    total_size: int
    total_files: int
    current_path: str

class QuotaResponse(BaseModel):
    used_bytes: int
    quota_bytes: int
    used_percentage: float
    available_bytes: int

def get_user_base_path(user: User) -> str:
    """Get the base path for user's files"""
    if user.role == UserRole.DOWNLOAD_ONLY and user.username == "cipher":
        return "/data"  # Cipher user can access /data/movies and /data/tv
    else:
        return f"/data/users/{user.username}"

def validate_file_path(user: User, file_path: str) -> str:
    """Validate and normalize file path for user"""
    base_path = get_user_base_path(user)
    
    # Normalize the path
    if not file_path.startswith("/"):
        file_path = "/" + file_path
    
    # For cipher user, allow access to movies and tv
    if user.role == UserRole.DOWNLOAD_ONLY and user.username == "cipher":
        allowed_paths = ["/movies", "/tv"]
        if not any(file_path.startswith(path) for path in allowed_paths):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this path"
            )
        full_path = f"/data{file_path}"
    else:
        # For normal users, restrict to their home directory
        if file_path.startswith(base_path):
            full_path = file_path
        else:
            full_path = os.path.join(base_path, file_path.lstrip("/"))
    
    # Prevent path traversal attacks
    full_path = os.path.normpath(full_path)
    if not full_path.startswith(base_path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid file path"
        )
    
    return full_path

async def check_quota(user: User, db: Session, additional_bytes: int = 0) -> bool:
    """Check if user has enough quota for additional bytes"""
    if user.role == UserRole.ADMIN:
        return True  # Admins have unlimited quota
    
    quota = db.query(UserQuota).filter(UserQuota.user_id == user.id).first()
    if not quota:
        return False
    
    if quota.used_bytes + additional_bytes > quota.quota_bytes:
        return False
    
    return True

async def update_quota_usage(user: User, db: Session, bytes_delta: int):
    """Update user's quota usage"""
    if user.role == UserRole.ADMIN:
        return  # Don't track quota for admins
    
    quota = db.query(UserQuota).filter(UserQuota.user_id == user.id).first()
    if quota:
        quota.used_bytes = max(0, quota.used_bytes + bytes_delta)
        db.commit()

async def calculate_directory_size(path: str) -> int:
    """Calculate total size of directory and its contents"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
    except Exception:
        pass
    return total_size

@router.get("/quota", response_model=QuotaResponse)
async def get_user_quota(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's quota information"""
    
    if current_user.role == UserRole.ADMIN:
        # Admins don't have quota limits
        return QuotaResponse(
            used_bytes=0,
            quota_bytes=-1,  # Unlimited
            used_percentage=0.0,
            available_bytes=-1
        )
    
    quota = db.query(UserQuota).filter(UserQuota.user_id == current_user.id).first()
    if not quota:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quota not found"
        )
    
    used_percentage = (quota.used_bytes / quota.quota_bytes * 100) if quota.quota_bytes > 0 else 0
    available_bytes = max(0, quota.quota_bytes - quota.used_bytes)
    
    return QuotaResponse(
        used_bytes=quota.used_bytes,
        quota_bytes=quota.quota_bytes,
        used_percentage=used_percentage,
        available_bytes=available_bytes
    )

@router.get("/browse", response_model=DirectoryResponse)
async def browse_directory(
    path: str = "/",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Browse directory contents"""
    
    try:
        full_path = validate_file_path(current_user, path)
    except HTTPException:
        raise
    
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Directory not found"
        )
    
    if not os.path.isdir(full_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path is not a directory"
        )
    
    try:
        files = []
        total_size = 0
        total_files = 0
        
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            
            try:
                stat_info = os.stat(item_path)
                is_directory = os.path.isdir(item_path)
                
                if is_directory:
                    file_size = 0  # Don't calculate directory size for performance
                else:
                    file_size = stat_info.st_size
                    total_size += file_size
                    total_files += 1
                
                # Get content type
                content_type = None
                if not is_directory:
                    content_type, _ = mimetypes.guess_type(item)
                    if not content_type:
                        try:
                            content_type = magic.from_file(item_path, mime=True)
                        except:
                            content_type = "application/octet-stream"
                
                files.append(FileResponse(
                    filename=item,
                    filepath=os.path.join(path, item),
                    file_size=file_size,
                    content_type=content_type,
                    is_directory=is_directory,
                    created_at=datetime.fromtimestamp(stat_info.st_ctime, tz=timezone.utc),
                    updated_at=datetime.fromtimestamp(stat_info.st_mtime, tz=timezone.utc)
                ))
                
            except (OSError, PermissionError):
                continue  # Skip files we can't access
        
        return DirectoryResponse(
            files=sorted(files, key=lambda x: (not x.is_directory, x.filename.lower())),
            total_size=total_size,
            total_files=total_files,
            current_path=path
        )
        
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to browse directory: {str(e)}"
        )

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: str = "/",
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_normal_or_admin_user)
):
    """Upload a file"""
    
    # Cipher user cannot upload files
    if current_user.role == UserRole.DOWNLOAD_ONLY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Download-only users cannot upload files"
        )
    
    try:
        full_path = validate_file_path(current_user, path)
    except HTTPException:
        raise
    
    # Ensure upload directory exists
    os.makedirs(full_path, exist_ok=True)
    
    # Full file path
    file_path = os.path.join(full_path, file.filename)
    
    # Check if file already exists
    if os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File already exists"
        )
    
    # Check quota before upload
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if not await check_quota(current_user, db, file_size):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Quota exceeded"
        )
    
    try:
        # Write file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Update quota
        await update_quota_usage(current_user, db, file_size)
        
        # Store file metadata
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        
        file_metadata = FileMetadata(
            filename=file.filename,
            filepath=file_path,
            file_size=file_size,
            content_type=content_type,
            owner_id=current_user.id,
            is_directory=False
        )
        
        db.add(file_metadata)
        db.commit()
        
        # Audit log
        await log_audit(
            action=AuditActions.FILE_UPLOAD,
            db=db,
            user=current_user,
            resource_path=file_path,
            remote_ip=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={"file_size": file_size, "content_type": content_type}
        )
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "size": file_size,
            "path": file_path
        }
        
    except Exception as e:
        # Clean up file if it was created
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.get("/download")
async def download_file(
    path: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download a file"""
    
    try:
        full_path = validate_file_path(current_user, path)
    except HTTPException:
        raise
    
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    if os.path.isdir(full_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot download directory"
        )
    
    # Audit log
    file_size = os.path.getsize(full_path)
    await log_audit(
        action=AuditActions.FILE_DOWNLOAD,
        db=db,
        user=current_user,
        resource_path=full_path,
        remote_ip=get_client_ip(request),
        user_agent=get_user_agent(request),
        details={"file_size": file_size}
    )
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(full_path)
    if not content_type:
        try:
            content_type = magic.from_file(full_path, mime=True)
        except:
            content_type = "application/octet-stream"
    
    filename = os.path.basename(full_path)
    
    return FileResponse(
        path=full_path,
        filename=filename,
        media_type=content_type
    )

@router.delete("/delete")
async def delete_file(
    path: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_normal_or_admin_user)
):
    """Delete a file or directory"""
    
    # Cipher user cannot delete files
    if current_user.role == UserRole.DOWNLOAD_ONLY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Download-only users cannot delete files"
        )
    
    try:
        full_path = validate_file_path(current_user, path)
    except HTTPException:
        raise
    
    if not os.path.exists(full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File or directory not found"
        )
    
    # Calculate size before deletion for quota update
    if os.path.isdir(full_path):
        total_size = await calculate_directory_size(full_path)
        is_directory = True
    else:
        total_size = os.path.getsize(full_path)
        is_directory = False
    
    try:
        # Delete file or directory
        if is_directory:
            shutil.rmtree(full_path)
            action = AuditActions.FOLDER_DELETE
        else:
            os.remove(full_path)
            action = AuditActions.FILE_DELETE
        
        # Update quota (subtract the deleted bytes)
        await update_quota_usage(current_user, db, -total_size)
        
        # Remove from file metadata
        db.query(FileMetadata).filter(
            FileMetadata.filepath.like(f"{full_path}%"),
            FileMetadata.owner_id == current_user.id
        ).delete(synchronize_session=False)
        db.commit()
        
        # Audit log
        await log_audit(
            action=action,
            db=db,
            user=current_user,
            resource_path=full_path,
            remote_ip=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={"size_freed": total_size, "is_directory": is_directory}
        )
        
        return {
            "message": "File deleted successfully",
            "path": path,
            "size_freed": total_size
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

@router.post("/create-folder")
async def create_folder(
    path: str,
    folder_name: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_normal_or_admin_user)
):
    """Create a new folder"""
    
    # Cipher user cannot create folders
    if current_user.role == UserRole.DOWNLOAD_ONLY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Download-only users cannot create folders"
        )
    
    try:
        full_path = validate_file_path(current_user, path)
    except HTTPException:
        raise
    
    folder_path = os.path.join(full_path, folder_name)
    
    if os.path.exists(folder_path):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Folder already exists"
        )
    
    try:
        os.makedirs(folder_path)
        
        # Store folder metadata
        folder_metadata = FileMetadata(
            filename=folder_name,
            filepath=folder_path,
            file_size=0,
            content_type="inode/directory",
            owner_id=current_user.id,
            is_directory=True
        )
        
        db.add(folder_metadata)
        db.commit()
        
        # Audit log
        await log_audit(
            action=AuditActions.FOLDER_CREATE,
            db=db,
            user=current_user,
            resource_path=folder_path,
            remote_ip=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={"folder_name": folder_name}
        )
        
        return {
            "message": "Folder created successfully",
            "folder_name": folder_name,
            "path": folder_path
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create folder: {str(e)}"
        )