"""
AEGIS-Traffic — Database Engine & Session Factory
Supports SQLite (dev) and PostgreSQL (prod) via DATABASE_URL env var.
"""
from sqlalchemy import create_engine, event, text

from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator
import os

from app.config import get_settings

settings = get_settings()

# ── Ensure data directory exists (SQLite) ─────────────────────────────────────
if settings.database_url.startswith("sqlite"):
    _db_path = settings.database_url.replace("sqlite:///", "")
    _db_dir = os.path.dirname(_db_path)
    if _db_dir:
        os.makedirs(_db_dir, exist_ok=True)

# ── Engine ────────────────────────────────────────────────────────────────────
_connect_args = {}
if settings.database_url.startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    echo=settings.db_echo,
    # Only apply pool settings for non-SQLite
    **({"pool_size": settings.db_pool_size, "max_overflow": settings.db_max_overflow}
       if not settings.database_url.startswith("sqlite") else {})
)

# Enable WAL mode for SQLite (better concurrent read performance)
if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# ── Session Factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ── Base ──────────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Dependency ────────────────────────────────────────────────────────────────
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
    For SQLite: creates tables then individually creates indexes, skipping any that exist.
    For PostgreSQL: uses standard create_all which handles IF NOT EXISTS natively.
    """
    from app.db import models  # noqa: F401 — ensures all models are registered

    is_sqlite = settings.database_url.startswith("sqlite")

    if is_sqlite:
        # Create tables (skips existing ones)
        Base.metadata.create_all(bind=engine, checkfirst=True)

        # Create indexes individually with IF NOT EXISTS (SQLite 3.3.7+)
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
        with engine.begin() as conn:
            for sql in _indexes:
                try:
                    conn.execute(text(sql))
                except Exception:
                    pass  # index already exists
    else:
        # PostgreSQL: create_all handles IF NOT EXISTS natively for tables + indexes
        Base.metadata.create_all(bind=engine)
