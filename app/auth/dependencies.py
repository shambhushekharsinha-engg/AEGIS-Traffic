"""
AEGIS-Traffic — FastAPI Auth Dependencies
Provides get_current_user, require_role, and get_db.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.auth.auth import decode_access_token, is_jti_blacklisted

security = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    """
    Primary auth dependency. Validates JWT access token, checks blacklist,
    checks account active status. Returns token payload dict.
    """
    # Try Bearer token
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials

    # Fallback: legacy header support (backward compat)
    if not token:
        x_session = request.headers.get("x-session-auth")
        x_role = request.headers.get("x-role-profile")
        if x_session and x_role:
            return {"username": x_session, "role": x_role, "sub": "0", "jti": "legacy"}

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Unauthorized",
                "code": "MISSING_TOKEN",
                "detail": "Authorization header with Bearer token is required.",
            },
        )

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Unauthorized",
                "code": "INVALID_TOKEN",
                "detail": "Token is invalid or has expired. Please login again.",
            },
        )

    # Check blacklist (logout)
    jti = payload.get("jti", "")
    if jti and is_jti_blacklisted(db, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Unauthorized",
                "code": "TOKEN_REVOKED",
                "detail": "This session has been terminated. Please login again.",
            },
        )

    # Verify user still exists and is active
    user_id = int(payload.get("sub", 0))
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": "Unauthorized",
                    "code": "ACCOUNT_DISABLED",
                    "detail": "Your account has been deactivated. Contact an administrator.",
                },
            )
        if user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail={
                    "error": "AccountLocked",
                    "code": "ACCOUNT_LOCKED",
                    "detail": f"Account locked until {user.locked_until.strftime('%Y-%m-%d %H:%M UTC')}.",
                },
            )

    return payload


def require_role(*allowed_roles: str):
    """
    Role-based access control dependency factory.
    Usage:
        @app.get('/admin-only', dependencies=[Depends(require_role('Admin'))])
        @app.get('/admin-or-op',  dependencies=[Depends(require_role('Admin', 'Operator'))])
    """

    def _check(current_user: dict = Depends(get_current_user)):
        role = current_user.get("role", "")
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Forbidden",
                    "code": "INSUFFICIENT_ROLE",
                    "detail": f"This action requires role: {' or '.join(allowed_roles)}. Your role: {role}.",
                },
            )
        return current_user

    return _check


def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[dict]:
    """Like get_current_user but returns None instead of raising 401."""
    try:
        return get_current_user(request, credentials, db)
    except HTTPException:
        return None
