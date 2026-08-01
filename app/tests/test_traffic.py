import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.vision_module import FolderStreamAnalyzer as VisionEngine
from app.core.audio_module import AudioAnalyzer as AudioEngine
from app.pipeline.fusion_core import MultimodalFusionCore


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_vision_engine_synthetic_rendering():
    """Verify that the VisionEngine correctly synthesizes traffic frames and runs YOLOv8."""
    engine = VisionEngine()
    result = engine.process_traffic_scene("normal")
    assert "detections" in result
    assert "image_b64" in result
    assert len(result["image_b64"]) > 0
    labels = [d["label"] for d in result["detections"]]
    assert "car" in labels


def test_audio_engine_siren_detection():
    """Verify that the AudioEngine synthesizes WAV signals and detects siren sweeps."""
    engine = AudioEngine()
    normal_res = engine.check_anomaly("data/audio_samples/normal_sound.wav")
    assert normal_res["type"] == "Ambient"
    assert normal_res["status"] == "Normal"
    
    emergency_res = engine.check_anomaly("data/audio_samples/emergency_sound.wav")
    assert emergency_res["type"] == "Siren"
    assert emergency_res["status"] == "Anomaly Detected"
    assert emergency_res["peak_frequency"] > 0


def test_multimodal_fusion_priority_rules():
    """Verify that the Fusion Core adaptively overrides traffic light states under hazards."""
    core = MultimodalFusionCore()
    
    res_normal = core.fuse_and_classify([{"label": "car"}], {"type": "Ambient", "db_level": 42.0}, "normal")
    assert res_normal["priority"] == "✅ NOMINAL CONTROL"
    assert res_normal["signal_timing_seconds"] == 15
    assert res_normal["active_phase"] == "North-South Green"
    
    res_emergency = core.fuse_and_classify([{"label": "car"}, {"label": "truck"}], {"type": "Siren", "db_level": 85.0}, "emergency")
    assert res_emergency["priority"] == "🚨 EMERGENCY OVERRIDE (PRIORITY 1)"
    assert res_emergency["signal_timing_seconds"] == 25
    assert res_emergency["active_phase"] == "EMERGENCY VEHICLE PRIORITY (GREEN)"
    
    res_accident = core.fuse_and_classify([{"label": "car"}], {"type": "Collision", "db_level": 92.0}, "accident")
    assert res_accident["priority"] == "🚨 COLLISION ALERT (PRIORITY 2)"
    assert res_accident["active_phase"] == "ALL RED (CONTAINMENT)"


def test_fastapi_endpoints_clearance(client):
    """Verify that FastAPI endpoints restrict access without proper Zero-Trust headers."""
    response = client.post("/api/v1/analyze", json={"scenario": "normal", "vision_threshold": 0.4, "model_tier": "YOLOv8-Nano (Speed Edge)"})
    assert response.status_code == 401
    
    headers = {
        "x-session-auth": "TEST-SESSION-12345",
        "x-role-profile": "Operator"
    }
    response = client.post("/api/v1/analyze", json={"scenario": "normal", "vision_threshold": 0.4, "model_tier": "YOLOv8-Nano (Speed Edge)"}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "latency_ms" in data
    assert "telemetry" in data
    
    response_history = client.get("/api/v1/history", headers=headers)
    assert response_history.status_code in [200, 403]
    
    headers_admin = {
        "x-session-auth": "TEST-SESSION-12345",
        "x-role-profile": "Admin"
    }
    response_history_admin = client.get("/api/v1/history", headers=headers_admin)
    assert response_history_admin.status_code == 200
    assert "history" in response_history_admin.json()


def test_jwt_auth_flow(client):
    """Verify registration, login, and JWT-authenticated requests."""
    admin_login = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "Admin@AEGIS2024!"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    reg_response = client.post("/api/v1/auth/register", json={
        "username": "test_operator_99",
        "password": "securepassword",
        "role": "Operator"
    }, headers=admin_headers)
    assert reg_response.status_code in [200, 400, 409]
    
    login_response = client.post("/api/v1/auth/login", json={
        "username": "test_operator_99",
        "password": "securepassword"
    })
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    token = login_data["access_token"]
    
    jwt_headers = {"Authorization": f"Bearer {token}"}
    analyze_response = client.post("/api/v1/analyze", json={
        "scenario": "normal",
        "vision_threshold": 0.4,
        "model_tier": "YOLOv8-Nano (Speed Edge)",
        "location_name": "Times Square, NY",
        "latitude": 40.7580,
        "longitude": -73.9855,
        "operational_mode": "AI Automated Fusion"
    }, headers=jwt_headers)
    assert analyze_response.status_code == 200
    history_response = client.get("/api/v1/history", headers=jwt_headers)
    assert history_response.status_code in [200, 403]


def test_operational_modes(client):
    """Verify that operational mode parameters affect output states appropriately."""
    headers_admin = {
        "x-session-auth": "admin",
        "x-role-profile": "Admin"
    }
    
    lockdown_response = client.post("/api/v1/analyze", json={
        "scenario": "normal",
        "vision_threshold": 0.4,
        "model_tier": "YOLOv8-Nano (Speed Edge)",
        "operational_mode": "Security Lockdown"
    }, headers=headers_admin)
    assert lockdown_response.status_code == 200
    lockdown_data = lockdown_response.json()
    assert lockdown_data["fusion_layer"]["alert_status"] == "🔒 SECURITY LOCKDOWN (CRITICAL)"
    assert lockdown_data["fusion_layer"]["active_phase"] == "ALL RED (LOCKDOWN)"
    assert lockdown_data["fusion_layer"]["signal_timing_seconds"] == 0
    
    manual_response = client.post("/api/v1/analyze", json={
        "scenario": "normal",
        "vision_threshold": 0.4,
        "model_tier": "YOLOv8-Nano (Speed Edge)",
        "operational_mode": "Manual Override",
        "manual_active_phase": "ALL FLASHING YELLOW",
        "manual_signal_timing": 33
    }, headers=headers_admin)
    assert manual_response.status_code == 200
    manual_data = manual_response.json()
    assert manual_data["fusion_layer"]["alert_status"] == "🎛️ MANUAL CONTROL OVERRIDE"
    assert manual_data["fusion_layer"]["active_phase"] == "ALL FLASHING YELLOW"
    assert manual_data["fusion_layer"]["signal_timing_seconds"] == 33

    predictive_response = client.post("/api/v1/analyze", json={
        "scenario": "normal",
        "vision_threshold": 0.4,
        "model_tier": "YOLOv8-Nano (Speed Edge)",
        "operational_mode": "Predictive Optimization"
    }, headers=headers_admin)
    assert predictive_response.status_code == 200
    predictive_data = predictive_response.json()
    assert predictive_data["fusion_layer"]["alert_status"] == "🔮 PREDICTIVE OPTIMIZATION ACTIVE"
    assert predictive_data["fusion_layer"]["active_phase"] == "North-South Green (Predictive Shift)"
    assert predictive_data["fusion_layer"]["signal_timing_seconds"] == 40
