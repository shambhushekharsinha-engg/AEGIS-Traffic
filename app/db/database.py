"""
AEGIS-Traffic — Database Engine & Session Factory
Supports SQLite (dev/serverless fallback) and PostgreSQL (prod) via DATABASE_URL.
"""
import os
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings

settings = get_settings()


def _resolve_database_url(url: str) -> str:
    """
    Safely resolves SQLite URL for read-only filesystems (e.g. Vercel serverless).
    Falls back to /tmp if local data directory is not writable.
    """
    if not url.startswith("sqlite") or url == "sqlite:///:memory:":
        return url

    _db_path = url.replace("sqlite:///", "")
    _db_dir = os.path.dirname(_db_path)
    if _db_dir:
        try:
            os.makedirs(_db_dir, exist_ok=True)
            probe = os.path.join(_db_dir, ".write_probe")
            with open(probe, "w") as f:
                f.write("ok")
            os.remove(probe)
            return url
        except OSError:
            # Read-only filesystem (e.g. Vercel serverless environment)
            os.makedirs("/tmp/aegis_data", exist_ok=True)
            return f"sqlite:////tmp/aegis_data/{os.path.basename(_db_path)}"
    return url


effective_database_url = _resolve_database_url(settings.database_url)

# ── Engine ────────────────────────────────────────────────────────────────────
_connect_args = {}
if effective_database_url.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_engine(
    effective_database_url,
    connect_args=_connect_args,
    echo=settings.db_echo,
    **({"pool_size": settings.db_pool_size, "max_overflow": settings.db_max_overflow}
       if not effective_database_url.startswith("sqlite") else {})
)

# Enable WAL mode for SQLite (better concurrent read performance)
if effective_database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()
        except Exception:
            pass

# ── Session Factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    """
    FastAPI dependency that yields a DB session and guarantees cleanup.
    Usage:
        def my_endpoint(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables and indexes (idempotent — safe on both fresh and existing DBs).
    """
    from app.db import models  # noqa: F401 — ensures all models are registered

    is_sqlite = effective_database_url.startswith("sqlite")

    if is_sqlite:
        Base.metadata.create_all(bind=engine, checkfirst=True)

        _indexes = [
            "CREATE INDEX IF NOT EXISTS ix_audit_logs_username  ON audit_logs  (username)",
            "CREATE INDEX IF NOT EXISTS ix_audit_logs_action    ON audit_logs  (action)",
            "CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp ON audit_logs  (timestamp)",
            "CREATE INDEX IF NOT EXISTS ix_incident_logs_scenario   ON incident_logs (scenario)",
            "CREATE INDEX IF NOT EXISTS ix_incident_logs_created_at ON incident_logs (created_at)",
            "CREATE INDEX IF NOT EXISTS ix_incident_logs_priority   ON incident_logs (priority)",
            "CREATE INDEX IF NOT EXISTS ix_violation_records_plate     ON violation_records (plate)",
            "CREATE INDEX IF NOT EXISTS ix_violation_records_type_code ON violation_records (type_code)",
        ]
        try:
            with engine.begin() as conn:
                for sql in _indexes:
                    try:
                        conn.execute(text(sql))
                    except Exception:
                        pass
        except Exception as e:
            print(f"[DB WARN] Index creation notice: {e}")
    else:
        Base.metadata.create_all(bind=engine)
