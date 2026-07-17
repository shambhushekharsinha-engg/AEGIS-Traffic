# app/core/anpr_module.py
"""
ANPR (Automatic Number Plate Recognition) Module
=================================================
Pipeline:
  Vehicle bounding boxes → Plate region crop (simulated) → OCR (simulated) → Plate text

For Vercel deployment this module operates in pure-simulation mode (no EasyOCR/Tesseract
dependency) to keep the package footprint minimal. When run locally with full deps the
OCR step can be swapped in at `_run_ocr`.

Plate format used: <2 letters><2 digits><space><3 letters>
  e.g.  AB12 XYZ  →  common Indian RTO style
"""

import random
import string
import time
from datetime import datetime


# --------------------------------------------------------------------------- #
#  Internal helpers                                                            #
# --------------------------------------------------------------------------- #

_PLATE_CACHE: dict[str, list[dict]] = {}   # cache per scenario for session consistency

def _random_plate() -> str:
    """Generate a plausible synthetic number plate string."""
    state_codes = ["MH", "DL", "KA", "TN", "GJ", "UP", "RJ", "WB", "AP", "TS"]
    state = random.choice(state_codes)
    district = str(random.randint(1, 99)).zfill(2)
    series = random.choice(["AA", "AB", "BC", "CA", "DA", "XY", "ZA"])
    num = str(random.randint(1000, 9999))
    return f"{state}{district} {series}{num}"


def _vehicle_type_from_label(label: str) -> str:
    mapping = {
        "car": "Car",
        "truck": "Truck",
        "bus": "Bus",
        "motorcycle": "Motorcycle",
        "bicycle": "Bicycle",
        "person": "Pedestrian",
    }
    return mapping.get(label.lower(), "Unknown")


# --------------------------------------------------------------------------- #
#  Main ANPR Engine                                                            #
# --------------------------------------------------------------------------- #

class ANPREngine:
    """
    Simulated ANPR pipeline.

    Steps replicated in simulation:
        1. Receive vehicle detections (label + confidence + bounding box)
        2. For each vehicle, "crop" the plate region (synthetic)
        3. Apply OCR → return plate text + confidence
        4. Return structured records for storage / display

    Real-world upgrade path:
        Replace `_run_ocr()` with EasyOCR or PaddleOCR call on actual
        plate crops from video frames.
    """

    # Plates that should persist per session/scenario so consecutive calls
    # to the same scenario return consistent plate numbers (simulates stable tracking)
    def __init__(self):
        random.seed(42)                          # reproducible during server lifetime
        self._session_plates: dict[str, str] = {}  # vehicle_id → plate

    # ------------------------------------------------------------------ #
    #  Private                                                            #
    # ------------------------------------------------------------------ #

    def _run_ocr(self, vehicle_id: str) -> dict:
        """
        Simulates the OCR step.  In a real pipeline this would receive a cropped
        plate image (numpy array) and return EasyOCR/Tesseract output.
        """
        if vehicle_id not in self._session_plates:
            self._session_plates[vehicle_id] = _random_plate()

        plate_text = self._session_plates[vehicle_id]
        # Simulate OCR confidence: 75–98%
        ocr_confidence = round(random.uniform(0.75, 0.98), 2)
        return {"plate_text": plate_text, "ocr_confidence": ocr_confidence}

    def _plate_crop_simulated(self, detection: dict, index: int) -> dict:
        """
        Simulate cropping the license plate region from a bounding box.
        Returns synthetic crop metadata (in real use: image bytes).
        """
        box = detection.get("box", [0, 0, 100, 60])
        # Plate typically occupies bottom-third of vehicle bounding box
        x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
        h = y2 - y1
        plate_region = {
            "x1": x1 + 5,
            "y1": y2 - int(h * 0.25),
            "x2": x2 - 5,
            "y2": y2,
        }
        return plate_region

    # ------------------------------------------------------------------ #
    #  Public API                                                         #
    # ------------------------------------------------------------------ #

    def process_detections(self, detections: list[dict], scenario: str) -> list[dict]:
        """
        Main entry point.

        Args:
            detections: list of detection dicts from VisionEngine.
                        Each dict has keys: label, confidence, box (optional)
            scenario:   scenario name string (normal/congested/emergency/accident/tamper)

        Returns:
            list of ANPR records, one per recognised vehicle (non-persons)
        """
        if scenario == "tamper":
            return []   # No plate data recoverable when camera is obstructed

        results = []
        vehicle_idx = 0

        for i, det in enumerate(detections):
            label = det.get("label", "").lower()
            if label in ["person", "camera_blocked_tamper"]:
                continue          # No plate on pedestrians or tamper events

            vehicle_idx += 1
            vehicle_id = f"VH-{scenario.upper()[:3]}-{vehicle_idx:03d}"

            crop_info   = self._plate_crop_simulated(det, i)
            ocr_result  = self._run_ocr(vehicle_id)

            record = {
                "vehicle_id":      vehicle_id,
                "vehicle_type":    _vehicle_type_from_label(label),
                "detection_label": label,
                "detection_conf":  det.get("confidence", 0.0),
                "plate_region":    crop_info,
                "plate_text":      ocr_result["plate_text"],
                "ocr_confidence":  ocr_result["ocr_confidence"],
                "timestamp":       datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "scenario":        scenario.upper(),
                "status":          "RECOGNISED",
            }
            results.append(record)

        return results

    def get_summary(self, records: list[dict]) -> dict:
        """Returns aggregate statistics for a set of ANPR records."""
        if not records:
            return {
                "total_vehicles_recognised": 0,
                "avg_ocr_confidence": 0.0,
                "vehicle_type_breakdown": {},
            }

        type_counts: dict[str, int] = {}
        conf_total = 0.0
        for r in records:
            vt = r["vehicle_type"]
            type_counts[vt] = type_counts.get(vt, 0) + 1
            conf_total += r["ocr_confidence"]

        return {
            "total_vehicles_recognised": len(records),
            "avg_ocr_confidence":        round(conf_total / len(records), 3),
            "vehicle_type_breakdown":    type_counts,
        }
