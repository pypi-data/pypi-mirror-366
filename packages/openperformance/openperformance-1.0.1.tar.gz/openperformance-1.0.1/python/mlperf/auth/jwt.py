"""JWT token handling for authentication."""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from mlperf.auth.models import RefreshToken, User, UserRole
from mlperf.auth.schemas import TokenData
from mlperf.utils.config import get_settings

settings = get_settings()

# Security scheme
security = HTTPBearer()

# Token settings
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"


def create_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access"
) -> str:
    """Create a JWT token."""
    to_encode = data.copy()
    
    # Add token metadata
    now = datetime.utcnow()
    to_encode.update({
        "iat": now,
        "jti": str(uuid.uuid4()),  # JWT ID for revocation
        "type": token_type
    })
    
    # Set expiration
    if expires_delta:
        expire = now + expires_delta
    else:
        if token_type == "access":
            expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode["exp"] = expire
    
    # Encode token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt


def create_access_token(
    user: User,
    scopes: Optional[List[str]] = None
) -> str:
    """Create access token for user."""
    data = {
        "sub": str(user.id),
        "email": user.email,
        "username": user.username,
        "role": user.role.value,
        "scopes": scopes or []
    }
    
    return create_token(
        data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access"
    )


def create_refresh_token(user: User) -> str:
    """Create refresh token for user."""
    data = {
        "sub": str(user.id),
        "email": user.email
    }
    
    return create_token(
        data,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh"
    )


def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        # Extract token data
        token_data = TokenData(
            sub=payload.get("sub"),
            email=payload.get("email"),
            username=payload.get("username"),
            role=UserRole(payload.get("role", "user")),
            scopes=payload.get("scopes", []),
            exp=payload.get("exp"),
            iat=payload.get("iat"),
            jti=payload.get("jti")
        )
        
        return token_data
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(),  # Will need to implement get_db
) -> TokenData:
    """Verify JWT token from request."""
    token = credentials.credentials
    
    # Decode token
    token_data = decode_token(token)
    
    # Check token type
    if token_data.jti:
        # Check if token is revoked (implement token revocation check)
        pass
    
    return token_data


async def get_current_user(
    token_data: TokenData = Depends(verify_token),
    db: AsyncSession = Depends(),  # Will need to implement get_db
) -> User:
    """Get current user from token."""
    # Fetch user from database
    user = await db.get(User, int(token_data.sub))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    if user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is locked"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def require_scopes(required_scopes: List[str]):
    """Dependency to require specific scopes."""
    async def scope_checker(
        token_data: TokenData = Depends(verify_token)
    ):
        token_scopes = set(token_data.scopes)
        required = set(required_scopes)
        
        if not required.issubset(token_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required scopes: {', '.join(required_scopes)}"
            )
        
        return token_data
    
    return scope_checker


def require_role(allowed_roles: List[UserRole]):
    """Dependency to require specific roles."""
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {', '.join(r.value for r in allowed_roles)}"
            )
        
        return current_user
    
    return role_checker


# Convenience functions
require_admin = require_role([UserRole.ADMIN])
require_user = require_role([UserRole.ADMIN, UserRole.USER])
require_viewer = require_role([UserRole.ADMIN, UserRole.USER, UserRole.VIEWER])


async def revoke_token(
    token: str,
    db: AsyncSession
) -> None:
    """Revoke a refresh token."""
    # Decode token to get JTI
    token_data = decode_token(token)
    
    if not token_data.jti:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token does not support revocation"
        )
    
    # Create revocation record
    refresh_token = RefreshToken(
        token=token,
        user_id=int(token_data.sub),
        expires_at=datetime.fromtimestamp(token_data.exp),
        revoked=True,
        revoked_at=datetime.utcnow()
    )
    
    db.add(refresh_token)
    await db.commit()


async def refresh_access_token(
    refresh_token: str,
    db: AsyncSession
) -> Dict[str, str]:
    """Refresh access token using refresh token."""
    # Decode refresh token
    token_data = decode_token(refresh_token)
    
    # Verify token type
    if token_data.jti:
        # Check if refresh token is revoked
        revoked = await db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.revoked == True
        ).first()
        
        if revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
            )
    
    # Get user
    user = await db.get(User, int(token_data.sub))
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(user)
    new_refresh_token = create_refresh_token(user)
    
    # Revoke old refresh token
    await revoke_token(refresh_token, db)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }