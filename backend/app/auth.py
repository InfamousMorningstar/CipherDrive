import os
import secrets
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Optional, Dict, Any

import jwt
import pyotp
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import get_database
from .models import User, PasswordResetToken, AuditLog
from .utils import log_audit_event

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET", "your-refresh-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer scheme
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        secret_key = SECRET_KEY if token_type == "access" else REFRESH_SECRET_KEY
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> User:
    """Get current authenticated user"""
    payload = verify_token(credentials.credentials)
    user_id: str = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges"
        )
    return current_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user by email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def generate_2fa_secret() -> str:
    """Generate a new 2FA secret"""
    return pyotp.random_base32()

def verify_2fa_token(secret: str, token: str) -> bool:
    """Verify 2FA token"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)  # Allow 1 step tolerance

def send_2fa_email(email: str, code: str) -> bool:
    """Send 2FA code via email"""
    try:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        from_email = os.getenv("FROM_EMAIL", smtp_user)
        
        if not all([smtp_host, smtp_user, smtp_pass]):
            return False
        
        msg = MimeMultipart()
        msg['From'] = from_email
        msg['To'] = email
        msg['Subject'] = "Your Login Code - Dropbox Lite"
        
        body = f"""
        <html>
        <body>
            <h2>Your Login Code</h2>
            <p>Use this code to complete your login:</p>
            <h3 style="color: #3b82f6; font-family: monospace;">{code}</h3>
            <p>This code will expire in 5 minutes.</p>
            <p><small>If you didn't request this, please ignore this email.</small></p>
        </body>
        </html>
        """
        
        msg.attach(MimeText(body, 'html'))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        if os.getenv("SMTP_TLS", "true").lower() == "true":
            server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(from_email, email, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def create_password_reset_token(db: Session, user: User) -> str:
    """Create a password reset token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    
    # Deactivate any existing tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False
    ).update({"used": True})
    
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    db.add(reset_token)
    db.commit()
    
    return token

def verify_password_reset_token(db: Session, token: str) -> Optional[User]:
    """Verify password reset token and return associated user"""
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_token:
        return None
    
    return reset_token.user

def send_password_reset_email(email: str, token: str) -> bool:
    """Send password reset email"""
    try:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        from_email = os.getenv("FROM_EMAIL", smtp_user)
        
        if not all([smtp_host, smtp_user, smtp_pass]):
            return False
        
        reset_url = f"http://localhost:3000/reset-password?token={token}"
        
        msg = MimeMultipart()
        msg['From'] = from_email
        msg['To'] = email
        msg['Subject'] = "Password Reset - Dropbox Lite"
        
        body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>You requested a password reset for your Dropbox Lite account.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_url}" style="color: #3b82f6;">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p><small>If you didn't request this, please ignore this email.</small></p>
        </body>
        </html>
        """
        
        msg.attach(MimeText(body, 'html'))
        
        server = smtplib.SMTP(smtp_host, smtp_port)
        if os.getenv("SMTP_TLS", "true").lower() == "true":
            server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(from_email, email, msg.as_string())
        server.quit()
        
        return True
    except Exception as e:
        print(f"Password reset email failed: {e}")
        return False

def validate_password_strength(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return all([has_upper, has_lower, has_digit, has_special])

async def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"