# app/core/violation_module.py
"""
Traffic Violation Detection Module — Global Edition
=====================================================
Pipeline (spec §15):
    Signal state + vehicle position → Cross stop-line check → Violation record
    Lane assignment + vehicle path   → Wrong-lane check
    Vehicle speed + threshold        → Overspeed check
    Parking zone + stopped vehicle   → Illegal parking

Global support:
    Fine amounts are automatically converted to the jurisdiction's local
    currency using the geo_currency module.  Every violation record now
    carries `fine_local`, `fine_usd`, `currency_code`, `currency_symbol`.

In simulation mode violations are deterministically generated from the
scenario name + active signal phase so the API returns believable, varied
records without requiring live video frames.

Real-world upgrade path:
    Feed actual bounding boxes + tracking IDs from ByteTrack/DeepSORT into
    check_red_light_jump() and check_wrong_lane() with a virtual stop-line.
"""

import hashlib
from datetime import datetime, timedelta

from app.core.geo_currency import (
    _DEFAULT_COUNTRY,
    format_fine_with_usd,
    get_country_config,
    get_fine,
)

# --------------------------------------------------------------------------- #
#  Violation type catalogue                                                    #
# --------------------------------------------------------------------------- #

VIOLATION_TYPES = {
    "RED_LIGHT_JUMP": "🚦 Red Light Jump",
    "WRONG_LANE": "⬅️  Wrong Lane",
    "ILLEGAL_UTURN": "🔄 Illegal U-Turn",
    "OVERSPEEDING": "💨 Overspeeding",
    "NO_HELMET": "🪖 No Helmet (Motorcycle)",
    "ILLEGAL_PARKING": "🅿️  Illegal Parking",
    "WRONG_WAY": "⛔ Wrong Way Driving",
    # ── UCF Crime Dataset-driven violation types ──────────────────────────
    "ROAD_ACCIDENT": "🚗 Road Accident Detected",
    "ASSAULT_DETECTED": "🥊 Physical Assault / Fight",
    "EXPLOSION_HAZARD": "💥 Explosion / Arson Hazard",
    "CRIMINAL_ACTIVITY": "🔫 Criminal Activity Detected",
    "VANDALISM_DETECTED": "🧨 Vandalism Detected",
    "SUSPICIOUS_ARREST": "🚔 Arrest / Burglary Incident",
}

# Violations that are plausible per scenario
SCENARIO_VIOLATION_MAP: dict[str, list[str]] = {
    "normal": [],
    "congested": ["WRONG_LANE", "ILLEGAL_PARKING", "NO_HELMET"],
    "accident": ["RED_LIGHT_JUMP", "OVERSPEEDING", "WRONG_WAY"],
    "emergency": [],
    "tamper": [],
}

# UCF Crime label → AEGIS violation type mapping
UCF_LABEL_TO_VIOLATION: dict[str, str] = {
    "RoadAccidents": "ROAD_ACCIDENT",
    "Assault": "ASSAULT_DETECTED",
    "Abuse": "ASSAULT_DETECTED",
    "Fighting": "ASSAULT_DETECTED",
    "Explosion": "EXPLOSION_HAZARD",
    "Arson": "EXPLOSION_HAZARD",
    "Shooting": "CRIMINAL_ACTIVITY",
    "Robbery": "CRIMINAL_ACTIVITY",
    "Shoplifting": "CRIMINAL_ACTIVITY",
    "Stealing": "CRIMINAL_ACTIVITY",
    "Vandalism": "VANDALISM_DETECTED",
    "Arrest": "SUSPICIOUS_ARREST",
    "Burglary": "SUSPICIOUS_ARREST",
}

# Severity for UCF-driven violations (fine is sourced from geo_currency)
UCF_VIOLATION_SEVERITY: dict[str, str] = {
    "ROAD_ACCIDENT": "CRITICAL",
    "ASSAULT_DETECTED": "CRITICAL",
    "EXPLOSION_HAZARD": "CRITICAL",
    "CRIMINAL_ACTIVITY": "CRITICAL",
    "VANDALISM_DETECTED": "HIGH",
    "SUSPICIOUS_ARREST": "HIGH",
}


# --------------------------------------------------------------------------- #
#  Helpers                                                                     #
# --------------------------------------------------------------------------- #


def _stable_random(seed_str: str, lo: float, hi: float) -> float:
    """Returns a stable float in [lo, hi) based on an arbitrary seed string."""
    digest = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    return lo + (digest % 10000) / 10000 * (hi - lo)


def _make_vehicle_id(scenario: str, idx: int) -> str:
    return f"VH-{scenario.upper()[:3]}-{idx:03d}"


def _make_timestamp(offset_seconds: int = 0) -> str:
    ts = datetime.utcnow() - timedelta(seconds=offset_seconds)
    return ts.strftime("%Y-%m-%d %H:%M:%S UTC")


def _violation_id(violation_type: str, vehicle_id: str) -> str:
    raw = f"{violation_type}-{vehicle_id}-{datetime.utcnow().date()}"
    return "VIO-" + hashlib.sha1(raw.encode()).hexdigest()[:10].upper()


def _build_violation(
    violation_type: str,
    vehicle_id: str,
    plate: str,
    country_code: str,
    severity: str,
    extra_fields: dict,
    timestamp_offset: int = 0,
) -> dict:
    """
    Build a normalized violation record with global currency support.
    Merges fine info from geo_currency and extra context fields.
    """
    country_cfg = get_country_config(country_code)
    fine_amount = get_fine(violation_type, country_code)
    fine_info = format_fine_with_usd(fine_amount, country_code)

    return {
        "violation_id": _violation_id(violation_type, vehicle_id),
        "type": VIOLATION_TYPES.get(violation_type, violation_type),
        "type_code": violation_type,
        "vehicle_id": vehicle_id,
        "plate": plate,
        # ── Global currency fields ───────────────────────────────────────
        "fine_amount": fine_amount,
        "fine_local": fine_info["local_formatted"],
        "fine_usd": fine_info["usd_formatted"],
        "currency_code": fine_info["currency_code"],
        "currency_symbol": fine_info["currency_symbol"],
        "usd_equivalent": fine_info["usd_equivalent"],
        # ── Jurisdiction context ────────────────────────────────────────
        "country_code": country_code,
        "country_name": country_cfg["name"],
        "country_flag": country_cfg["flag"],
        "jurisdiction": f"{country_cfg['flag']} {country_cfg['name']}",
        # ── Metadata ────────────────────────────────────────────────────
        "severity": severity,
        "timestamp": _make_timestamp(timestamp_offset),
        "evidence_note": extra_fields.get("evidence_note", ""),
        "image_placeholder": extra_fields.get("image_placeholder", ""),
        **{
            k: v
            for k, v in extra_fields.items()
            if k not in ("evidence_note", "image_placeholder")
        },
    }


# --------------------------------------------------------------------------- #
#  Violation Detector                                                          #
# --------------------------------------------------------------------------- #


class ViolationDetector:
    """
    Detects traffic violations based on scenario state.

    Args:
        stop_line_y:      Y-pixel coordinate of the virtual stop line.
        lane_boundaries:  X-pixel boundaries of each lane.
        speed_limit_kmh:  Speed limit override. If None, uses country default.
        country_code:     ISO 3166-1 alpha-2 country code (from geo_currency).
    """

    def __init__(
        self,
        stop_line_y: int = 160,
        lane_boundaries: list[int] = None,
        speed_limit_kmh: float = None,
        country_code: str = _DEFAULT_COUNTRY,
    ):
        self.stop_line_y = stop_line_y
        self.lane_boundaries = lane_boundaries or [0, 220, 420, 640]
        self.country_code = country_code
        self.country_cfg = get_country_config(country_code)

        # Speed limit: caller override > country urban default
        if speed_limit_kmh is not None:
            self.speed_limit_kmh = speed_limit_kmh
        else:
            self.speed_limit_kmh = float(self.country_cfg.get("speed_limit_urban", 50))

    # ------------------------------------------------------------------ #
    #  Individual violation checkers                                      #
    # ------------------------------------------------------------------ #

    def check_red_light_jump(
        self, vehicle_id: str, plate: str, box: list[int], signal_phase: str, idx: int
    ) -> dict | None:
        is_red = "RED" in signal_phase.upper() and "GREEN" not in signal_phase.upper()
        if not is_red:
            return None
        if idx % 2 == 0:
            return None
        bottom_y = box[3] if len(box) >= 4 else 200
        if bottom_y < self.stop_line_y:
            return None

        return _build_violation(
            "RED_LIGHT_JUMP",
            vehicle_id,
            plate,
            self.country_code,
            "HIGH",
            {
                "signal_phase": signal_phase,
                "stop_line_y_px": self.stop_line_y,
                "vehicle_bottom_y": bottom_y,
                "evidence_note": "Vehicle crossed stop line while signal was RED.",
                "image_placeholder": f"evidence/{vehicle_id}_red_jump.jpg",
            },
            timestamp_offset=idx * 3,
        )

    def check_wrong_lane(
        self, vehicle_id: str, plate: str, box: list[int], expected_lane: int, idx: int
    ) -> dict | None:
        if len(box) < 4:
            return None
        center_x = (box[0] + box[2]) // 2
        actual_lane = 1
        for lane_num, boundary in enumerate(self.lane_boundaries[1:], start=1):
            if center_x < boundary:
                actual_lane = lane_num
                break
        if actual_lane == expected_lane:
            return None

        return _build_violation(
            "WRONG_LANE",
            vehicle_id,
            plate,
            self.country_code,
            "MEDIUM",
            {
                "expected_lane": f"Lane {expected_lane}",
                "actual_lane": f"Lane {actual_lane}",
                "center_x_px": center_x,
                "evidence_note": f"Vehicle detected in Lane {actual_lane}, expected Lane {expected_lane}.",
                "image_placeholder": f"evidence/{vehicle_id}_wrong_lane.jpg",
            },
            timestamp_offset=idx * 5,
        )

    def check_overspeeding(
        self, vehicle_id: str, plate: str, speed_kmh: float, idx: int
    ) -> dict | None:
        if speed_kmh <= self.speed_limit_kmh:
            return None
        excess = round(speed_kmh - self.speed_limit_kmh, 1)
        severity = "HIGH" if excess > 20 else "MEDIUM"

        return _build_violation(
            "OVERSPEEDING",
            vehicle_id,
            plate,
            self.country_code,
            severity,
            {
                "measured_speed_kmh": round(speed_kmh, 1),
                "speed_limit_kmh": self.speed_limit_kmh,
                "excess_kmh": excess,
                "evidence_note": (
                    f"Vehicle travelling at {speed_kmh:.1f} km/h "
                    f"in a {self.speed_limit_kmh} km/h zone."
                ),
                "image_placeholder": f"evidence/{vehicle_id}_overspeed.jpg",
            },
            timestamp_offset=idx * 2,
        )

    def check_no_helmet(
        self, vehicle_id: str, plate: str, label: str, idx: int
    ) -> dict | None:
        if label.lower() != "motorcycle":
            return None
        seed_val = _stable_random(f"helmet-{vehicle_id}", 0, 1)
        if seed_val > 0.4:
            return None

        return _build_violation(
            "NO_HELMET",
            vehicle_id,
            plate,
            self.country_code,
            "MEDIUM",
            {
                "evidence_note": "Motorcycle rider detected without helmet.",
                "image_placeholder": f"evidence/{vehicle_id}_no_helmet.jpg",
            },
            timestamp_offset=idx * 4,
        )

    # ------------------------------------------------------------------ #
    #  Main public method                                                  #
    # ------------------------------------------------------------------ #

    def detect_violations(
        self,
        detections: list[dict],
        scenario: str,
        signal_phase: str,
        avg_speed_kmh: float = 30.0,
        plate_pool: list[str] = None,
    ) -> dict:
        """
        Runs all applicable violation checks for the current scenario.

        Args:
            detections:    list of detection dicts (label, confidence, box)
            scenario:      one of normal/congested/accident/emergency/tamper
            signal_phase:  e.g. "ALL RED (CONTAINMENT)", "North-South Green"
            avg_speed_kmh: estimated average speed from fusion_core
            plate_pool:    country-specific plate strings from geo_currency

        Returns:
            {
              "violations": [...],
              "total_count": int,
              "summary": { type_code: count },
              "total_fines_local": int,
              "total_fine_amount": int,    # alias
              "currency_code": str,
              "currency_symbol": str,
              "country_code": str,
              "country_name": str,
              "country_flag": str,
              "speed_limit_kmh": float,
              "drive_side": str,
            }
        """

        # Country info for summary
        cc = self.country_code
        cfg = self.country_cfg
        sym = cfg["currency_symbol"]
        code = cfg["currency_code"]

        # Default plate pool if not provided
        if plate_pool is None:
            from app.core.geo_currency import get_plate_pool

            plate_pool = get_plate_pool(cc)

        def _get_plate(idx: int) -> str:
            return (
                plate_pool[idx % len(plate_pool)]
                if plate_pool
                else f"UNKNOWN-{idx:03d}"
            )

        applicable_types = SCENARIO_VIOLATION_MAP.get(scenario.lower(), [])
        violations: list[dict] = []
        vehicle_idx = 0

        for i, det in enumerate(detections):
            label = det.get("label", "").lower()
            if label in ["person", "camera_blocked_tamper"]:
                continue

            vehicle_idx += 1
            vehicle_id = _make_vehicle_id(scenario, vehicle_idx)
            plate = _get_plate(vehicle_idx)
            box = det.get("box", [0, 0, 200, 200])
            veh_speed = avg_speed_kmh + _stable_random(f"spd-{vehicle_id}", -5, 25)

            if "RED_LIGHT_JUMP" in applicable_types:
                v = self.check_red_light_jump(
                    vehicle_id, plate, box, signal_phase, vehicle_idx
                )
                if v:
                    violations.append(v)

            if "WRONG_LANE" in applicable_types:
                expected_lane = (vehicle_idx % 2) + 1
                v = self.check_wrong_lane(
                    vehicle_id, plate, box, expected_lane, vehicle_idx
                )
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
        total_fine_local = 0
        total_fine_usd = 0.0

        for v in violations:
            tc = v["type_code"]
            type_summary[tc] = type_summary.get(tc, 0) + 1
            total_fine_local += v.get("fine_amount", 0)
            total_fine_usd += v.get("usd_equivalent", 0.0)

        return {
            "violations": violations,
            "total_count": len(violations),
            "summary": type_summary,
            # ── Currency-aware totals ───────────────────────────────────
            "total_fines_local": total_fine_local,
            "total_fine_amount": total_fine_local,  # alias for backward compat
            "total_fines_usd": round(total_fine_usd, 2),
            "currency_code": code,
            "currency_symbol": sym,
            # ── Jurisdiction ────────────────────────────────────────────
            "country_code": cc,
            "country_name": cfg["name"],
            "country_flag": cfg["flag"],
            "jurisdiction": f"{cfg['flag']} {cfg['name']}",
            "speed_limit_kmh": self.speed_limit_kmh,
            "drive_side": cfg.get("drive_side", "right"),
            # ── Context ─────────────────────────────────────────────────
            "scenario": scenario.upper(),
            "signal_phase": signal_phase,
            "checked_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
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
        Converts a CrimeClassifier prediction into a violation record
        with global currency support.
        """
        label = crime_prediction.get("label", "NormalVideos")
        is_anomaly = crime_prediction.get("is_anomaly", False)
        confidence = crime_prediction.get("confidence", 0.0)
        crime_score = crime_prediction.get("crime_score", 0.0)

        if not is_anomaly or confidence < 0.3:
            return []

        violation_type = UCF_LABEL_TO_VIOLATION.get(label)
        if not violation_type:
            if label == "Anomalous" and is_anomaly:
                violation_type = "CRIMINAL_ACTIVITY"
            else:
                return []

        severity = UCF_VIOLATION_SEVERITY.get(violation_type, "HIGH")
        vid_id = f"UCF-{label.upper()[:4]}-{int(crime_score):03d}"

        return [
            _build_violation(
                violation_type,
                vid_id,
                "N/A (CCTV Frame)",
                self.country_code,
                severity,
                {
                    "ucf_label": label,
                    "crime_score": crime_score,
                    "classifier_confidence": round(confidence, 4),
                    "evidence_note": (
                        f"UCF Crime Classifier detected '{label}' activity with "
                        f"{confidence:.0%} confidence (crime_score={crime_score:.1f}). "
                        f"Location: {location_name}."
                    ),
                    "image_placeholder": f"evidence/ucf_{label.lower()}_{vid_id}.jpg",
                    "source": "UCF_CRIME_CLASSIFIER",
                },
            )
        ]
