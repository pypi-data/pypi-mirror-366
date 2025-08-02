"""Authentication and authorization module for OpenPerformance platform."""

from mlperf.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    require_admin,
    require_user,
)
from mlperf.auth.models import User, UserRole
from mlperf.auth.schemas import (
    Token,
    TokenData,
    UserCreate,
    UserInDB,
    UserResponse,
    UserUpdate,
)
from mlperf.auth.security import get_password_hash, verify_password

__all__ = [
    # JWT functions
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "get_current_user",
    "require_admin",
    "require_user",
    # Models
    "User",
    "UserRole",
    # Schemas
    "Token",
    "TokenData",
    "UserCreate",
    "UserInDB",
    "UserResponse",
    "UserUpdate",
    # Security functions
    "get_password_hash",
    "verify_password",
]