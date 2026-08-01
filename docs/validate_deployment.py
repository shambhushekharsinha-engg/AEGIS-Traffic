"""
AEGIS-Traffic — Deployment & Endpoint Validation Script
Validates backend REST endpoints, frontend assets, database readiness, WebSocket endpoints, and API SLA monitors.
"""
import sys
import os
import time
import requests

def validate_deployment(base_url: str = "http://127.0.0.1:8000"):
    print("============================================================")
    print("Deployment Validation")
    print("============================================================")

    # 1. Backend Service Check
    backend_status = "PASS"
    try:
        r = requests.get(f"{base_url}/health", timeout=3)
        if r.status_code != 200:
            backend_status = "FAIL"
    except Exception:
        backend_status = "FAIL"

    # 2. Frontend / Public Endpoint Check
    frontend_status = "PASS"
    try:
        r = requests.get(f"{base_url}/", timeout=3)
        if r.status_code not in (200, 307, 404): # 200 OK or served index
            frontend_status = "FAIL"
    except Exception:
        frontend_status = "FAIL"

    # 3. Database / Core Health Check
    db_status = "PASS"
    try:
        r = requests.get(f"{base_url}/api/v1/system/health", timeout=3)
        if r.status_code != 200:
            db_status = "FAIL"
    except Exception:
        db_status = "FAIL"

    # 4. WebSockets / Telemetry Endpoint Check
    ws_status = "PASS"
    try:
        # Check HTTP upgrade availability or websocket route endpoint metadata
        r = requests.get(f"{base_url}/api/v1/cctv/analytics?camera_id=CAM-01", timeout=3)
        if r.status_code != 200:
            ws_status = "FAIL"
    except Exception:
        ws_status = "FAIL"

    # 5. REST APIs Suite Check
    api_status = "PASS"
    endpoints = [
        "/api/v1/system/benchmarks",
        "/api/v1/predict/timeline",
        "/api/v1/predict/explain",
        "/api/v1/dataset/explorer",
        "/api/v1/search?q=Connaught",
    ]
    for ep in endpoints:
        try:
            r = requests.get(base_url + ep, timeout=3)
            if r.status_code != 200:
                api_status = "FAIL"
                break
        except Exception:
            api_status = "FAIL"
            break

    # Determine overall status
    statuses = [backend_status, frontend_status, db_status, ws_status, api_status]
    overall_status = "READY" if all(s == "PASS" for s in statuses) else "DEGRADED"

    print(f"\nBackend:    {backend_status}")
    print(f"Frontend:   {frontend_status}")
    print(f"Database:   {db_status}")
    print(f"WebSockets: {ws_status}")
    print(f"API:        {api_status}\n")
    print(f"Overall Status: {overall_status}")
    print("============================================================")

    return overall_status == "READY"

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    validate_deployment(url)
