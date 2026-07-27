"""
AEGIS-Traffic — Database CRUD Operations
All database read/write operations go here. Never call DB directly from endpoints.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.db.models import (
    User, RefreshToken, SessionBlacklist, AuditLog,
    IncidentLog, ViolationRecord
)
from app.auth.auth import hash_password
from app.config import get_settings

settings = get_settings()


# ──────────────────────────────────────────────────────────────────────
#  USER CRUD
# ──────────────────────────────────────────────────────────────────────

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> tuple[List[User], int]:
    """Returns (users_list, total_count) with optional filtering."""
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    if is_active is not None:
        q = q.filter(User.is_active == is_active)
    total = q.count()
    users = q.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return users, total


def create_user(
    db: Session,
    username: str,
    password: str,
    role: str,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    created_by: Optional[str] = None,
) -> User:
    """Create a new user with hashed password."""
    user = User(
        username      = username,
        email         = email,
        full_name     = full_name,
        password_hash = hash_password(password),
        role          = role,
        is_active     = True,
        is_verified   = True,  # Admin-created users are pre-verified
        created_by    = created_by,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    db: Session,
    user: User,
    full_name: Optional[str] = None,
    email: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    password: Optional[str] = None,
) -> User:
    """Partially update user fields."""
    if full_name  is not None: user.full_name     = full_name
    if email      is not None: user.email         = email
    if role       is not None: user.role          = role
    if is_active  is not None: user.is_active      = is_active
    if password   is not None: user.password_hash  = hash_password(password)
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def seed_default_users(db: Session) -> None:
    """
    Seed Admin, Operator, and Auditor accounts if they don't exist.
    Credentials should be changed immediately after first login in production.
    """
    defaults = [
        {"username": "admin",    "password": "Admin@AEGIS2024!",    "role": "Admin",    "full_name": "System Administrator"},
        {"username": "operator", "password": "Operator@AEGIS2024!",  "role": "Operator", "full_name": "Traffic Operator"},
        {"username": "auditor",  "password": "Auditor@AEGIS2024!",   "role": "Auditor",  "full_name": "System Auditor"},
    ]
    for u in defaults:
        if not get_user_by_username(db, u["username"]):
            create_user(
                db,
                username   = u["username"],
                password   = u["password"],
                role       = u["role"],
                full_name  = u["full_name"],
                created_by = "system",
            )
    print("[DB] Default users seeded.")


# ──────────────────────────────────────────────────────────────────────
#  INCIDENT CRUD
# ──────────────────────────────────────────────────────────────────────

def create_incident(
    db: Session,
    operator_name: str,
    scenario: str,
    priority: str,
    risk_score: int,
    latency_ms: float,
    vehicle_count: int = 0,
    avg_speed_kmh: Optional[float] = None,
    traffic_density: Optional[str] = None,
    active_phase: Optional[str] = None,
    signal_timing: Optional[int] = None,
    operational_mode: Optional[str] = None,
    crime_score: Optional[float] = None,
    crime_type: Optional[str] = None,
    crime_severity: Optional[str] = None,
    crime_is_anomaly: Optional[bool] = None,
    location_name: str = "Unknown",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    operator_id: Optional[int] = None,
    request_id: Optional[str] = None,
    encrypted_payload: Optional[bytes] = None,
    violations_data: Optional[list] = None,
) -> IncidentLog:
    """Create a full incident record with linked violation rows."""
    incident = IncidentLog(
        operator_id      = operator_id,
        operator_name    = operator_name,
        request_id       = request_id,
        scenario         = scenario.upper(),
        priority         = priority,
        risk_score       = risk_score,
        latency_ms       = latency_ms,
        vehicle_count    = vehicle_count,
        avg_speed_kmh    = avg_speed_kmh,
        traffic_density  = traffic_density,
        active_phase     = active_phase,
        signal_timing    = signal_timing,
        operational_mode = operational_mode,
        crime_score      = crime_score,
        crime_type       = crime_type,
        crime_severity   = crime_severity,
        crime_is_anomaly = crime_is_anomaly,
        location_name    = location_name,
        latitude         = latitude,
        longitude        = longitude,
        encrypted_payload = encrypted_payload,
    )
    db.add(incident)
    db.flush()  # get incident.id before adding violations

    # Normalize violations into queryable rows
    if violations_data:
        for v in violations_data:
            vr = ViolationRecord(
                incident_id  = incident.id,
                violation_id = v.get("violation_id"),
                type_code    = v.get("type_code", "UNKNOWN"),
                type_label   = v.get("type"),
                severity     = v.get("severity", "MEDIUM"),
                plate        = v.get("plate"),
                vehicle_id   = v.get("vehicle_id"),
                fine_amount  = v.get("fine_amount_inr", 0),
                location_name = location_name,
                source       = v.get("source", "TRAFFIC_RULE"),
                evidence_note = v.get("evidence_note"),
            )
            db.add(vr)

    db.commit()
    db.refresh(incident)
    return incident


def get_incidents(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    scenario: Optional[str] = None,
    operator_name: Optional[str] = None,
    priority: Optional[str] = None,
) -> tuple[List[IncidentLog], int]:
    """Paginated incident list with optional filters."""
    q = db.query(IncidentLog)
    if scenario:       q = q.filter(IncidentLog.scenario == scenario.upper())
    if operator_name:  q = q.filter(IncidentLog.operator_name == operator_name)
    if priority:       q = q.filter(IncidentLog.priority.contains(priority))
    total = q.count()
    items = q.order_by(desc(IncidentLog.created_at)).offset(skip).limit(limit).all()
    return items, total


def get_incident_by_id(db: Session, incident_id: int) -> Optional[IncidentLog]:
    return db.query(IncidentLog).filter(IncidentLog.id == incident_id).first()


# ──────────────────────────────────────────────────────────────────────
#  VIOLATION CRUD
# ──────────────────────────────────────────────────────────────────────

def get_violations(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    plate: Optional[str] = None,
    type_code: Optional[str] = None,
    severity: Optional[str] = None,
) -> tuple[List[ViolationRecord], int]:
    """Paginated, searchable violation records."""
    q = db.query(ViolationRecord)
    if plate:     q = q.filter(ViolationRecord.plate.contains(plate))
    if type_code: q = q.filter(ViolationRecord.type_code == type_code)
    if severity:  q = q.filter(ViolationRecord.severity == severity)
    total = q.count()
    items = q.order_by(desc(ViolationRecord.created_at)).offset(skip).limit(limit).all()
    return items, total


def get_violation_stats(db: Session) -> dict:
    """Aggregate violation statistics."""
    total         = db.query(func.count(ViolationRecord.id)).scalar() or 0
    total_fines   = db.query(func.sum(ViolationRecord.fine_amount)).scalar() or 0
    by_type       = (
        db.query(ViolationRecord.type_code, func.count(ViolationRecord.id))
        .group_by(ViolationRecord.type_code)
        .all()
    )
    by_severity   = (
        db.query(ViolationRecord.severity, func.count(ViolationRecord.id))
        .group_by(ViolationRecord.severity)
        .all()
    )
    return {
        "total_violations": total,
        "total_fines_inr":  int(total_fines),
        "by_type":          {t: c for t, c in by_type},
        "by_severity":      {s: c for s, c in by_severity},
    }


# ──────────────────────────────────────────────────────────────────────
#  AUDIT LOG CRUD
# ──────────────────────────────────────────────────────────────────────

def get_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    username: Optional[str] = None,
    action: Optional[str] = None,
    status: Optional[str] = None,
) -> tuple[List[AuditLog], int]:
    """Paginated audit log retrieval."""
    q = db.query(AuditLog)
    if username: q = q.filter(AuditLog.username == username)
    if action:   q = q.filter(AuditLog.action   == action)
    if status:   q = q.filter(AuditLog.status    == status)
    total = q.count()
    items = q.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    return items, total


def get_incident_stats(db: Session) -> dict:
    """Dashboard summary stats."""
    total        = db.query(func.count(IncidentLog.id)).scalar() or 0
    by_scenario  = (
        db.query(IncidentLog.scenario, func.count(IncidentLog.id))
        .group_by(IncidentLog.scenario).all()
    )
    by_priority  = (
        db.query(IncidentLog.priority, func.count(IncidentLog.id))
        .group_by(IncidentLog.priority).all()
    )
    avg_risk     = db.query(func.avg(IncidentLog.risk_score)).scalar() or 0
    crime_count  = db.query(func.count(IncidentLog.id)).filter(
        IncidentLog.crime_is_anomaly == True
    ).scalar() or 0
    return {
        "total_incidents":  total,
        "crime_incidents":  crime_count,
        "avg_risk_score":   round(float(avg_risk), 1),
        "by_scenario":      {s: c for s, c in by_scenario},
        "by_priority":      {p: c for p, c in by_priority},
    }
