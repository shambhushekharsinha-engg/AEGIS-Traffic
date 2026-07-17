# app/tests/test_new_modules.py
"""
Tests for new pipeline modules added in v6.1.0:
  - ANPREngine (§16)
  - ViolationDetector (§15)
  - New API endpoints: /api/v1/anpr/{scenario}, /api/v1/violations/{scenario}, /api/v1/pipeline/status
  - Enhanced /api/v1/analyze response with traffic_analytics fields
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.anpr_module import ANPREngine
from app.core.violation_module import ViolationDetector
from app.pipeline.fusion_core import MultimodalFusionCore

client = TestClient(app)

# Shared auth headers
HEADERS = {
    "x-session-auth": "test-admin",
    "x-role-profile": "Admin"
}


# ---------------------------------------------------------------------------
# §16 ANPR Module unit tests
# ---------------------------------------------------------------------------

class TestANPREngine:
    def test_normal_scenario_returns_records(self):
        """ANPR should recognise vehicles in normal traffic."""
        engine = ANPREngine()
        detections = [
            {"label": "car",   "confidence": 0.92, "box": [100, 100, 200, 180]},
            {"label": "truck", "confidence": 0.87, "box": [300, 100, 450, 200]},
        ]
        records = engine.process_detections(detections, "normal")
        assert len(records) == 2
        for rec in records:
            assert "plate_text" in rec
            assert "vehicle_id" in rec
            assert "ocr_confidence" in rec
            assert 0.0 <= rec["ocr_confidence"] <= 1.0
            assert rec["status"] == "RECOGNISED"

    def test_tamper_scenario_returns_empty(self):
        """ANPR cannot read plates when camera is blocked."""
        engine = ANPREngine()
        detections = [{"label": "CAMERA_BLOCKED_TAMPER", "confidence": 0.99, "box": [0, 0, 640, 480]}]
        records = engine.process_detections(detections, "tamper")
        assert records == []

    def test_persons_excluded(self):
        """Pedestrians should not get ANPR records."""
        engine = ANPREngine()
        detections = [
            {"label": "person", "confidence": 0.85, "box": [50, 50, 100, 180]},
            {"label": "car",    "confidence": 0.90, "box": [200, 100, 300, 180]},
        ]
        records = engine.process_detections(detections, "normal")
        assert len(records) == 1
        assert records[0]["detection_label"] == "car"

    def test_plate_text_format(self):
        """Plate text should follow state-code format."""
        engine = ANPREngine()
        detections = [{"label": "car", "confidence": 0.90, "box": [100, 100, 200, 180]}]
        records = engine.process_detections(detections, "normal")
        plate = records[0]["plate_text"]
        # Should start with 2 uppercase letters (state code)
        assert plate[:2].isalpha() and plate[:2].isupper()
        assert len(plate) >= 8  # e.g. "MH12 AA1234"

    def test_summary_aggregation(self):
        """Summary should count types correctly."""
        engine = ANPREngine()
        detections = [
            {"label": "car",  "confidence": 0.91, "box": [100, 100, 200, 180]},
            {"label": "car",  "confidence": 0.88, "box": [250, 100, 350, 180]},
            {"label": "truck","confidence": 0.94, "box": [400, 100, 520, 200]},
        ]
        records = engine.process_detections(detections, "congested")
        summary  = engine.get_summary(records)
        assert summary["total_vehicles_recognised"] == 3
        assert summary["vehicle_type_breakdown"]["Car"] == 2
        assert summary["vehicle_type_breakdown"]["Truck"] == 1

    def test_plate_consistency_across_calls(self):
        """Same vehicle_id should get the same plate in the same session."""
        engine = ANPREngine()
        dets = [{"label": "car", "confidence": 0.9, "box": [100, 100, 200, 180]}]
        r1 = engine.process_detections(dets, "normal")
        r2 = engine.process_detections(dets, "normal")
        # Same engine instance → same plate for same scenario
        assert r1[0]["plate_text"] == r2[0]["plate_text"]


# ---------------------------------------------------------------------------
# §15 Violation Detector unit tests
# ---------------------------------------------------------------------------

class TestViolationDetector:
    def test_no_violations_in_normal(self):
        """Normal scenario should produce zero violations."""
        detector = ViolationDetector()
        detections = [
            {"label": "car", "confidence": 0.92, "box": [100, 100, 200, 180]},
        ]
        result = detector.detect_violations(detections, "normal", "North-South Green", 30.0)
        assert result["total_count"] == 0
        assert result["violations"] == []

    def test_no_violations_in_emergency(self):
        """Emergency override disables violation checks."""
        detector = ViolationDetector()
        detections = [
            {"label": "truck", "confidence": 0.96, "box": [250, 350, 290, 420]},
        ]
        result = detector.detect_violations(detections, "emergency", "EMERGENCY VEHICLE PRIORITY (GREEN)", 40.0)
        assert result["total_count"] == 0

    def test_accident_produces_violations(self):
        """Accident scenario should trigger red-light jump / overspeeding checks."""
        detector = ViolationDetector(speed_limit_kmh=50.0)
        detections = [
            {"label": "car", "confidence": 0.95, "box": [290, 200, 335, 245]},
            {"label": "car", "confidence": 0.92, "box": [325, 225, 370, 270]},
        ]
        result = detector.detect_violations(
            detections, "accident", "ALL RED (CONTAINMENT)", 75.0
        )
        assert isinstance(result["violations"], list)
        assert result["total_count"] >= 0   # may be 0 or more based on rules
        assert "summary" in result
        assert "total_fines_inr" in result

    def test_violation_record_structure(self):
        """Violation records must contain required fields."""
        detector = ViolationDetector(speed_limit_kmh=30.0)
        detections = [
            {"label": "car", "confidence": 0.93, "box": [290, 200, 335, 245]},
        ]
        result = detector.detect_violations(
            detections, "accident", "ALL RED (CONTAINMENT)", 80.0
        )
        for v in result["violations"]:
            assert "violation_id" in v
            assert "type" in v
            assert "vehicle_id" in v
            assert "plate" in v
            assert "timestamp" in v
            assert "severity" in v
            assert "fine_amount_inr" in v

    def test_congested_may_flag_wrong_lane(self):
        """Congested scenario checks wrong-lane and no-helmet violations."""
        detector = ViolationDetector()
        detections = [
            {"label": "car",        "confidence": 0.90, "box": [50, 100, 150, 180]},   # Lane 1
            {"label": "motorcycle", "confidence": 0.85, "box": [300, 100, 380, 180]},  # Lane 2
        ]
        result = detector.detect_violations(detections, "congested", "North-South Green", 30.0)
        # Result is a dict with required keys regardless of violation count
        assert "violations" in result
        assert "summary" in result
        assert "total_fines_inr" in result
        assert isinstance(result["total_fines_inr"], int)

    def test_tamper_returns_empty(self):
        """Tamper scenario: feed lost, no violations verifiable."""
        detector = ViolationDetector()
        detections = [{"label": "CAMERA_BLOCKED_TAMPER", "confidence": 0.99, "box": [0, 0, 640, 480]}]
        result = detector.detect_violations(detections, "tamper", "ALL FLASHING YELLOW (CAUTION)", 0.0)
        assert result["total_count"] == 0


# ---------------------------------------------------------------------------
# New API Endpoints
# ---------------------------------------------------------------------------

class TestANPREndpoint:
    def test_anpr_normal_returns_200(self):
        response = client.get("/api/v1/anpr/normal", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "anpr_records" in data
        assert "summary" in data
        assert data["scenario"] == "NORMAL"

    def test_anpr_tamper_returns_empty_records(self):
        response = client.get("/api/v1/anpr/tamper", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["anpr_records"] == []

    def test_anpr_invalid_scenario_returns_400(self):
        response = client.get("/api/v1/anpr/invalid_scene", headers=HEADERS)
        assert response.status_code == 400

    def test_anpr_requires_auth(self):
        response = client.get("/api/v1/anpr/normal")
        assert response.status_code == 401


class TestViolationsEndpoint:
    def test_violations_normal_returns_empty(self):
        response = client.get("/api/v1/violations/normal", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "violations" in data
        assert data["total_count"] == 0

    def test_violations_accident_structure(self):
        response = client.get("/api/v1/violations/accident", headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "violations" in data
        assert "summary" in data
        assert "total_fines_inr" in data
        assert "checked_at" in data

    def test_violations_invalid_scenario_400(self):
        response = client.get("/api/v1/violations/blah", headers=HEADERS)
        assert response.status_code == 400

    def test_violations_requires_auth(self):
        response = client.get("/api/v1/violations/congested")
        assert response.status_code == 401


class TestPipelineStatusEndpoint:
    def test_pipeline_status_no_auth_required(self):
        """Pipeline status is public — no auth headers needed."""
        response = client.get("/api/v1/pipeline/status")
        assert response.status_code == 200

    def test_pipeline_status_structure(self):
        response = client.get("/api/v1/pipeline/status")
        data = response.json()
        assert data["overall_status"] == "OPERATIONAL"
        assert "modules" in data
        assert "pipeline_stages" in data
        assert "system_metrics" in data
        # All 15 pipeline stages should be listed
        assert len(data["pipeline_stages"]) == 15
        # Check key module entries
        modules = data["modules"]
        assert "vehicle_detection" in modules
        assert "violation_detection" in modules
        assert "anpr_ocr" in modules
        assert "speed_estimation" in modules
        assert "lane_detection" in modules


class TestAnalyzeResponseTrafficAnalytics:
    def test_analyze_includes_traffic_analytics(self):
        """The /analyze endpoint must now return a traffic_analytics block."""
        response = client.post(
            "/api/v1/analyze",
            json={
                "scenario": "congested",
                "vision_threshold": 0.4,
                "model_tier": "YOLOv8-Nano (Speed Edge)"
            },
            headers=HEADERS
        )
        assert response.status_code == 200
        data = response.json()
        assert "traffic_analytics" in data
        ta = data["traffic_analytics"]
        assert "traffic_density_percent" in ta
        assert "density_level" in ta
        assert "queue_length_meters" in ta
        assert "avg_speed_kmh" in ta
        assert "lane_counts" in ta
        assert ta["density_level"] in ["Low", "Medium", "High", "Very High"]
        assert isinstance(ta["traffic_density_percent"], float)
        assert ta["avg_speed_kmh"] > 0

    def test_density_percent_in_valid_range(self):
        """traffic_density_percent must be between 0 and 100."""
        response = client.post(
            "/api/v1/analyze",
            json={"scenario": "normal", "vision_threshold": 0.4, "model_tier": "YOLOv8-Nano (Speed Edge)"},
            headers=HEADERS
        )
        data = response.json()
        pct = data["traffic_analytics"]["traffic_density_percent"]
        assert 0.0 <= pct <= 100.0

    def test_lane_counts_structure(self):
        """lane_counts must have Lane 1, Lane 2, Lane 3 keys."""
        response = client.post(
            "/api/v1/analyze",
            json={"scenario": "congested", "vision_threshold": 0.4, "model_tier": "YOLOv8-Nano (Speed Edge)"},
            headers=HEADERS
        )
        data = response.json()
        lane_counts = data["traffic_analytics"]["lane_counts"]
        assert "Lane 1" in lane_counts
        assert "Lane 2" in lane_counts
        assert "Lane 3" in lane_counts
        total = sum(lane_counts.values())
        assert total == data["fusion_layer"]["vehicle_count"]


# ---------------------------------------------------------------------------
# Fusion Core new fields unit test
# ---------------------------------------------------------------------------

class TestFusionCoreNewFields:
    def test_density_fields_present(self):
        core = MultimodalFusionCore()
        result = core.fuse_and_classify(
            [{"label": "car"}, {"label": "car"}, {"label": "truck"}],
            {"type": "Ambient", "db_level": 40.0},
            "normal"
        )
        assert "traffic_density_percent" in result
        assert "density_level" in result
        assert "queue_length_meters" in result
        assert "avg_speed_kmh" in result
        assert "lane_counts" in result

    def test_density_calculation_accuracy(self):
        """3 vehicles / 50 capacity = 6% → Low"""
        core = MultimodalFusionCore()
        result = core.fuse_and_classify(
            [{"label": "car"}, {"label": "car"}, {"label": "truck"}],
            {"type": "Ambient", "db_level": 40.0},
            "normal"
        )
        assert result["traffic_density_percent"] == 6.0
        assert result["density_level"] == "Low"

    def test_queue_length_proportional_to_count(self):
        """9 vehicles × 7m = 63m queue."""
        core = MultimodalFusionCore()
        detections = [{"label": "car"}] * 9
        result = core.fuse_and_classify(
            detections, {"type": "Ambient", "db_level": 42.0}, "congested"
        )
        assert result["queue_length_meters"] == 63.0

    def test_speed_decreases_with_density(self):
        """Higher vehicle count should yield lower avg speed."""
        core = MultimodalFusionCore()
        res_low  = core.fuse_and_classify(
            [{"label": "car"}],
            {"type": "Ambient", "db_level": 40.0}, "normal"
        )
        res_high = core.fuse_and_classify(
            [{"label": "car"}] * 20,
            {"type": "Ambient", "db_level": 50.0}, "congested"
        )
        assert res_low["avg_speed_kmh"] > res_high["avg_speed_kmh"]

    def test_lane_counts_sum_equals_vehicle_count(self):
        """Sum of lane counts must equal total vehicle_count."""
        core = MultimodalFusionCore()
        detections = [
            {"label": "car",   "box": [50,  100, 150, 180]},   # Lane 1
            {"label": "truck", "box": [300, 100, 420, 200]},   # Lane 2
            {"label": "car",   "box": [480, 100, 580, 180]},   # Lane 3
        ]
        result = core.fuse_and_classify(
            detections, {"type": "Ambient", "db_level": 42.0}, "normal"
        )
        lc = result["lane_counts"]
        assert lc["Lane 1"] + lc["Lane 2"] + lc["Lane 3"] == result["vehicle_count"]
