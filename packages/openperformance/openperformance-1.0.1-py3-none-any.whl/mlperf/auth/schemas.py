"""Pydantic schemas for authentication and authorization."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, ValidationInfo

from mlperf.auth.models import UserRole


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100, pattern="^[a-zA-Z0-9_-]+$")
    full_name: Optional[str] = Field(None, max_length=255)
    role: UserRole = UserRole.USER
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str
    
    @field_validator("confirm_password")
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        """Validate that passwords match."""
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match")
        return v
    
    @field_validator("password")
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100, pattern="^[a-zA-Z0-9_-]+$")
    full_name: Optional[str] = Field(None, max_length=255)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class UserResponse(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class UserInDB(UserResponse):
    """Schema for user in database."""

    hashed_password: str
    totp_secret: Optional[str] = None
    api_key: Optional[str] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None


class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int  # Seconds until expiration


class TokenData(BaseModel):
    """Token data schema."""

    sub: str  # Subject (user ID)
    email: Optional[str] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    scopes: List[str] = []
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None
    jti: Optional[str] = None  # JWT ID for token revocation


class LoginRequest(BaseModel):
    """Login request schema."""

    username: str  # Can be username or email
    password: str
    totp_code: Optional[str] = None  # For 2FA


class PasswordChange(BaseModel):
    """Password change request schema."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str
    
    @field_validator("confirm_password")
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        """Validate that passwords match."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class PasswordReset(BaseModel):
    """Password reset request schema."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str
    
    @field_validator("confirm_password")
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        """Validate that passwords match."""
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


class ApiKeyCreate(BaseModel):
    """API key creation schema."""

    name: str = Field(..., min_length=1, max_length=255)
    scopes: List[str] = []
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)
    rate_limit: int = Field(1000, ge=1, le=10000)  # Requests per hour


class ApiKeyResponse(BaseModel):
    """API key response schema."""

    model_config = ConfigDict(from_attributes=True)
    
    id: int
    key: str  # Only shown once during creation
    name: str
    scopes: List[str]
    expires_at: Optional[datetime]
    created_at: datetime
    rate_limit: int


class AuditLogEntry(BaseModel):
    """Audit log entry schema."""

    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: Optional[int]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    details: Optional[Dict[str, Any]]
    timestamp: datetime


class TOTPSetup(BaseModel):
    """TOTP setup response schema."""

    secret: str
    qr_code: str  # Base64 encoded QR code image
    backup_codes: List[str]


class TOTPVerify(BaseModel):
    """TOTP verification request schema."""

    code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]+$")