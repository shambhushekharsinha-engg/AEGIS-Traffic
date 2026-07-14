import json
import os
from datetime import datetime

LOG_FILE = "data/incident_history.json"

def log_incident_to_ledger(priority: str, scenario: str, risk_score: int, latency: float):
    """Appends structural telemetry alerts to a rolling time-series audit tracking matrix."""
    # Ensure data folder baseline exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scenario": scenario.upper(),
        "priority": priority,
        "risk_score": risk_score,
        "latency_ms": latency
    }
    
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []
            
        data.append(log_entry)
        
        with open(LOG_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"⚠️ Ledger IO exception bypassed: {str(e)}")

def fetch_incident_history():
    """Retrieves chronological incident trends for dashboard matrix charts."""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []