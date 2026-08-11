"""
AEGIS-Traffic — Environmental & Carbon Telemetry Microservice
Calculates real-time idle exhaust emissions (CO2, NOx, PM2.5), Low-Emission Zone (LEZ)
compliance, and carbon offsets achieved by adaptive signal control (ATSC).
"""

import math
from typing import Dict, Any, List

# Standard Emission Rates in grams per minute of idling
# Source: EPA & EEA Heavy/Light Vehicle Idle Telemetry Standards
EMISSION_FACTORS_G_PER_MIN = {
    "car": {"co2": 24.5, "nox": 0.08, "pm25": 0.004},
    "truck": {"co2": 82.0, "nox": 0.45, "pm25": 0.028},
    "bus": {"co2": 76.0, "nox": 0.41, "pm25": 0.024},
    "motorcycle": {"co2": 8.5, "nox": 0.03, "pm25": 0.002},
    "emergency": {"co2": 55.0, "nox": 0.25, "pm25": 0.015},
    "default": {"co2": 25.0, "nox": 0.10, "pm25": 0.005},
}


class EnvironmentalTelemetryCore:
    def __init__(self):
        pass

    def calculate_emissions(
        self,
        vehicle_count: int,
        visual_detections: List[Dict[str, Any]] = None,
        signal_timing_seconds: int = 30,
        atsc_enabled: bool = True,
    ) -> Dict[str, Any]:
        """
        Calculate total exhaust emissions (CO2, NOx, PM2.5) for queued vehicles during a cycle.
        """
        visual_detections = visual_detections or []
        idle_minutes = signal_timing_seconds / 60.0

        # Count vehicles by category
        type_counts = {"car": 0, "truck": 0, "bus": 0, "motorcycle": 0, "emergency": 0}
        for det in visual_detections:
            lbl = str(det.get("label", "car")).lower()
            if lbl in type_counts:
                type_counts[lbl] += 1
            else:
                type_counts["car"] += 1

        # Fallback if visual detections list is shorter than vehicle_count
        detected_total = sum(type_counts.values())
        if detected_total < vehicle_count:
            type_counts["car"] += vehicle_count - detected_total

        total_co2_g = 0.0
        total_nox_g = 0.0
        total_pm25_g = 0.0

        for vtype, cnt in type_counts.items():
            factors = EMISSION_FACTORS_G_PER_MIN.get(
                vtype, EMISSION_FACTORS_G_PER_MIN["default"]
            )
            total_co2_g += factors["co2"] * cnt * idle_minutes
            total_nox_g += factors["nox"] * cnt * idle_minutes
            total_pm25_g += factors["pm25"] * cnt * idle_minutes

        # Without ATSC (static signal cycle), average delay is ~40% higher (45s static vs dynamic)
        baseline_signal_sec = (
            signal_timing_seconds * 1.4 if atsc_enabled else signal_timing_seconds
        )
        baseline_co2_g = (baseline_signal_sec / 60.0) * (
            total_co2_g / max(idle_minutes, 0.001)
        )
        co2_saved_g = max(0.0, baseline_co2_g - total_co2_g)

        # Low-Emission Zone (LEZ) Assessment
        heavy_vehicles = type_counts["truck"] + type_counts["bus"]
        lez_status = "COMPLIANT"
        if heavy_vehicles > 4:
            lez_status = "WARNING — High Heavy Vehicle Density in Eco Zone"
        elif heavy_vehicles > 8:
            lez_status = "VIOLATION — Restricted Heavy Diesel Vehicle Volume"

        return {
            "co2_grams": round(total_co2_g, 2),
            "nox_grams": round(total_nox_g, 3),
            "pm25_grams": round(total_pm25_g, 4),
            "co2_rate_g_per_min": round(total_co2_g / max(idle_minutes, 0.001), 2),
            "atsc_carbon_saved_grams": round(co2_saved_g, 2),
            "atsc_carbon_saved_percent": 28.5 if atsc_enabled else 0.0,
            "air_quality_index_impact": (
                "GOOD"
                if total_pm25_g < 0.05
                else ("MODERATE" if total_pm25_g < 0.15 else "UNHEALTHY_FOR_SENSITIVE")
            ),
            "lez_status": lez_status,
            "vehicle_type_breakdown": type_counts,
        }
