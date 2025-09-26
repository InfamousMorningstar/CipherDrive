import os
import asyncio
import aiosmtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@cipherdrive.ahmxd.net")
FROM_NAME = os.getenv("FROM_NAME", "CipherDrive")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://cipherdrive.ahmxd.net")

async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None
) -> bool:
    """Send an email using SMTP"""
    
    if not SMTP_USER or not SMTP_PASS:
        logger.warning("SMTP credentials not configured, skipping email send")
        return False
    
    try:
        # Create message
        message = MimeMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        message["To"] = to_email
        
        # Add text and HTML parts
        if text_body:
            text_part = MimeText(text_body, "plain")
            message.attach(text_part)
        
        html_part = MimeText(html_body, "html")
        message.attach(html_part)
        
        # Send email
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASS,
            use_tls=SMTP_USE_TLS,
        )
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

async def send_welcome_email(email: str, username: str, temp_password: str) -> bool:
    """Send welcome email to new user"""
    
    subject = "Welcome to CipherDrive"
    
    html_body = f"""
    <html>
        <body>
            <h2>Welcome to CipherDrive!</h2>
            <p>Hello {username},</p>
            <p>Your account has been created successfully. Here are your login details:</p>
            
            <div style="background-color: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 5px;">
                <strong>Username:</strong> {username}<br>
                <strong>Temporary Password:</strong> {temp_password}
            </div>
            
            <p><strong>Important:</strong> You will be required to change your password upon first login for security purposes.</p>
            
            <p>You can access CipherDrive at: <a href="{FRONTEND_URL}">{FRONTEND_URL}</a></p>
            
            <p>If you have any questions, please contact your administrator.</p>
            
            <p>Best regards,<br>
            The CipherDrive Team</p>
        </body>
    </html>
    """
    
    text_body = f"""
    Welcome to CipherDrive!
    
    Hello {username},
    
    Your account has been created successfully. Here are your login details:
    
    Username: {username}
    Temporary Password: {temp_password}
    
    Important: You will be required to change your password upon first login for security purposes.
    
    You can access CipherDrive at: {FRONTEND_URL}
    
    If you have any questions, please contact your administrator.
    
    Best regards,
    The CipherDrive Team
    """
    
    return await send_email(email, subject, html_body, text_body)

async def send_password_reset_email(email: str, username: str, reset_token: str) -> bool:
    """Send password reset email"""
    
    reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    
    subject = "CipherDrive Password Reset"
    
    html_body = f"""
    <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hello {username},</p>
            <p>We received a request to reset your CipherDrive password.</p>
            
            <p>To reset your password, click the link below:</p>
            <p><a href="{reset_url}" style="background-color: #007bff; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
            
            <p>Or copy and paste this URL into your browser:</p>
            <p><code>{reset_url}</code></p>
            
            <p>This link will expire in 1 hour for security purposes.</p>
            
            <p>If you did not request a password reset, please ignore this email and your password will remain unchanged.</p>
            
            <p>Best regards,<br>
            The CipherDrive Team</p>
        </body>
    </html>
    """
    
    text_body = f"""
    Password Reset Request
    
    Hello {username},
    
    We received a request to reset your CipherDrive password.
    
    To reset your password, visit this URL:
    {reset_url}
    
    This link will expire in 1 hour for security purposes.
    
    If you did not request a password reset, please ignore this email and your password will remain unchanged.
    
    Best regards,
    The CipherDrive Team
    """
    
    return await send_email(email, subject, html_body, text_body)

async def send_quota_warning_email(email: str, username: str, used_percent: float) -> bool:
    """Send quota warning email"""
    
    subject = "CipherDrive Storage Quota Warning"
    
    html_body = f"""
    <html>
        <body>
            <h2>Storage Quota Warning</h2>
            <p>Hello {username},</p>
            <p>Your CipherDrive storage is {used_percent:.1f}% full.</p>
            
            <div style="background-color: #fff3cd; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #ffc107;">
                <strong>Warning:</strong> You are approaching your storage limit. Please consider deleting unnecessary files or contact your administrator to increase your quota.
            </div>
            
            <p>You can manage your files at: <a href="{FRONTEND_URL}">{FRONTEND_URL}</a></p>
            
            <p>Best regards,<br>
            The CipherDrive Team</p>
        </body>
    </html>
    """
    
    text_body = f"""
    Storage Quota Warning
    
    Hello {username},
    
    Your CipherDrive storage is {used_percent:.1f}% full.
    
    Warning: You are approaching your storage limit. Please consider deleting unnecessary files or contact your administrator to increase your quota.
    
    You can manage your files at: {FRONTEND_URL}
    
    Best regards,
    The CipherDrive Team
    """
    
    return await send_email(email, subject, html_body, text_body)

async def send_account_locked_email(email: str, username: str, reason: str) -> bool:
    """Send account locked notification email"""
    
    subject = "CipherDrive Account Security Alert"
    
    html_body = f"""
    <html>
        <body>
            <h2>Account Security Alert</h2>
            <p>Hello {username},</p>
            <p>Your CipherDrive account has been temporarily locked due to: {reason}</p>
            
            <div style="background-color: #f8d7da; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #dc3545;">
                <strong>Security Notice:</strong> If this was not you, please contact your administrator immediately.
            </div>
            
            <p>Please contact your administrator to unlock your account.</p>
            
            <p>Best regards,<br>
            The CipherDrive Team</p>
        </body>
    </html>
    """
    
    text_body = f"""
    Account Security Alert
    
    Hello {username},
    
    Your CipherDrive account has been temporarily locked due to: {reason}
    
    Security Notice: If this was not you, please contact your administrator immediately.
    
    Please contact your administrator to unlock your account.
    
    Best regards,
    The CipherDrive Team
    """
    
    return await send_email(email, subject, html_body, text_body)