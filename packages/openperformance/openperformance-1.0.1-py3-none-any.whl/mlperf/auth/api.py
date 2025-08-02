"""Authentication API endpoints."""

import json
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBasicCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mlperf.auth.jwt import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    refresh_access_token,
    require_admin,
    revoke_token,
)
from mlperf.auth.models import ApiKey, AuditLog, User
from mlperf.auth.schemas import (
    ApiKeyCreate,
    ApiKeyResponse,
    LoginRequest,
    PasswordChange,
    PasswordReset,
    TOTPSetup,
    TOTPVerify,
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from mlperf.auth.security import (
    calculate_account_lockout_time,
    generate_api_key,
    generate_backup_codes,
    generate_qr_code,
    generate_totp_secret,
    generate_totp_uri,
    get_password_hash,
    hash_backup_code,
    verify_password,
    verify_totp,
)
from mlperf.utils.database import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])


async def create_audit_log(
    db: AsyncSession,
    user_id: Optional[int],
    action: str,
    request: Request,
    details: Optional[dict] = None
) -> None:
    """Create audit log entry."""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        details=json.dumps(details) if details else None
    )
    db.add(audit_log)
    await db.commit()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Register a new user."""
    # Check if user already exists
    existing_user = await db.execute(
        select(User).where(
            (User.email == user_data.email) | (User.username == user_data.username)
        )
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        is_active=user_data.is_active,
        password_changed_at=datetime.utcnow()
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create audit log
    await create_audit_log(
        db,
        user.id,
        "user_registered",
        request,
        {"username": user.username, "email": user.email}
    )
    
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    credentials: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Login user and return access token."""
    # Find user by username or email
    user_query = select(User).where(
        (User.username == credentials.username) | (User.email == credentials.username)
    )
    result = await db.execute(user_query)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if account is locked
    if user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked until {user.locked_until}"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        # Increment failed login attempts
        user.increment_failed_login()
        user.locked_until = calculate_account_lockout_time(user.failed_login_attempts)
        await db.commit()
        
        await create_audit_log(
            db,
            user.id,
            "login_failed",
            request,
            {"reason": "invalid_password", "attempts": user.failed_login_attempts}
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check 2FA if enabled
    if user.totp_secret and not credentials.totp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA code required"
        )
    
    if user.totp_secret:
        if not verify_totp(user.totp_secret, credentials.totp_code):
            await create_audit_log(
                db,
                user.id,
                "login_failed",
                request,
                {"reason": "invalid_2fa"}
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid 2FA code"
            )
    
    # Reset failed login attempts
    user.reset_failed_login()
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    
    # Set secure cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    await create_audit_log(
        db,
        user.id,
        "login_success",
        request
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60  # 30 minutes
    )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Logout user and revoke tokens."""
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if refresh_token:
        try:
            await revoke_token(refresh_token, db)
        except Exception:
            pass  # Ignore errors when revoking
    
    # Clear cookie
    response.delete_cookie("refresh_token")
    
    await create_audit_log(
        db,
        current_user.id,
        "logout",
        request
    )
    
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Refresh access token using refresh token."""
    # Get refresh token from cookie or header
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        # Try to get from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            refresh_token = auth_header.split(" ")[1]
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )
    
    # Refresh tokens
    tokens = await refresh_access_token(refresh_token, db)
    
    # Update cookie
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    
    return Token(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        expires_in=30 * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Get current user information."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Update current user information."""
    # Update user fields
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "preferences" or field == "metadata":
            # Store as JSON string
            setattr(current_user, field, json.dumps(value) if value else None)
        else:
            setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)
    
    await create_audit_log(
        db,
        current_user.id,
        "user_updated",
        request,
        {"fields": list(update_data.keys())}
    )
    
    return UserResponse.model_validate(current_user)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Change user password."""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.password_changed_at = datetime.utcnow()
    await db.commit()
    
    await create_audit_log(
        db,
        current_user.id,
        "password_changed",
        request
    )
    
    return {"message": "Password changed successfully"}


@router.post("/setup-2fa", response_model=TOTPSetup)
async def setup_2fa(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> TOTPSetup:
    """Setup 2FA for user."""
    if current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA already enabled"
        )
    
    # Generate TOTP secret
    secret = generate_totp_secret()
    uri = generate_totp_uri(secret, current_user.email)
    qr_code = generate_qr_code(uri)
    
    # Generate backup codes
    backup_codes = generate_backup_codes()
    
    # Store secret temporarily (not committed until verified)
    current_user.totp_secret = secret
    
    await create_audit_log(
        db,
        current_user.id,
        "2fa_setup_started",
        request
    )
    
    return TOTPSetup(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )


@router.post("/verify-2fa")
async def verify_2fa(
    verification: TOTPVerify,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Verify and enable 2FA."""
    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not initiated"
        )
    
    # Verify code
    if not verify_totp(current_user.totp_secret, verification.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Enable 2FA
    await db.commit()
    
    await create_audit_log(
        db,
        current_user.id,
        "2fa_enabled",
        request
    )
    
    return {"message": "2FA enabled successfully"}


@router.delete("/disable-2fa")
async def disable_2fa(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Disable 2FA for user."""
    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not enabled"
        )
    
    current_user.totp_secret = None
    await db.commit()
    
    await create_audit_log(
        db,
        current_user.id,
        "2fa_disabled",
        request
    )
    
    return {"message": "2FA disabled successfully"}


@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    key_data: ApiKeyCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ApiKeyResponse:
    """Create new API key."""
    # Generate key
    key = generate_api_key()
    
    # Calculate expiration
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
    
    # Create API key
    api_key = ApiKey(
        key=key,
        name=key_data.name,
        user_id=current_user.id,
        scopes=json.dumps(key_data.scopes),
        expires_at=expires_at,
        rate_limit=key_data.rate_limit
    )
    
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    
    await create_audit_log(
        db,
        current_user.id,
        "api_key_created",
        request,
        {"key_name": key_data.name}
    )
    
    return ApiKeyResponse(
        id=api_key.id,
        key=key,  # Only shown once
        name=api_key.name,
        scopes=key_data.scopes,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
        rate_limit=api_key.rate_limit
    )


@router.get("/api-keys", response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ApiKeyResponse]:
    """List user's API keys."""
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.user_id == current_user.id,
            ApiKey.is_active == True
        )
    )
    api_keys = result.scalars().all()
    
    return [
        ApiKeyResponse(
            id=key.id,
            key="*" * 8 + key.key[-8:],  # Partially hidden
            name=key.name,
            scopes=json.loads(key.scopes) if key.scopes else [],
            expires_at=key.expires_at,
            created_at=key.created_at,
            rate_limit=key.rate_limit
        )
        for key in api_keys
    ]


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Revoke API key."""
    # Get API key
    result = await db.execute(
        select(ApiKey).where(
            ApiKey.id == key_id,
            ApiKey.user_id == current_user.id
        )
    )
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    # Revoke key
    api_key.is_active = False
    await db.commit()
    
    await create_audit_log(
        db,
        current_user.id,
        "api_key_revoked",
        request,
        {"key_name": api_key.name}
    )
    
    return {"message": "API key revoked successfully"}


# Admin endpoints
@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> List[UserResponse]:
    """List all users (admin only)."""
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    
    return [UserResponse.model_validate(user) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get user by ID (admin only)."""
    user = await db.get(User, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Update user (admin only)."""
    user = await db.get(User, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "preferences" or field == "metadata":
            setattr(user, field, json.dumps(value) if value else None)
        else:
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    
    await create_audit_log(
        db,
        current_user.id,
        "admin_user_updated",
        request,
        {"target_user_id": user_id, "fields": list(update_data.keys())}
    )
    
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Delete user (admin only)."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    user = await db.get(User, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Soft delete - just deactivate
    user.is_active = False
    await db.commit()
    
    await create_audit_log(
        db,
        current_user.id,
        "admin_user_deleted",
        request,
        {"target_user_id": user_id, "username": user.username}
    )
    
    return {"message": "User deleted successfully"}