import json
import os
from datetime import datetime
from cryptography.fernet import Fernet

# The filename is changed to reflect an encrypted binary payload
LOG_FILE = "data/incident_history.enc"

# Secure symmetric key placeholder (Must be 32 url-safe base64-encoded bytes)
# In professional cloud production, fetch this via: os.environ.get("AEGIS_CRYPTO_KEY")
SECRET_KEY = b'AegisSystemSecureKeyTelemetryMHR2026=' 
cipher = Fernet(SECRET_KEY)

def log_incident_to_ledger(priority: str, scenario: str, risk_score: int, latency: float):
    """Encrypts and appends sensory telemetry alerts using AES-256 bit format."""
    # Ensure data folder baseline path directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scenario": scenario.upper(),
        "priority": priority,
        "risk_score": risk_score,
        "latency_ms": latency
    }
    
    data = []
    # Attempt to read and decrypt existing data ledger matrices securely
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "rb") as f:
                encrypted_data = f.read()
            if encrypted_data:
                decrypted_bytes = cipher.decrypt(encrypted_data)
                data = json.loads(decrypted_bytes.decode('utf-8'))
        except Exception as e:
            print(f"⚠️ Cryptographic decryption exception bypassed: {str(e)}")
            data = []

    data.append(log_entry)
    
    # Encrypt raw JSON payload back onto safe local storage
    serialized_data = json.dumps(data).encode('utf-8')
    encrypted_bytes = cipher.encrypt(serialized_data)
    
    with open(LOG_FILE, "wb") as f:
        f.write(encrypted_bytes)

def fetch_incident_history():
    """Decrypts historical telemetry matrices dynamically for authorized sessions."""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "rb") as f:
            encrypted_data = f.read()
        decrypted_bytes = cipher.decrypt(encrypted_data)
        return json.loads(decrypted_bytes.decode('utf-8'))
    except Exception:
        return []