"""
AEGIS-Traffic — History Logger (v8.0.0 Compatibility Shim)

This module is retained for backward API compatibility with existing endpoints
that call log_incident_to_ledger() and fetch_incident_history().

All actual database operations now go through the new production layer:
  - app.db.database  → engine, SessionLocal, get_db()
  - app.db.models    → all ORM models (single source of truth)
  - app.db.crud      → all read/write operations

The legacy encrypted telemetry ledger (EncryptedTelemetryLedger) is still
written to for backward compatibility and older data queries.
"""
import json
import os
from datetime import datetime
from cryptography.fernet import Fernet

# ── Use the new shared engine & session (single DB, no conflicts) ─────────────
from app.db.database import SessionLocal, engine
from app.db.models import EncryptedTelemetryLedger

# ── Encryption (unchanged) ────────────────────────────────────────────────────
_DEFAULT_KEY = b'w21zdO8nX3jPcKFtyoHMmhquCU_sIf_bmra0Zl3A2L4='
_SECRET_KEY = os.environ.get("AEGIS_SECRET_KEY", "").encode("utf-8") or _DEFAULT_KEY
if isinstance(_SECRET_KEY, str):
    _SECRET_KEY = _SECRET_KEY.encode("utf-8")

try:
    cipher = Fernet(_SECRET_KEY)
except Exception:
    cipher = Fernet(_DEFAULT_KEY)


def log_incident_to_ledger(
    operator_id: str,
    priority: str,
    scenario: str,
    risk_score: int,
    latency: float,
    vehicle_count: int = 0,
    active_phase: str = "Unknown",
    signal_timing: int = 15,
    location_name: str = "Times Square, NY",
    latitude: float = 40.7580,
    longitude: float = -73.9855,
    operational_mode: str = "AI Automated Fusion",
):
    """
    Encrypts raw traffic incident metrics and writes to the legacy
    EncryptedTelemetryLedger table. Kept for backward compatibility.
    New code should use crud.create_incident() directly.
    """
    db = SessionLocal()
    try:
        log_entry = {
            "scenario":              scenario.upper(),
            "priority":              priority,
            "risk_score":            risk_score,
            "latency_ms":            latency,
            "vehicle_count":         vehicle_count,
            "active_phase":          active_phase,
            "signal_timing_seconds": signal_timing,
            "location_name":         location_name,
            "latitude":              latitude,
            "longitude":             longitude,
            "operational_mode":      operational_mode,
        }
        serialized = json.dumps(log_entry).encode("utf-8")
        encrypted  = cipher.encrypt(serialized)

        record = EncryptedTelemetryLedger(
            operator_id       = str(operator_id),
            encrypted_payload = encrypted,
            location_name     = location_name,
            latitude          = latitude,
            longitude         = longitude,
            operational_mode  = operational_mode,
        )
        db.add(record)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[history_logger] Ledger write error: {e}")
    finally:
        db.close()


def fetch_incident_history() -> list:
    """
    Decrypts and returns records from the legacy EncryptedTelemetryLedger.
    For new queries use GET /api/v1/incidents (paginated, normalized).
    """
    db = SessionLocal()
    results = []
    try:
        records = (
            db.query(EncryptedTelemetryLedger)
            .order_by(EncryptedTelemetryLedger.timestamp.desc())
            .all()
        )
        for rec in records:
            try:
                payload = json.loads(cipher.decrypt(rec.encrypted_payload).decode("utf-8"))
                # Normalize missing fields from legacy records
                payload.setdefault("vehicle_count", 0)
                payload.setdefault("active_phase", "Unknown")
                payload.setdefault("signal_timing_seconds", 15)
                payload.setdefault("location_name", rec.location_name or "Times Square, NY")
                payload.setdefault("latitude", rec.latitude or 40.7580)
                payload.setdefault("longitude", rec.longitude or -73.9855)
                payload.setdefault("operational_mode", rec.operational_mode or "AI Automated Fusion")
                results.append({
                    "timestamp":   rec.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "operator_id": rec.operator_id,
                    **payload,
                })
            except Exception as decrypt_err:
                print(f"[history_logger] Decryption failed for record {rec.id}: {decrypt_err}")
                continue
    except Exception as e:
        print(f"[history_logger] Fetch error: {e}")
    finally:
        db.close()
    return results