"""
AEGIS-Traffic — Full Production SQLAlchemy ORM Models

Tables:
  users              — Full user profile with lockout and lifecycle
  refresh_tokens     — Server-side refresh token store (allows logout)
  session_blacklist  — Revoked access token JTIs (instant logout)
  audit_logs         — Immutable record of every sensitive action
  incident_logs      — Traffic/crime simulation incident records
  violation_records  — Normalized, searchable violation rows
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Float,
    Text, LargeBinary, ForeignKey

)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.db.database import Base


class User(Base):
    """Full user profile with security fields."""
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    username        = Column(String(64), unique=True, nullable=False, index=True)
    email           = Column(String(255), unique=True, nullable=True, index=True)
    full_name       = Column(String(128), nullable=True)
    password_hash   = Column(String(256), nullable=False)
    role            = Column(String(32), nullable=False, default="Operator")
    # Admin | Operator | Auditor

    # Lifecycle
    is_active       = Column(Boolean, nullable=False, default=True)
    is_verified     = Column(Boolean, nullable=False, default=False)
    created_at      = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at      = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    last_login      = Column(DateTime, nullable=True)
    created_by      = Column(String(64), nullable=True)  # username of Admin who created this user

    # Security
    login_count     = Column(Integer, nullable=False, default=0)
    failed_attempts = Column(Integer, nullable=False, default=0)
    locked_until    = Column(DateTime, nullable=True)

    # Relationships
    refresh_tokens  = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs      = relationship("AuditLog",     back_populates="user")
    incidents       = relationship("IncidentLog",  back_populates="operator")

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r} role={self.role!r}>"

    @property
    def is_locked(self) -> bool:
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until


class RefreshToken(Base):
    """Server-side refresh token store. Enables real logout and token rotation."""
    __tablename__ = "refresh_tokens"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash  = Column(String(128), unique=True, nullable=False, index=True)
    issued_at   = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at  = Column(DateTime, nullable=False)
    revoked     = Column(Boolean, nullable=False, default=False)
    revoked_at  = Column(DateTime, nullable=True)
    device_info = Column(String(256), nullable=True)   # e.g. "Chrome on Windows"
    ip_address  = Column(String(64),  nullable=True)

    user = relationship("User", back_populates="refresh_tokens")



class SessionBlacklist(Base):
    """Revoked access-token JTIs. Checked on every authenticated request."""
    __tablename__ = "session_blacklist"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    jti        = Column(String(64), unique=True, nullable=False, index=True)
    user_id    = Column(Integer, nullable=False)
    revoked_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # auto-cleanup after this time


class AuditLog(Base):
    """Immutable audit trail — every sensitive action is recorded here."""
    __tablename__ = "audit_logs"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    username   = Column(String(64),  nullable=False, default="system")
    action     = Column(String(64),  nullable=False)   # e.g. LOGIN, LOGOUT, SIMULATE, TRAIN
    resource   = Column(String(128), nullable=True)    # e.g. /api/v1/simulation/run
    method     = Column(String(16),  nullable=True)    # GET | POST | PATCH | DELETE
    status     = Column(String(32),  nullable=False, default="SUCCESS")  # SUCCESS | FAILURE | DENIED
    detail     = Column(Text,        nullable=True)    # extra context JSON string
    ip_address = Column(String(64),  nullable=True)
    user_agent = Column(String(256), nullable=True)
    request_id = Column(String(64),  nullable=True)    # UUID per-request
    timestamp  = Column(DateTime,    nullable=False, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")



class IncidentLog(Base):
    """Traffic + crime simulation incident records. Each simulation run = one row."""
    __tablename__ = "incident_logs"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    operator_id      = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    operator_name    = Column(String(64),  nullable=False, default="unknown")
    request_id       = Column(String(64),  nullable=True,  index=True)

    # Scenario
    scenario         = Column(String(32),  nullable=False)
    priority         = Column(String(64),  nullable=False)
    risk_score       = Column(Integer,     nullable=False, default=0)
    latency_ms       = Column(Float,       nullable=False, default=0.0)

    # Traffic
    vehicle_count    = Column(Integer,     nullable=False, default=0)
    avg_speed_kmh    = Column(Float,       nullable=True)
    traffic_density  = Column(String(32),  nullable=True)
    active_phase     = Column(String(32),  nullable=True)
    signal_timing    = Column(Integer,     nullable=True)
    operational_mode = Column(String(64),  nullable=True)

    # Crime / UCF
    crime_score      = Column(Float,       nullable=True)
    crime_type       = Column(String(64),  nullable=True)
    crime_severity   = Column(String(32),  nullable=True)
    crime_is_anomaly = Column(Boolean,     nullable=True)

    # Location
    location_name    = Column(String(128), nullable=True)
    latitude         = Column(Float,       nullable=True)
    longitude        = Column(Float,       nullable=True)

    # Full encrypted payload (backward compat)
    encrypted_payload = Column(LargeBinary, nullable=True)

    created_at       = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    operator         = relationship("User", back_populates="incidents")
    violations       = relationship("ViolationRecord", back_populates="incident", cascade="all, delete-orphan")



class ViolationRecord(Base):
    """Normalized, fully queryable traffic violation rows linked to incidents."""
    __tablename__ = "violation_records"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    incident_id   = Column(Integer, ForeignKey("incident_logs.id", ondelete="CASCADE"), nullable=False)
    violation_id  = Column(String(64),  nullable=True)   # original VID string
    type_code     = Column(String(64),  nullable=False, index=True)
    type_label    = Column(String(128), nullable=True)
    severity      = Column(String(32),  nullable=False)
    plate         = Column(String(32),  nullable=True, index=True)
    vehicle_id    = Column(String(64),  nullable=True)
    fine_amount   = Column(Integer,     nullable=False, default=0)  # INR
    location_name = Column(String(128), nullable=True)
    source        = Column(String(64),  nullable=True)   # TRAFFIC_RULE | UCF_CRIME_CLASSIFIER
    evidence_note = Column(Text,        nullable=True)
    created_at    = Column(DateTime,    nullable=False, default=datetime.utcnow)

    incident = relationship("IncidentLog", back_populates="violations")



# ── Legacy table (kept for backward compatibility) ────────────────────────────
from sqlalchemy import String as Str  # noqa
class EncryptedTelemetryLedger(Base):
    """Legacy encrypted telemetry — kept for backward compatibility with old data."""
    __tablename__ = "telemetry_ledger"
    __table_args__ = {"extend_existing": True}

    id               = Column(Integer, primary_key=True, autoincrement=True)
    timestamp        = Column(DateTime, default=datetime.utcnow)
    operator_id      = Column(String, nullable=False)
    encrypted_payload = Column(LargeBinary, nullable=False)
    location_name    = Column(String, nullable=True)
    latitude         = Column(Float, nullable=True)
    longitude        = Column(Float, nullable=True)
    operational_mode = Column(String, nullable=True)


class CitizenHazardReport(Base):
    """Public citizen hazard reports (potholes, accidents, outages)."""
    __tablename__ = "citizen_hazard_reports"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    report_id     = Column(String(64), unique=True, nullable=False, index=True)
    citizen_name  = Column(String(64), nullable=False, default="Anonymous Citizen")
    contact_info  = Column(String(128), nullable=True)
    hazard_type   = Column(String(64), nullable=False)  # Pothole | Accident | Signal Outage | Flooding | Debris
    description   = Column(Text, nullable=True)
    location_name = Column(String(128), nullable=False)
    latitude      = Column(Float, nullable=False)
    longitude     = Column(Float, nullable=False)
    status        = Column(String(32), nullable=False, default="SUBMITTED")  # SUBMITTED | IN_REVIEW | DISPATCHED | RESOLVED
    created_at    = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

