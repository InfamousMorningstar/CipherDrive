from sqlalchemy import Column, String, Boolean, Integer, BigInteger, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    quota_gb = Column(Integer, default=5)
    used_storage_bytes = Column(BigInteger, default=0)
    must_change_password = Column(Boolean, default=True)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32))
    last_login = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    files = relationship("File", back_populates="owner", cascade="all, delete-orphan")
    shared_links = relationship("SharedLink", back_populates="created_by_user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")

class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100))
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_folder_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), index=True)
    is_folder = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="files")
    parent_folder = relationship("File", remote_side=[id], back_populates="children")
    children = relationship("File", back_populates="parent_folder", cascade="all, delete-orphan")
    shared_links = relationship("SharedLink", back_populates="file", cascade="all, delete-orphan")
    thumbnails = relationship("Thumbnail", back_populates="file", cascade="all, delete-orphan")

class SharedLink(Base):
    __tablename__ = "shared_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True)
    share_token = Column(String(255), unique=True, nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime)
    max_downloads = Column(Integer)
    current_downloads = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    password_hash = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    file = relationship("File", back_populates="shared_links")
    created_by_user = relationship("User", back_populates="shared_links")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSON)
    ip_address = Column(INET)
    user_agent = Column(Text)
    created_at = Column(DateTime, server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="password_reset_tokens")

class Thumbnail(Base):
    __tablename__ = "thumbnails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True)
    size = Column(Integer, nullable=False)
    thumbnail_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    file = relationship("File", back_populates="thumbnails")