import json
import os
from datetime import datetime
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, DateTime, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
import secrets

# Ensure data directory structures are fully initialized
DB_DIR = "data"
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_DIR}/aegis_secure_vault.db"

# --- INDUSTRIAL KEY MANAGEMENT & ROTATION ---
DEFAULT_KEY = b'w21zdO8nX3jPcKFtyoHMmhquCU_sIf_bmra0Zl3A2L4='
SECRET_KEY = os.environ.get("AEGIS_SECRET_KEY")

if not SECRET_KEY:
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("AEGIS_SECRET_KEY="):
                    SECRET_KEY = line.strip().split("=")[1]
                    break
    
if not SECRET_KEY:
    try:
        with open(".env", "a") as f:
            f.write(f"\n# Aegis Cryptographic Vault Symmetric Secret Key\nAEGIS_SECRET_KEY={DEFAULT_KEY.decode('utf-8')}\n")
    except Exception as e:
        print(f"⚠️ Could not write to .env: {e}")
    SECRET_KEY = DEFAULT_KEY
else:
    if isinstance(SECRET_KEY, str):
        SECRET_KEY = SECRET_KEY.encode('utf-8')

try:
    cipher = Fernet(SECRET_KEY)
except Exception as e:
    print(f"⚠️ Invalid key configuration, reverting to fallback default key. Error: {e}")
    SECRET_KEY = DEFAULT_KEY
    cipher = Fernet(SECRET_KEY)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False) # Admin, Operator, Auditor

class EncryptedTelemetryLedger(Base):
    __tablename__ = "telemetry_ledger"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    operator_id = Column(String, nullable=False)
    encrypted_payload = Column(LargeBinary, nullable=False)
    location_name = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    operational_mode = Column(String, nullable=True)

# Build Relational Pooling Infrastructure Engine Layers
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# --- SECURE NATIVE HASHING & SEEDING ---
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"pbkdf2_sha256:100000:{salt}:{pw_hash.hex()}"

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        parts = hashed_password.split(':')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            return False
        iterations = int(parts[1])
        salt = parts[2]
        original_hash = parts[3]
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), iterations)
        return secrets.compare_digest(new_hash.hex(), original_hash)
    except Exception:
        return False

def migrate_database():
    from sqlalchemy import inspect
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns('telemetry_ledger')]
    with engine.begin() as conn:
        if 'location_name' not in columns:
            conn.execute(text("ALTER TABLE telemetry_ledger ADD COLUMN location_name VARCHAR"))
        if 'latitude' not in columns:
            conn.execute(text("ALTER TABLE telemetry_ledger ADD COLUMN latitude FLOAT"))
        if 'longitude' not in columns:
            conn.execute(text("ALTER TABLE telemetry_ledger ADD COLUMN longitude FLOAT"))
        if 'operational_mode' not in columns:
            conn.execute(text("ALTER TABLE telemetry_ledger ADD COLUMN operational_mode VARCHAR"))

def seed_users():
    db = SessionLocal()
    try:
        # Seed Admin
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="Admin"
            )
            db.add(admin_user)
        
        # Seed Operator
        operator = db.query(User).filter(User.username == "operator").first()
        if not operator:
            operator_user = User(
                username="operator",
                password_hash=hash_password("operator123"),
                role="Operator"
            )
            db.add(operator_user)

        # Seed Auditor
        auditor = db.query(User).filter(User.username == "auditor").first()
        if not auditor:
            auditor_user = User(
                username="auditor",
                password_hash=hash_password("auditor123"),
                role="Auditor"
            )
            db.add(auditor_user)
            
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"⚠️ User seeding failure: {e}")
    finally:
        db.close()

# Run database migrations and seed users automatically
migrate_database()
seed_users()

def log_incident_to_ledger(operator_id: str, priority: str, scenario: str, risk_score: int, 
                           latency: float, vehicle_count: int = 0, active_phase: str = "Unknown", 
                           signal_timing: int = 15, location_name: str = "Times Square, NY",
                           latitude: float = 40.7580, longitude: float = -73.9855,
                           operational_mode: str = "AI Automated Fusion"):
    """
    Encrypts raw traffic incident metrics and commits them to the secure database ledger.
    """
    db = SessionLocal()
    try:
        log_entry = {
            "scenario": scenario.upper(),
            "priority": priority,
            "risk_score": risk_score,
            "latency_ms": latency,
            "vehicle_count": vehicle_count,
            "active_phase": active_phase,
            "signal_timing_seconds": signal_timing,
            "location_name": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "operational_mode": operational_mode
        }
        
        # Serialize text strings into protected binary structures
        serialized_data = json.dumps(log_entry).encode('utf-8')
        encrypted_bytes = cipher.encrypt(serialized_data)
        
        db_record = EncryptedTelemetryLedger(
            operator_id=operator_id,
            encrypted_payload=encrypted_bytes,
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            operational_mode=operational_mode
        )
        db.add(db_record)
        db.commit()
        print(f"🔒 Encrypted log committed to relational ledger for scenario: {scenario.upper()}")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Cryptographic database vault failure traces: {str(e)}")
    finally:
        db.close()

def fetch_incident_history():
    """
    Decrypts operational logs from the ledger dynamically for dashboard plotting.
    Filters out and handles records that cannot be decrypted due to key rotations gracefully.
    """
    db = SessionLocal()
    decrypted_history = []
    try:
        records = db.query(EncryptedTelemetryLedger).order_by(EncryptedTelemetryLedger.timestamp.desc()).all()
        for record in records:
            try:
                decrypted_bytes = cipher.decrypt(record.encrypted_payload)
                payload = json.loads(decrypted_bytes.decode('utf-8'))
                
                # Normalize legacy records that lack traffic fields or geographic fields
                if "vehicle_count" not in payload:
                    payload["vehicle_count"] = 0
                if "active_phase" not in payload:
                    payload["active_phase"] = "Unknown"
                if "signal_timing_seconds" not in payload:
                    payload["signal_timing_seconds"] = 15
                if "location_name" not in payload:
                    payload["location_name"] = record.location_name or "Times Square, NY"
                if "latitude" not in payload:
                    payload["latitude"] = record.latitude or 40.7580
                if "longitude" not in payload:
                    payload["longitude"] = record.longitude or -73.9855
                if "operational_mode" not in payload:
                    payload["operational_mode"] = record.operational_mode or "AI Automated Fusion"
                
                decrypted_history.append({
                    "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "operator_id": record.operator_id,
                    **payload
                })
            except Exception as decrypt_error:
                # Handle decryption failures gracefully if key has changed and old logs cannot be decrypted
                print(f"⚠️ Decryption failed for record ID {record.id}: {decrypt_error}. Skipping entry.")
                continue
    except Exception as e:
        print(f"⚠️ Crypto parsing exceptions safely bypassed: {str(e)}")
    finally:
        db.close()
    return decrypted_history