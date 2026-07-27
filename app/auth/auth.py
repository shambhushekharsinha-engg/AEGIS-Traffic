"""
AEGIS-Traffic — Production Authentication Module
Features:
  - Standards-compliant JWT (PyJWT) with jti (JWT ID) claim
  - Access token: 15-minute expiry
  - Refresh token: 7-day expiry, stored hashed in DB
  - Secure logout: JTI blacklisted + refresh token revoked
  - PBKDF2-SHA256 password hashing
  - Account lockout after N failed attempts
"""
from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import User, RefreshToken, SessionBlacklist, AuditLog

settings = get_settings()


# ──────────────────────────────────────────────────────────────────────
# Password hashing
# ──────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """PBKDF2-SHA256 with random salt. Format: pbkdf2_sha256:iters:salt:hash"""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 260_000
    )
    return f"pbkdf2_sha256:260000:{salt}:{pw_hash.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Constant-time password verification."""
    try:
        parts = hashed.split(":")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt       = parts[2]
        orig_hash  = parts[3]
        new_hash   = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
        )
        return secrets.compare_digest(new_hash.hex(), orig_hash)
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────────────
# Token creation
# ──────────────────────────────────────────────────────────────────────

def _make_jti() -> str:
    return str(uuid.uuid4()).replace("-", "")


def create_access_token(user: User) -> tuple[str, str]:
    """
    Create a short-lived access token.
    Returns (token_string, jti)
    """
    jti = _make_jti()
    now    = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub":      str(user.id),
        "username": user.username,
        "role":     user.role,
        "email":    user.email or "",
        "jti":      jti,
        "iat":      int(now.timestamp()),
        "exp":      int(expire.timestamp()),
        "type":     "access",
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti


def create_refresh_token_string() -> str:
    """Generate a cryptographically random refresh token string (not JWT)."""
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """SHA-256 hash of the refresh token for storage."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def store_refresh_token(
    db: Session,
    user: User,
    token: str,
    ip_address: Optional[str] = None,
    device_info: Optional[str] = None,
) -> RefreshToken:
    """Hash and persist a refresh token to the database."""
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    rt = RefreshToken(
        user_id     = user.id,
        token_hash  = hash_refresh_token(token),
        expires_at  = expires_at.replace(tzinfo=None),  # store as naive UTC
        ip_address  = ip_address,
        device_info = device_info,
    )
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


# ──────────────────────────────────────────────────────────────────────
# Token verification
# ──────────────────────────────────────────────────────────────────────

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate an access token. Returns payload or None."""
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "iat", "sub", "jti"]},
            leeway=10,  # 10s clock skew tolerance
        )
    except (ExpiredSignatureError, InvalidTokenError):
        return None


def is_jti_blacklisted(db: Session, jti: str) -> bool:
    """Check if a JTI has been revoked (logout)."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    record = db.query(SessionBlacklist).filter(
        SessionBlacklist.jti == jti,
        SessionBlacklist.expires_at > now,
    ).first()
    return record is not None


def blacklist_jti(db: Session, jti: str, user_id: int, expires_at: datetime) -> None:
    """Add a JTI to the blacklist (used on logout)."""
    entry = SessionBlacklist(jti=jti, user_id=user_id, expires_at=expires_at)
    db.add(entry)
    db.commit()


def rotate_refresh_token(
    db: Session,
    old_token: str,
    ip_address: Optional[str] = None,
) -> Optional[tuple[str, str]]:
    """
    Validate old refresh token, revoke it, issue a new one.
    Returns (new_token_string, new_token_hash) or None if invalid.
    """
    token_hash = hash_refresh_token(old_token)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    rt = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked    == False,
        RefreshToken.expires_at > now,
    ).first()
    if not rt:
        return None

    # Revoke old token (rotation)
    rt.revoked    = True
    rt.revoked_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()

    # Issue new refresh token
    new_token = create_refresh_token_string()
    new_hash  = hash_refresh_token(new_token)
    new_rt = RefreshToken(
        user_id     = rt.user_id,
        token_hash  = new_hash,
        expires_at  = (datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)).replace(tzinfo=None),
        ip_address  = ip_address,
    )
    db.add(new_rt)
    db.commit()
    return new_token, new_hash


# ──────────────────────────────────────────────────────────────────────
# Account management helpers
# ──────────────────────────────────────────────────────────────────────

def record_failed_login(db: Session, user: User) -> None:
    """Increment failed attempts and lock account if threshold reached."""
    user.failed_attempts = (user.failed_attempts or 0) + 1
    if user.failed_attempts >= settings.max_login_attempts:
        user.locked_until    = (datetime.now(timezone.utc) + timedelta(minutes=settings.lockout_duration_minutes)).replace(tzinfo=None)
        user.failed_attempts = 0  # reset after lockout applied
    db.commit()


def record_successful_login(db: Session, user: User) -> None:
    """Reset failed attempts and update last_login timestamp."""
    user.failed_attempts = 0
    user.locked_until    = None
    user.last_login      = datetime.now(timezone.utc).replace(tzinfo=None)
    user.login_count     = (user.login_count or 0) + 1
    db.commit()


# ──────────────────────────────────────────────────────────────────────
# Audit logging helper
# ──────────────────────────────────────────────────────────────────────

def write_audit(
    db: Session,
    action: str,
    username: str = "system",
    user_id: Optional[int] = None,
    resource: Optional[str] = None,
    method: Optional[str] = None,
    status: str = "SUCCESS",
    detail: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Write an immutable audit log entry. Silently ignores DB errors."""
    try:
        entry = AuditLog(
            user_id    = user_id,
            username   = username,
            action     = action,
            resource   = resource,
            method     = method,
            status     = status,
            detail     = detail,
            ip_address = ip_address,
            user_agent = user_agent,
            request_id = request_id,
        )
        db.add(entry)
        db.commit()
    except Exception as exc:
        db.rollback()
        print(f"[AUDIT] Failed to write audit log: {exc}")
