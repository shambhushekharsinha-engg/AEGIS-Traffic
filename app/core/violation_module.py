# app/core/violation_module.py
"""
Traffic Violation Detection Module
===================================
Pipeline (spec §15):
    Signal state + vehicle position → Cross stop-line check → Violation record
    Lane assignment + vehicle path   → Wrong-lane check
    Vehicle speed + threshold        → Overspeed check
    Parking zone + stopped vehicle   → Illegal parking

In simulation mode (Vercel) violations are deterministically generated from
the scenario name + active signal phase so the API returns believable, varied
records without requiring live video frames.

Real-world upgrade path:
    Feed actual bounding boxes + tracking IDs from ByteTrack/DeepSORT into
    check_red_light_jump() and check_wrong_lane() with a virtual stop-line.
"""

import random
import hashlib
from datetime import datetime, timedelta


# --------------------------------------------------------------------------- #
#  Violation type catalogue                                                   #
# --------------------------------------------------------------------------- #

VIOLATION_TYPES = {
    "RED_LIGHT_JUMP":      "🚦 Red Light Jump",
    "WRONG_LANE":          "⬅️  Wrong Lane",
    "ILLEGAL_UTURN":       "🔄 Illegal U-Turn",
    "OVERSPEEDING":        "💨 Overspeeding",
    "NO_HELMET":           "🪖 No Helmet (Motorcycle)",
    "ILLEGAL_PARKING":     "🅿️  Illegal Parking",
    "WRONG_WAY":           "⛔ Wrong Way Driving",
    # ── UCF Crime Dataset-driven violation types ──────────────────────────
    "ROAD_ACCIDENT":       "🚗 Road Accident Detected",
    "ASSAULT_DETECTED":    "🥊 Physical Assault / Fight",
    "EXPLOSION_HAZARD":    "💥 Explosion / Arson Hazard",
    "CRIMINAL_ACTIVITY":   "🔫 Criminal Activity Detected",
    "VANDALISM_DETECTED":  "🧨 Vandalism Detected",
    "SUSPICIOUS_ARREST":   "🚔 Arrest / Burglary Incident",
}

# Violations that are plausible per scenario
SCENARIO_VIOLATION_MAP: dict[str, list[str]] = {
    "normal":     [],                                                         # Nominal — no violations
    "congested":  ["WRONG_LANE", "ILLEGAL_PARKING", "NO_HELMET"],
    "accident":   ["RED_LIGHT_JUMP", "OVERSPEEDING", "WRONG_WAY"],           # Pre-collision actions
    "emergency":  [],                                                         # Emergency override — bypass violations
    "tamper":     [],                                                         # Feed lost — unverifiable
}

# UCF Crime label → AEGIS violation type mapping
UCF_LABEL_TO_VIOLATION: dict[str, str] = {
    "RoadAccidents": "ROAD_ACCIDENT",
    "Assault":       "ASSAULT_DETECTED",
    "Abuse":         "ASSAULT_DETECTED",
    "Fighting":      "ASSAULT_DETECTED",
    "Explosion":     "EXPLOSION_HAZARD",
    "Arson":         "EXPLOSION_HAZARD",
    "Shooting":      "CRIMINAL_ACTIVITY",
    "Robbery":       "CRIMINAL_ACTIVITY",
    "Shoplifting":   "CRIMINAL_ACTIVITY",
    "Stealing":      "CRIMINAL_ACTIVITY",
    "Vandalism":     "VANDALISM_DETECTED",
    "Arrest":        "SUSPICIOUS_ARREST",
    "Burglary":      "SUSPICIOUS_ARREST",
}

# Fine amounts (INR) and severity for each UCF-driven violation
UCF_VIOLATION_DETAILS: dict[str, dict] = {
    "ROAD_ACCIDENT":      {"fine": 5000,  "severity": "CRITICAL"},
    "ASSAULT_DETECTED":   {"fine": 10000, "severity": "CRITICAL"},
    "EXPLOSION_HAZARD":   {"fine": 0,     "severity": "CRITICAL"},
    "CRIMINAL_ACTIVITY":  {"fine": 0,     "severity": "CRITICAL"},
    "VANDALISM_DETECTED": {"fine": 3000,  "severity": "HIGH"},
    "SUSPICIOUS_ARREST":  {"fine": 0,     "severity": "HIGH"},
}

# Plate pool (consistent within a session via seeded random)
_PLATE_POOL = [
    "MH12 AA1234", "DL05 ZX9876", "KA09 BB4321", "TN22 XY5678",
    "GJ01 CC2345", "UP32 YZ6789", "RJ14 DD3456", "WB28 AB7890",
    "AP07 EF8901", "TS11 GH0123", "MH43 IJ2345", "DL09 KL4567",
]


# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #

def _stable_random(seed_str: str, lo: float, hi: float) -> float:
    """Returns a stable float in [lo, hi) based on an arbitrary seed string."""
    digest = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    return lo + (digest % 10000) / 10000 * (hi - lo)


def _make_vehicle_id(scenario: str, idx: int) -> str:
    return f"VH-{scenario.upper()[:3]}-{idx:03d}"


def _make_plate(idx: int) -> str:
    return _PLATE_POOL[idx % len(_PLATE_POOL)]


def _make_timestamp(offset_seconds: int = 0) -> str:
    ts = datetime.utcnow() - timedelta(seconds=offset_seconds)
    return ts.strftime("%Y-%m-%d %H:%M:%S UTC")


def _violation_id(violation_type: str, vehicle_id: str) -> str:
    raw = f"{violation_type}-{vehicle_id}-{datetime.utcnow().date()}"
    return "VIO-" + hashlib.sha1(raw.encode()).hexdigest()[:10].upper()


# --------------------------------------------------------------------------- #
#  Violation Detector                                                          #
# --------------------------------------------------------------------------- #

class ViolationDetector:
    """
    Detects traffic violations based on scenario state.

    Attributes:
        stop_line_y (int): Y-pixel coordinate of the virtual stop line (default 160).
        lane_boundaries (list): X-pixel boundaries of each lane.
        speed_limit_kmh (float): Speed limit threshold for overspeeding check.
    """

    def __init__(
        self,
        stop_line_y: int = 160,
        lane_boundaries: list[int] = None,
        speed_limit_kmh: float = 50.0,
    ):
        self.stop_line_y      = stop_line_y
        self.lane_boundaries  = lane_boundaries or [0, 220, 420, 640]  # matches vision_module
        self.speed_limit_kmh  = speed_limit_kmh

    # ------------------------------------------------------------------ #
    #  Individual violation checkers                                      #
    # ------------------------------------------------------------------ #

    def check_red_light_jump(
        self, vehicle_id: str, plate: str, box: list[int],
        signal_phase: str, idx: int
    ) -> dict | None:
        """
        Returns a violation record if vehicle crossed the stop line on RED.
        Logic: If signal_phase contains 'RED' and vehicle's bottom y > stop_line_y
        """
        is_red = "RED" in signal_phase.upper() and "GREEN" not in signal_phase.upper()
        if not is_red:
            return None

        # Simulate: not every vehicle jumps red (only odd-indexed ones)
        if idx % 2 == 0:
            return None

        bottom_y = box[3] if len(box) >= 4 else 200
        if bottom_y < self.stop_line_y:
            return None     # Vehicle hasn't reached stop line yet

        return {
            "violation_id":     _violation_id("RED_LIGHT_JUMP", vehicle_id),
            "type":             VIOLATION_TYPES["RED_LIGHT_JUMP"],
            "type_code":        "RED_LIGHT_JUMP",
            "vehicle_id":       vehicle_id,
            "plate":            plate,
            "signal_phase":     signal_phase,
            "stop_line_y_px":   self.stop_line_y,
            "vehicle_bottom_y": bottom_y,
            "fine_amount_inr":  2000,
            "timestamp":        _make_timestamp(offset_seconds=idx * 3),
            "evidence_note":    "Vehicle crossed stop line while signal was RED.",
            "image_placeholder": f"evidence/{vehicle_id}_red_jump.jpg",
            "severity":         "HIGH",
        }

    def check_wrong_lane(
        self, vehicle_id: str, plate: str, box: list[int], expected_lane: int, idx: int
    ) -> dict | None:
        """
        Returns a violation if vehicle's center X falls outside its assigned lane.
        """
        if len(box) < 4:
            return None

        center_x = (box[0] + box[2]) // 2
        # Determine which lane the vehicle is actually in
        actual_lane = 1
        for lane_num, boundary in enumerate(self.lane_boundaries[1:], start=1):
            if center_x < boundary:
                actual_lane = lane_num
                break

        if actual_lane == expected_lane:
            return None

        return {
            "violation_id":     _violation_id("WRONG_LANE", vehicle_id),
            "type":             VIOLATION_TYPES["WRONG_LANE"],
            "type_code":        "WRONG_LANE",
            "vehicle_id":       vehicle_id,
            "plate":            plate,
            "expected_lane":    f"Lane {expected_lane}",
            "actual_lane":      f"Lane {actual_lane}",
            "center_x_px":      center_x,
            "fine_amount_inr":  500,
            "timestamp":        _make_timestamp(offset_seconds=idx * 5),
            "evidence_note":    f"Vehicle detected in Lane {actual_lane}, expected Lane {expected_lane}.",
            "image_placeholder": f"evidence/{vehicle_id}_wrong_lane.jpg",
            "severity":         "MEDIUM",
        }

    def check_overspeeding(
        self, vehicle_id: str, plate: str, speed_kmh: float, idx: int
    ) -> dict | None:
        """Returns a violation if estimated speed exceeds speed_limit_kmh."""
        if speed_kmh <= self.speed_limit_kmh:
            return None

        excess = round(speed_kmh - self.speed_limit_kmh, 1)
        severity = "HIGH" if excess > 20 else "MEDIUM"
        fine = 2000 if excess > 20 else 1000

        return {
            "violation_id":     _violation_id("OVERSPEEDING", vehicle_id),
            "type":             VIOLATION_TYPES["OVERSPEEDING"],
            "type_code":        "OVERSPEEDING",
            "vehicle_id":       vehicle_id,
            "plate":            plate,
            "measured_speed_kmh": round(speed_kmh, 1),
            "speed_limit_kmh":  self.speed_limit_kmh,
            "excess_kmh":       excess,
            "fine_amount_inr":  fine,
            "timestamp":        _make_timestamp(offset_seconds=idx * 2),
            "evidence_note":    f"Vehicle travelling at {speed_kmh:.1f} km/h in a {self.speed_limit_kmh} km/h zone.",
            "image_placeholder": f"evidence/{vehicle_id}_overspeed.jpg",
            "severity":         severity,
        }

    def check_no_helmet(
        self, vehicle_id: str, plate: str, label: str, idx: int
    ) -> dict | None:
        """Flags motorcycle riders without a helmet (simulated probabilistically)."""
        if label.lower() != "motorcycle":
            return None
        # 40% chance of no-helmet violation for motorcycles in congested scenes
        seed_val = _stable_random(f"helmet-{vehicle_id}", 0, 1)
        if seed_val > 0.4:
            return None

        return {
            "violation_id":     _violation_id("NO_HELMET", vehicle_id),
            "type":             VIOLATION_TYPES["NO_HELMET"],
            "type_code":        "NO_HELMET",
            "vehicle_id":       vehicle_id,
            "plate":            plate,
            "fine_amount_inr":  1000,
            "timestamp":        _make_timestamp(offset_seconds=idx * 4),
            "evidence_note":    "Motorcycle rider detected without helmet.",
            "image_placeholder": f"evidence/{vehicle_id}_no_helmet.jpg",
            "severity":         "MEDIUM",
        }

    # ------------------------------------------------------------------ #
    #  Main public method                                                  #
    # ------------------------------------------------------------------ #

    def detect_violations(
        self,
        detections: list[dict],
        scenario: str,
        signal_phase: str,
        avg_speed_kmh: float = 30.0,
    ) -> dict:
        """
        Runs all applicable violation checks for the current scenario.

        Args:
            detections:     list of detection dicts (label, confidence, box)
            scenario:       one of normal/congested/accident/emergency/tamper
            signal_phase:   e.g. "ALL RED (CONTAINMENT)", "North-South Green"
            avg_speed_kmh:  estimated average speed from fusion_core

        Returns:
            {
                "violations": [...],
                "total_count": int,
                "summary": { type_code: count },
                "total_fines_inr": int,
            }
        """
        applicable_types = SCENARIO_VIOLATION_MAP.get(scenario.lower(), [])
        violations: list[dict] = []
        vehicle_idx = 0

        for i, det in enumerate(detections):
            label = det.get("label", "").lower()
            if label in ["person", "camera_blocked_tamper"]:
                continue

            vehicle_idx += 1
            vehicle_id = _make_vehicle_id(scenario, vehicle_idx)
            plate      = _make_plate(vehicle_idx)
            box        = det.get("box", [0, 0, 200, 200])

            # Vary speed per vehicle slightly
            veh_speed = avg_speed_kmh + _stable_random(f"spd-{vehicle_id}", -5, 25)

            if "RED_LIGHT_JUMP" in applicable_types:
                v = self.check_red_light_jump(vehicle_id, plate, box, signal_phase, vehicle_idx)
                if v:
                    violations.append(v)

            if "WRONG_LANE" in applicable_types:
                expected_lane = (vehicle_idx % 2) + 1
                v = self.check_wrong_lane(vehicle_id, plate, box, expected_lane, vehicle_idx)
                if v:
                    violations.append(v)

            if "OVERSPEEDING" in applicable_types:
                v = self.check_overspeeding(vehicle_id, plate, veh_speed, vehicle_idx)
                if v:
                    violations.append(v)

            if "NO_HELMET" in applicable_types:
                v = self.check_no_helmet(vehicle_id, plate, label, vehicle_idx)
                if v:
                    violations.append(v)

        # Summary
        type_summary: dict[str, int] = {}
        total_fines = 0
        for v in violations:
            tc = v["type_code"]
            type_summary[tc] = type_summary.get(tc, 0) + 1
            total_fines += v.get("fine_amount_inr", 0)

        return {
            "violations":      violations,
            "total_count":     len(violations),
            "summary":         type_summary,
            "total_fines_inr": total_fines,
            "scenario":        scenario.upper(),
            "signal_phase":    signal_phase,
            "checked_at":      datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        }

    # ------------------------------------------------------------------ #
    #  UCF Crime-driven violation injection                                #
    # ------------------------------------------------------------------ #

    def detect_crime_violations(
        self,
        crime_prediction: dict,
        location_name: str = "Intersection",
    ) -> list[dict]:
        """
        Converts a CrimeClassifier prediction into a violation record.

        Args:
            crime_prediction:  dict from CrimeClassifier.predict_frame()
            location_name:     Human-readable location string.

        Returns:
            list of violation dicts (empty if no anomaly detected).
        """
        violations: list[dict] = []

        label      = crime_prediction.get("label", "NormalVideos")
        is_anomaly = crime_prediction.get("is_anomaly", False)
        confidence = crime_prediction.get("confidence", 0.0)
        crime_score = crime_prediction.get("crime_score", 0.0)
        severity   = crime_prediction.get("severity", "NONE")

        # Only create violations for anomalous predictions with reasonable confidence
        if not is_anomaly or confidence < 0.3:
            return violations

        violation_type = UCF_LABEL_TO_VIOLATION.get(label)
        if not violation_type:
            # Binary mode: "Anomalous" label → generic criminal activity
            if label == "Anomalous" and is_anomaly:
                violation_type = "CRIMINAL_ACTIVITY"
            else:
                return violations

        details = UCF_VIOLATION_DETAILS.get(violation_type, {"fine": 0, "severity": "HIGH"})
        vid_id  = f"UCF-{label.upper()[:4]}-{int(crime_score):03d}"

        violations.append({
            "violation_id":       _violation_id(violation_type, vid_id),
            "type":               VIOLATION_TYPES[violation_type],
            "type_code":          violation_type,
            "vehicle_id":         vid_id,
            "plate":              "N/A (CCTV Frame)",
            "ucf_label":          label,
            "crime_score":        crime_score,
            "classifier_confidence": round(confidence, 4),
            "fine_amount_inr":    details["fine"],
            "timestamp":          _make_timestamp(0),
            "evidence_note":      (
                f"UCF Crime Classifier detected '{label}' activity with "
                f"{confidence:.0%} confidence (crime_score={crime_score:.1f}). "
                f"Location: {location_name}."
            ),
            "image_placeholder":  f"evidence/ucf_{label.lower()}_{vid_id}.jpg",
            "severity":           details["severity"],
            "source":             "UCF_CRIME_CLASSIFIER",
        })

        return violations
