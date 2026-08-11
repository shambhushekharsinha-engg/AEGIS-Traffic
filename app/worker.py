import os
import time
import threading
from celery import Celery
import uuid

# Set up Celery
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "aegis_tasks", broker=broker_url, backend=result_backend, include=["app.worker"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

# Global singletons for worker
vision_engine_instance = None
audio_engine_instance = None
fusion_core_instance = None


def get_engines():
    global vision_engine_instance, audio_engine_instance, fusion_core_instance
    if fusion_core_instance is None:
        from app.pipeline.fusion_core import MultimodalFusionCore
        from app.pipeline.vision_engine import VisionEngine
        from app.pipeline.audio_engine import AudioEngine

        vision_engine_instance = VisionEngine()
        audio_engine_instance = AudioEngine()
        fusion_core_instance = MultimodalFusionCore()
    return vision_engine_instance, audio_engine_instance, fusion_core_instance


@celery_app.task(bind=True, max_retries=3, name="app.worker.analyze_traffic_task")
def analyze_traffic_task(self, payload: dict, user_context: dict):
    """
    Decoupled YOLO/PyTorch inference task.
    """
    try:
        from app.db.database import SessionLocal
        from app.db import crud
        from app.core.violation_module import ViolationDetector
        from app.pipeline.geo_context import (
            detect_country,
            get_country_config,
            get_plate_pool,
        )
        from app.pipeline.history_logger import log_incident_to_ledger
        from app.pipeline.simulate_pipeline import execute_async_broadcast

        scenario = payload.get("scenario", "normal").lower()
        model_tier = payload.get("model_tier")

        vision_eng, audio_eng, fusion_core = get_engines()
        start_time = time.time()

        if model_tier == "YOLOv8-XLarge (Precision High-Load)":
            time.sleep(0.12)

        try:
            vision_result = vision_eng.process_traffic_scene(scenario)
            visual_data = vision_result["detections"]
            visual_image_b64 = vision_result["image_b64"]
            audio_data = audio_eng.check_anomaly(
                f"dataset/Audio_Samples/{scenario}_sound.wav"
            )
        except Exception as e:
            visual_data = [
                {
                    "label": "person" if scenario == "normal" else "car",
                    "confidence": 0.95,
                }
            ]
            visual_image_b64 = ""
            audio_data = {
                "status": (
                    "Anomaly Detected"
                    if scenario in ["accident", "emergency"]
                    else "Normal"
                ),
                "db_level": 88.5,
                "type": "Collision" if scenario == "accident" else "Ambient",
                "waveform": [0.0] * 100,
                "fft_frequencies": [0.0] * 100,
                "fft_amplitudes": [0.0] * 100,
                "peak_frequency": 0.0,
            }

        fused_results = fusion_core.fuse_and_classify(
            visual_data,
            audio_data,
            scenario,
            operational_mode=payload.get("operational_mode"),
            manual_active_phase=payload.get("manual_active_phase"),
            manual_signal_timing=payload.get("manual_signal_timing"),
        )

        execution_latency = (time.time() - start_time) * 1000

        # Geo-context
        country_code = detect_country(
            location_name=payload.get("location_name"),
            lat=payload.get("latitude"),
            lon=payload.get("longitude"),
            try_nominatim=True,
        )
        country_cfg = get_country_config(country_code)
        _plate_pool = get_plate_pool(country_code)

        # Database Insertion
        try:
            _db = SessionLocal()
            _detector_v = ViolationDetector(
                speed_limit_kmh=float(country_cfg.get("speed_limit_urban", 50)),
                country_code=country_code,
            )
            _viols_raw = _detector_v.detect_violations(
                visual_data,
                scenario,
                fused_results["active_phase"],
                fused_results["avg_speed_kmh"],
                plate_pool=_plate_pool,
            ).get("violations", [])

            # Idempotency check: we can use self.request.id as request_id
            req_id = self.request.id

            crud.create_incident(
                _db,
                operator_name=user_context.get("username", "system"),
                operator_id=user_context.get("user_id"),
                scenario=scenario,
                priority=fused_results["priority"],
                risk_score=fused_results["risk_score"],
                latency_ms=round(execution_latency, 2),
                vehicle_count=fused_results["vehicle_count"],
                avg_speed_kmh=fused_results["avg_speed_kmh"],
                traffic_density=fused_results["density_level"],
                active_phase=fused_results["active_phase"],
                signal_timing=fused_results["signal_timing_seconds"],
                operational_mode=payload.get("operational_mode"),
                crime_score=fused_results.get("crime_score"),
                crime_type=fused_results.get("detected_crime_type"),
                crime_severity=fused_results.get("crime_severity"),
                crime_is_anomaly=fused_results.get("crime_is_anomaly"),
                location_name=payload.get("location_name"),
                latitude=payload.get("latitude"),
                longitude=payload.get("longitude"),
                request_id=req_id,
                violations_data=_viols_raw,
            )
            _db.close()
        except Exception as _log_err:
            pass

        return {
            "scenario": scenario,
            "latency_ms": round(execution_latency, 2),
            "risk_score": fused_results["risk_score"],
            "fused_context": fused_results["fused_context"],
            "telemetry": {
                "visual_detections": visual_data,
                "visual_image_b64": visual_image_b64,
                "acoustic_profile": audio_data,
            },
            "fusion_layer": {
                "alert_status": fused_results["priority"],
                "automated_incident_report": fused_results["report"],
                "rerouting_advisory": fused_results["advisory"],
                "signal_timing_seconds": fused_results["signal_timing_seconds"],
                "active_phase": fused_results["active_phase"],
                "vehicle_count": fused_results["vehicle_count"],
            },
            "traffic_analytics": {
                "traffic_density_percent": fused_results["traffic_density_percent"],
                "density_level": fused_results["density_level"],
                "queue_length_meters": fused_results["queue_length_meters"],
                "avg_speed_kmh": fused_results["avg_speed_kmh"],
                "lane_counts": fused_results["lane_counts"],
            },
            "location": {
                "name": payload.get("location_name"),
                "latitude": payload.get("latitude"),
                "longitude": payload.get("longitude"),
            },
            "geo_context": {
                "country_code": country_code,
                "country_name": country_cfg["name"],
                "country_flag": country_cfg["flag"],
                "currency_code": country_cfg["currency_code"],
                "currency_symbol": country_cfg["currency_symbol"],
                "speed_limit_kmh": country_cfg["speed_limit_urban"],
                "drive_side": country_cfg.get("drive_side", "right"),
                "plate_format": country_cfg.get("plate_format", ""),
                "plate_example": country_cfg.get("plate_example", ""),
            },
        }

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
