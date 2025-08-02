"""Security utilities for authentication."""

import base64
import io
import secrets
from datetime import datetime, timedelta
from typing import List, Optional, Tuple, cast

import pyotp
import qrcode
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError

# Initialize password hasher with secure settings
ph = PasswordHasher(
    time_cost=2,
    memory_cost=102400,  # 100 MB
    parallelism=8,
    hash_len=32,
    salt_len=16,
)


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except (VerifyMismatchError, VerificationError, InvalidHash):
        return False


def needs_rehash(hashed_password: str) -> bool:
    """Check if password hash needs to be updated."""
    try:
        return ph.check_needs_rehash(hashed_password)
    except (InvalidHash, ValueError):
        return True


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(48)


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)


def generate_totp_secret() -> str:
    """Generate a TOTP secret."""
    return str(pyotp.random_base32())


def generate_totp_uri(
    secret: str,
    email: str,
    issuer: str = "OpenPerformance"
) -> str:
    """Generate TOTP URI for QR code."""
    totp = pyotp.TOTP(secret)
    return str(totp.provisioning_uri(
        name=email,
        issuer_name=issuer
    ))


def generate_qr_code(uri: str) -> str:
    """Generate QR code as base64 string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()


def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    """Verify a TOTP code."""
    totp = pyotp.TOTP(secret)
    return bool(totp.verify(code, valid_window=window))


def generate_backup_codes(count: int = 10) -> List[str]:
    """Generate backup codes for 2FA."""
    codes = []
    for _ in range(count):
        # Generate 8-character alphanumeric codes
        code = "".join(secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(8))
        # Format as XXXX-XXXX for readability
        formatted_code = f"{code[:4]}-{code[4:]}"
        codes.append(formatted_code)
    return codes


def hash_backup_code(code: str) -> str:
    """Hash a backup code for storage."""
    # Remove formatting
    clean_code = code.replace("-", "")
    # Use a simpler hash for backup codes
    return ph.hash(clean_code)


def verify_backup_code(code: str, hashed_code: str) -> bool:
    """Verify a backup code."""
    clean_code = code.replace("-", "")
    try:
        ph.verify(hashed_code, clean_code)
        return True
    except (VerifyMismatchError, VerificationError, InvalidHash):
        return False


def is_strong_password(password: str) -> Tuple[bool, List[str]]:
    """Check if password meets strength requirements."""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if len(password) > 100:
        errors.append("Password must not exceed 100 characters")
    
    if not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one digit")
    
    if not any(char.isupper() for char in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(char.islower() for char in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
        errors.append("Password must contain at least one special character")
    
    # Check for common patterns
    common_patterns = ["password", "12345", "qwerty", "abc123", "admin"]
    lower_password = password.lower()
    for pattern in common_patterns:
        if pattern in lower_password:
            errors.append(f"Password contains common pattern: {pattern}")
    
    return len(errors) == 0, errors


def calculate_account_lockout_time(failed_attempts: int) -> Optional[datetime]:
    """Calculate account lockout time based on failed attempts."""
    if failed_attempts < 3:
        return None
    elif failed_attempts < 5:
        # Lock for 5 minutes
        return datetime.utcnow() + timedelta(minutes=5)
    elif failed_attempts < 10:
        # Lock for 30 minutes
        return datetime.utcnow() + timedelta(minutes=30)
    else:
        # Lock for 24 hours
        return datetime.utcnow() + timedelta(hours=24)


def sanitize_user_input(input_string: str, max_length: int = 255) -> str:
    """Sanitize user input to prevent injection attacks."""
    # Remove null bytes
    sanitized = input_string.replace("\x00", "")
    
    # Trim to max length
    sanitized = sanitized[:max_length]
    
    # Remove control characters except newlines and tabs
    allowed_chars = ["\n", "\t", "\r"]
    sanitized = "".join(
        char for char in sanitized
        if char in allowed_chars or not (0 <= ord(char) < 32 or ord(char) == 127)
    )
    
    return sanitized.strip()


def constant_time_compare(val1: str, val2: str) -> bool:
    """Compare two strings in constant time to prevent timing attacks."""
    if len(val1) != len(val2):
        return False
    
    result = 0
    for x, y in zip(val1, val2):
        result |= ord(x) ^ ord(y)
    
    return result == 0