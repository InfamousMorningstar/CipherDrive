import os
import shutil
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

import aiofiles
from fastapi import HTTPException, status, UploadFile, Depends
from PIL import Image, ImageOps
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .database import get_database
from .models import User, File, SharedLink, Thumbnail
from .auth import get_current_user
from .utils import (
    log_audit_event, generate_secure_filename, get_file_extension,
    is_image_file, is_video_file, format_file_size, validate_file_size,
    sanitize_filename, get_mime_type, ensure_directory_exists
)

class FileService:
    """Service class for file management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.upload_path = os.getenv("UPLOAD_PATH", "/data")
        self.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
        self.thumbnail_sizes = [int(s) for s in os.getenv("THUMBNAIL_SIZES", "150,300,600").split(",")]
    
    async def create_folder(self, name: str, parent_folder_id: Optional[str], user: User) -> File:
        """Create a new folder"""
        # Sanitize folder name
        sanitized_name = sanitize_filename(name)
        if not sanitized_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid folder name"
            )
        
        # Check if folder already exists in parent
        existing_folder = self.db.query(File).filter(
            and_(
                File.owner_id == user.id,
                File.parent_folder_id == UUID(parent_folder_id) if parent_folder_id else None,
                File.filename == sanitized_name,
                File.is_folder == True
            )
        ).first()
        
        if existing_folder:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Folder with this name already exists"
            )
        
        # Create physical directory
        user_path = os.path.join(self.upload_path, str(user.id))
        if parent_folder_id:
            parent_folder = await self.get_file_by_id(parent_folder_id, user)
            if not parent_folder or not parent_folder.is_folder:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent folder not found"
                )
            folder_path = os.path.join(user_path, parent_folder.file_path, sanitized_name)
        else:
            folder_path = os.path.join(user_path, sanitized_name)
        
        ensure_directory_exists(folder_path)
        
        # Create database record
        folder = File(
            filename=sanitized_name,
            original_filename=sanitized_name,
            file_path=os.path.relpath(folder_path, user_path),
            file_size=0,
            owner_id=user.id,
            parent_folder_id=UUID(parent_folder_id) if parent_folder_id else None,
            is_folder=True
        )
        
        self.db.add(folder)
        self.db.commit()
        self.db.refresh(folder)
        
        # Log audit event
        log_audit_event(
            self.db,
            str(user.id),
            "folder_created",
            "folder",
            str(folder.id),
            {"folder_name": sanitized_name}
        )
        
        return folder
    
    async def upload_file(
        self, 
        file: UploadFile, 
        parent_folder_id: Optional[str], 
        user: User
    ) -> File:
        """Upload a file"""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided"
            )
        
        # Validate file size
        file_content = await file.read()
        file_size = len(file_content)
        
        if not validate_file_size(file_size, self.max_file_size_mb):
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {self.max_file_size_mb}MB"
            )
        
        # Check user quota
        quota_bytes = user.quota_gb * 1024 * 1024 * 1024
        if user.used_storage_bytes + file_size > quota_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Upload would exceed your storage quota"
            )
        
        # Generate secure filename
        original_filename = sanitize_filename(file.filename)
        secure_filename = generate_secure_filename(original_filename)
        
        # Determine upload path
        user_path = os.path.join(self.upload_path, str(user.id))
        if parent_folder_id:
            parent_folder = await self.get_file_by_id(parent_folder_id, user)
            if not parent_folder or not parent_folder.is_folder:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent folder not found"
                )
            upload_dir = os.path.join(user_path, parent_folder.file_path)
        else:
            upload_dir = user_path
        
        ensure_directory_exists(upload_dir)
        file_path = os.path.join(upload_dir, secure_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Get MIME type
        mime_type = get_mime_type(file_path)
        
        # Create database record
        file_record = File(
            filename=secure_filename,
            original_filename=original_filename,
            file_path=os.path.relpath(file_path, user_path),
            file_size=file_size,
            mime_type=mime_type,
            owner_id=user.id,
            parent_folder_id=UUID(parent_folder_id) if parent_folder_id else None,
            is_folder=False
        )
        
        self.db.add(file_record)
        
        # Update user storage usage
        user.used_storage_bytes += file_size
        
        self.db.commit()
        self.db.refresh(file_record)
        
        # Generate thumbnails for images
        if is_image_file(mime_type) and os.getenv("ENABLE_THUMBNAILS", "true").lower() == "true":
            await self.generate_thumbnails(file_record, file_path)
        
        # Log audit event
        log_audit_event(
            self.db,
            str(user.id),
            "file_uploaded",
            "file",
            str(file_record.id),
            {
                "original_filename": original_filename,
                "file_size": file_size,
                "mime_type": mime_type
            }
        )
        
        return file_record
    
    async def get_file_by_id(self, file_id: str, user: User) -> Optional[File]:
        """Get file by ID (user must own it)"""
        return self.db.query(File).filter(
            and_(File.id == UUID(file_id), File.owner_id == user.id)
        ).first()
    
    async def get_files_in_folder(
        self, 
        parent_folder_id: Optional[str], 
        user: User,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """Get files in a specific folder"""
        query = self.db.query(File).filter(
            and_(
                File.owner_id == user.id,
                File.parent_folder_id == UUID(parent_folder_id) if parent_folder_id else None
            )
        ).order_by(File.is_folder.desc(), File.filename)
        
        return query.offset(skip).limit(limit).all()
    
    async def delete_file(self, file_id: str, user: User) -> bool:
        """Delete a file or folder"""
        file_record = await self.get_file_by_id(file_id, user)
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        user_path = os.path.join(self.upload_path, str(user.id))
        full_path = os.path.join(user_path, file_record.file_path)
        
        # Calculate storage to be freed
        storage_freed = 0
        
        if file_record.is_folder:
            # Delete folder and all contents
            if os.path.exists(full_path):
                # Calculate total size of folder contents
                for root, dirs, files in os.walk(full_path):
                    for file in files:
                        try:
                            storage_freed += os.path.getsize(os.path.join(root, file))
                        except OSError:
                            continue
                shutil.rmtree(full_path)
            
            # Delete all child records from database
            await self.delete_folder_contents(file_record.id, user)
        else:
            # Delete single file
            if os.path.exists(full_path):
                storage_freed = os.path.getsize(full_path)
                os.remove(full_path)
            
            # Delete thumbnails
            thumbnails = self.db.query(Thumbnail).filter(Thumbnail.file_id == file_record.id).all()
            for thumbnail in thumbnails:
                thumbnail_path = os.path.join(self.upload_path, "thumbnails", thumbnail.thumbnail_path)
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                self.db.delete(thumbnail)
        
        # Update user storage usage
        user.used_storage_bytes = max(0, user.used_storage_bytes - storage_freed)
        
        # Delete file record
        self.db.delete(file_record)
        self.db.commit()
        
        # Log audit event
        log_audit_event(
            self.db,
            str(user.id),
            "file_deleted",
            "file" if not file_record.is_folder else "folder",
            str(file_record.id),
            {
                "filename": file_record.original_filename,
                "storage_freed": storage_freed
            }
        )
        
        return True
    
    async def delete_folder_contents(self, folder_id: UUID, user: User):
        """Recursively delete folder contents from database"""
        child_files = self.db.query(File).filter(
            and_(File.parent_folder_id == folder_id, File.owner_id == user.id)
        ).all()
        
        for child in child_files:
            if child.is_folder:
                await self.delete_folder_contents(child.id, user)
            
            # Delete thumbnails for files
            if not child.is_folder:
                thumbnails = self.db.query(Thumbnail).filter(Thumbnail.file_id == child.id).all()
                for thumbnail in thumbnails:
                    self.db.delete(thumbnail)
            
            self.db.delete(child)
    
    async def download_file(self, file_id: str, user: User) -> tuple[str, File]:
        """Get file path for download"""
        file_record = await self.get_file_by_id(file_id, user)
        if not file_record or file_record.is_folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        user_path = os.path.join(self.upload_path, str(user.id))
        file_path = os.path.join(user_path, file_record.file_path)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )
        
        # Log audit event
        log_audit_event(
            self.db,
            str(user.id),
            "file_downloaded",
            "file",
            str(file_record.id),
            {"filename": file_record.original_filename}
        )
        
        return file_path, file_record
    
    async def create_share_link(
        self,
        file_id: str,
        user: User,
        expires_at: Optional[datetime] = None,
        max_downloads: Optional[int] = None,
        password: Optional[str] = None
    ) -> SharedLink:
        """Create a shareable link for a file"""
        file_record = await self.get_file_by_id(file_id, user)
        if not file_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Generate secure share token
        share_token = secrets.token_urlsafe(32)
        
        # Hash password if provided
        password_hash = None
        if password:
            from .auth import get_password_hash
            password_hash = get_password_hash(password)
        
        shared_link = SharedLink(
            file_id=file_record.id,
            share_token=share_token,
            created_by=user.id,
            expires_at=expires_at,
            max_downloads=max_downloads,
            password_hash=password_hash
        )
        
        self.db.add(shared_link)
        self.db.commit()
        self.db.refresh(shared_link)
        
        # Log audit event
        log_audit_event(
            self.db,
            str(user.id),
            "share_link_created",
            "shared_link",
            str(shared_link.id),
            {
                "file_id": str(file_record.id),
                "filename": file_record.original_filename,
                "expires_at": expires_at.isoformat() if expires_at else None,
                "max_downloads": max_downloads,
                "password_protected": bool(password)
            }
        )
        
        return shared_link
    
    async def get_shared_file(self, share_token: str, password: Optional[str] = None) -> tuple[str, File]:
        """Access a shared file by token"""
        shared_link = self.db.query(SharedLink).filter(
            SharedLink.share_token == share_token,
            SharedLink.is_active == True
        ).first()
        
        if not shared_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shared link not found"
            )
        
        # Check if link has expired
        if shared_link.expires_at and shared_link.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Shared link has expired"
            )
        
        # Check download limit
        if shared_link.max_downloads and shared_link.current_downloads >= shared_link.max_downloads:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Download limit reached"
            )
        
        # Check password
        if shared_link.password_hash:
            if not password:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Password required"
                )
            
            from .auth import verify_password
            if not verify_password(password, shared_link.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid password"
                )
        
        # Get file
        file_record = shared_link.file
        if not file_record or file_record.is_folder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Build file path
        user_path = os.path.join(self.upload_path, str(file_record.owner_id))
        file_path = os.path.join(user_path, file_record.file_path)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )
        
        # Increment download count
        shared_link.current_downloads += 1
        self.db.commit()
        
        # Log audit event
        log_audit_event(
            self.db,
            None,  # Anonymous access
            "shared_file_downloaded",
            "shared_link",
            str(shared_link.id),
            {
                "file_id": str(file_record.id),
                "filename": file_record.original_filename,
                "download_count": shared_link.current_downloads
            }
        )
        
        return file_path, file_record
    
    async def generate_thumbnails(self, file_record: File, file_path: str):
        """Generate thumbnails for image files"""
        try:
            thumbnail_dir = os.path.join(self.upload_path, "thumbnails", str(file_record.owner_id))
            ensure_directory_exists(thumbnail_dir)
            
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                for size in self.thumbnail_sizes:
                    # Create thumbnail
                    thumbnail = img.copy()
                    thumbnail.thumbnail((size, size), Image.Resampling.LANCZOS)
                    
                    # Save thumbnail
                    thumbnail_filename = f"{file_record.filename}_{size}.jpg"
                    thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
                    thumbnail.save(thumbnail_path, "JPEG", quality=85, optimize=True)
                    
                    # Create database record
                    thumbnail_record = Thumbnail(
                        file_id=file_record.id,
                        size=size,
                        thumbnail_path=os.path.join(str(file_record.owner_id), thumbnail_filename)
                    )
                    self.db.add(thumbnail_record)
            
            self.db.commit()
            
        except Exception as e:
            print(f"Thumbnail generation failed: {e}")
    
    def get_user_shared_links(self, user: User) -> List[SharedLink]:
        """Get all shared links created by user"""
        return self.db.query(SharedLink).filter(
            SharedLink.created_by == user.id
        ).order_by(SharedLink.created_at.desc()).all()
    
    async def delete_shared_link(self, link_id: str, user: User) -> bool:
        """Delete a shared link"""
        shared_link = self.db.query(SharedLink).filter(
            and_(SharedLink.id == UUID(link_id), SharedLink.created_by == user.id)
        ).first()
        
        if not shared_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shared link not found"
            )
        
        self.db.delete(shared_link)
        self.db.commit()
        
        # Log audit event
        log_audit_event(
            self.db,
            str(user.id),
            "share_link_deleted",
            "shared_link",
            str(shared_link.id)
        )
        
        return True

# Dependency function
def get_file_service(db: Session = Depends(get_database)) -> FileService:
    """Get file service instance"""
    return FileService(db)