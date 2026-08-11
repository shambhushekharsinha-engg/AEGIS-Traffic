# app/core/anpr_module.py
"""
ANPR (Automatic Number Plate Recognition) Module — Global Edition
==================================================================
Pipeline:
  Vehicle bounding boxes → Plate region crop (simulated) → OCR (simulated) → Plate text

Global support:
  Plate formats are now derived from the geo_currency module so that plates
  returned by the API match the number plate standard of the detected country.

  Examples:
    India   →  MH12 AA1234   (State-District-Series-Number)
    UK      →  AB12 CDE      (DVLA format)
    USA     →  ABC 1234      (generic state format)
    Japan   →  品川 300 あ 1234
    UAE     →  Dubai A 12345
    Germany →  B AB 1234

For Vercel deployment this module operates in pure-simulation mode (no
EasyOCR/Tesseract dependency) to keep the package footprint minimal.
Real-world upgrade: replace `_run_ocr()` with EasyOCR/PaddleOCR on actual
plate crops from video frames.
"""

import hashlib
import random
from datetime import datetime

from app.core.geo_currency import _DEFAULT_COUNTRY, get_country_config, get_plate_pool

# --------------------------------------------------------------------------- #
#  Internal helpers                                                            #
# --------------------------------------------------------------------------- #

_SESSION_PLATES: dict[str, str] = {}  # vehicle_id → plate (stable per server lifetime)


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
    Simulated ANPR pipeline with global plate format support.

    Steps replicated in simulation:
        1. Receive vehicle detections (label + confidence + bounding box)
        2. For each vehicle, "crop" the plate region (synthetic)
        3. Apply OCR → return plate text in country-specific format
        4. Return structured records for storage / display

    Real-world upgrade path:
        Replace `_run_ocr()` with EasyOCR or PaddleOCR call on actual
        plate crops from video frames.
    """

    def __init__(self, country_code: str = _DEFAULT_COUNTRY):
        """
        Args:
            country_code: ISO 3166-1 alpha-2 code used to generate realistic
                          plate strings (e.g. 'IN', 'US', 'GB', 'JP', 'AE').
        """
        self.country_code = country_code
        self.country_cfg = get_country_config(country_code)
        # Pre-generate a pool of country-specific plates
        # Seed with country so pool is stable per country (not random each call)
        random.seed(hash(country_code) % (2**31))
        self._plate_pool = get_plate_pool(country_code)
        self._session_plates: dict[str, str] = {}  # vehicle_id → plate

    # ------------------------------------------------------------------ #
    #  Private                                                            #
    # ------------------------------------------------------------------ #

    def _run_ocr(self, vehicle_id: str) -> dict:
        """
        Simulates the OCR step.  In a real pipeline this would receive a
        cropped plate image (numpy array) and return EasyOCR/Tesseract output.
        """
        if vehicle_id not in self._session_plates:
            # Deterministic plate selection based on vehicle_id hash
            idx = int(hashlib.md5(vehicle_id.encode()).hexdigest(), 16)
            self._session_plates[vehicle_id] = self._plate_pool[
                idx % len(self._plate_pool)
            ]

        plate_text = self._session_plates[vehicle_id]
        ocr_confidence = round(
            0.75
            + (int(hashlib.md5(plate_text.encode()).hexdigest(), 16) % 2300) / 10000,
            2,
        )  # Deterministic 0.75–0.98
        return {"plate_text": plate_text, "ocr_confidence": ocr_confidence}

    def _plate_crop_simulated(self, detection: dict, index: int) -> dict:
        """
        Simulate cropping the license plate region from a bounding box.
        Returns synthetic crop metadata.
        """
        box = detection.get("box", [0, 0, 100, 60])
        x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
        h = y2 - y1
        return {
            "x1": x1 + 5,
            "y1": y2 - int(h * 0.25),
            "x2": x2 - 5,
            "y2": y2,
        }

    # ------------------------------------------------------------------ #
    #  Public API                                                         #
    # ------------------------------------------------------------------ #

    def process_detections(
        self,
        detections: list[dict],
        scenario: str,
        country_code: str | None = None,
    ) -> list[dict]:
        """
        Main entry point.

        Args:
            detections:   list of detection dicts from VisionEngine.
                          Each dict has keys: label, confidence, box (optional)
            scenario:     scenario name string (normal/congested/emergency/accident/tamper)
            country_code: override the engine's country_code for this call.

        Returns:
            list of ANPR records, one per recognised vehicle (non-persons).
            Each record now includes:
              - plate          → country-specific plate string
              - country_code   → ISO code
              - country_flag   → emoji flag
              - plate_format   → e.g. "XX00 XXX" (UK)
        """
        if country_code and country_code != self.country_code:
            # Hot-swap country config for this call
            self.country_code = country_code
            self.country_cfg = get_country_config(country_code)
            random.seed(hash(country_code) % (2**31))
            self._plate_pool = get_plate_pool(country_code)

        if scenario == "tamper":
            return []  # No plate data recoverable when camera is obstructed

        cc = self.country_code
        cfg = self.country_cfg
        results = []
        vehicle_idx = 0

        for i, det in enumerate(detections):
            label = det.get("label", "").lower()
            if label in ["person", "camera_blocked_tamper"]:
                continue

            vehicle_idx += 1
            vehicle_id = f"VH-{scenario.upper()[:3]}-{vehicle_idx:03d}"

            crop_info = self._plate_crop_simulated(det, i)
            ocr_result = self._run_ocr(vehicle_id)

            record = {
                "vehicle_id": vehicle_id,
                "vehicle_type": _vehicle_type_from_label(label),
                "detection_label": label,
                "detection_conf": det.get("confidence", 0.0),
                "plate_region": crop_info,
                "plate_text": ocr_result["plate_text"],
                "plate": ocr_result["plate_text"],  # normalized alias
                "ocr_confidence": ocr_result["ocr_confidence"],
                "plate_format": cfg.get("plate_format", ""),
                # ── Country context ─────────────────────────────────────
                "country_code": cc,
                "country_name": cfg["name"],
                "country_flag": cfg["flag"],
                "jurisdiction": f"{cfg['flag']} {cfg['name']}",
                # ── Metadata ────────────────────────────────────────────
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "scenario": scenario.upper(),
                "status": "RECOGNISED",
            }
            results.append(record)

        return results

    def get_summary(self, records: list[dict]) -> dict:
        """Returns aggregate statistics for a set of ANPR records."""
        if not records:
            return {
                "total_plates": 0,
                "registered": 0,
                "flagged": 0,
                "avg_ocr_confidence": 0.0,
                "vehicle_type_breakdown": {},
                "country_code": self.country_code,
                "country_name": self.country_cfg["name"],
                "country_flag": self.country_cfg["flag"],
            }

        type_counts: dict[str, int] = {}
        conf_total = 0.0
        for r in records:
            vt = r["vehicle_type"]
            type_counts[vt] = type_counts.get(vt, 0) + 1
            conf_total += r["ocr_confidence"]

        return {
            "total_plates": len(records),
            "total_vehicles_recognised": len(records),  # backward compat
            "registered": len(records),  # all recognised = registered
            "flagged": 0,  # updated by ANPR endpoint
            "avg_ocr_confidence": round(conf_total / len(records), 3),
            "vehicle_type_breakdown": type_counts,
            "country_code": self.country_code,
            "country_name": self.country_cfg["name"],
            "country_flag": self.country_cfg["flag"],
            "plate_format": self.country_cfg.get("plate_format", ""),
        }
