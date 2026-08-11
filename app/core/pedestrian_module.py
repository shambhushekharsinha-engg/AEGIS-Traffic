"""
AEGIS-Traffic — Vulnerable Road User (VRU) & Pedestrian Crosswalk Guardian
Detects pedestrians, wheelchairs, strollers, and cyclists in crosswalk zones and
calculates dynamic WALK phase extensions for municipal traffic controllers.
"""

from typing import Any, Dict, List


class PedestrianSafetyCore:
    def __init__(self):
        pass

    def evaluate_crosswalk_safety(
        self,
        visual_detections: List[Dict[str, Any]] = None,
        base_walk_seconds: int = 15,
    ) -> Dict[str, Any]:
        """
        Evaluate crosswalk occupancy and calculate WALK signal phase extension.
        """
        visual_detections = visual_detections or []

        pedestrian_count = 0
        vru_special_count = 0  # wheelchairs, strollers, elderly assistance

        for det in visual_detections:
            lbl = str(det.get("label", "")).lower()
            if "person" in lbl or "pedestrian" in lbl:
                pedestrian_count += 1
            elif any(
                k in lbl for k in ["wheelchair", "stroller", "bicycle", "cyclist"]
            ):
                vru_special_count += 1

        # Standard walking speed assumption = 1.2 m/s across 14m crosswalk
        # Vulnerable users assumption = 0.7 m/s (requires ~20s clear window)
        extension_seconds = 0
        if vru_special_count > 0:
            extension_seconds = 10
            status_msg = "VRU_ASSIST_EXTENSION_ACTIVE (+10s)"
        elif pedestrian_count > 5:
            extension_seconds = 6
            status_msg = "HIGH_DENSITY_PEDESTRIAN_EXTENSION (+6s)"
        elif pedestrian_count > 0:
            extension_seconds = 3
            status_msg = "STANDARD_PEDESTRIAN_EXTENSION (+3s)"
        else:
            status_msg = "CROSSWALK_CLEAR"

        recommended_walk_time = base_walk_seconds + extension_seconds

        return {
            "pedestrians_detected": pedestrian_count,
            "vru_special_needs_detected": vru_special_count,
            "crosswalk_status": status_msg,
            "base_walk_seconds": base_walk_seconds,
            "walk_extension_seconds": extension_seconds,
            "recommended_walk_seconds": recommended_walk_time,
            "blind_spot_warning_active": vru_special_count > 0 or pedestrian_count > 3,
        }
