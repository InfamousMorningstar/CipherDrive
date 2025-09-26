from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, BigInteger, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime, timezone

Base = declarative_base()

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    DOWNLOAD_ONLY = "download_only"

class ShareStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    force_password_reset = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    quota = relationship("UserQuota", back_populates="user", uselist=False)
    shares = relationship("Share", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class UserQuota(Base):
    __tablename__ = "user_quotas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    quota_bytes = Column(BigInteger, default=5368709120, nullable=False)  # 5GB default
    used_bytes = Column(BigInteger, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="quota")

class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(1024), nullable=False, index=True)
    file_size = Column(BigInteger, nullable=False)
    content_type = Column(String(100), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_directory = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    owner = relationship("User")

class Share(Base):
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, index=True)
    share_token = Column(String(64), unique=True, index=True, nullable=False)
    file_path = Column(String(1024), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    max_downloads = Column(Integer, nullable=True)
    download_count = Column(Integer, default=0, nullable=False)
    status = Column(Enum(ShareStatus), default=ShareStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="shares")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(50), nullable=True)  # Store username for deleted users
    action = Column(String(50), nullable=False, index=True)
    resource_path = Column(String(1024), nullable=True)
    remote_ip = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    details = Column(Text, nullable=True)  # JSON string for additional details
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")