import os
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Union
from passlib.context import CryptContext
from passlib.hash import bcrypt
from jose import JWTError
from models import User, UserRole

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None

def create_password_reset_token(user_id: int) -> str:
    """Create password reset token"""
    expire = datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour expiry
    payload = {
        "user_id": user_id,
        "type": "password_reset",
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_password_reset_token(token: str) -> Optional[int]:
    """Verify password reset token and return user ID"""
    payload = verify_token(token, "password_reset")
    if payload:
        return payload.get("user_id")
    return None

def check_user_permissions(user: User, required_role: UserRole = None, resource_path: str = None) -> bool:
    """Check if user has required permissions"""
    if not user.is_active:
        return False
    
    # Admin can do everything
    if user.role == UserRole.ADMIN:
        return True
    
    # Check role-specific permissions
    if required_role and user.role != required_role:
        return False
    
    # Check path-specific permissions for download-only users
    if user.role == UserRole.DOWNLOAD_ONLY:
        if user.username != "cipher":
            return False  # Only cipher user can have download-only role
        
        # Cipher user can only access /movies and /tv
        if resource_path:
            allowed_paths = ["/movies", "/tv", "/data/movies", "/data/tv"]
            if not any(resource_path.startswith(path) for path in allowed_paths):
                return False
    
    # Normal users can only access their home directory
    elif user.role == UserRole.USER and resource_path:
        user_home = f"/data/users/{user.username}"
        if not resource_path.startswith(user_home):
            return False
    
    return True

def generate_secure_token(length: int = 32) -> str:
    """Generate secure random token"""
    import secrets
    return secrets.token_urlsafe(length)