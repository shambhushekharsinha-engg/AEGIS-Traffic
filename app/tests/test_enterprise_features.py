"""
AEGIS-Traffic — Enterprise High-ROI Features Automated Test Suite
"""


from app.core.benchmark_engine import benchmark_engine
from app.core.performance_monitor import performance_monitor
from app.pipeline.cctv_analytics import cctv_engine
from app.pipeline.dataset_explorer import dataset_explorer
from app.pipeline.explainability import explainability_engine
from app.pipeline.forecasting import forecasting_engine


def test_cctv_analytics_frame():
    res = cctv_engine.process_cctv_frame("CAM-01")
    assert "analytics" in res
    assert "total_vehicles" in res["analytics"]
    assert res["analytics"]["total_vehicles"] >= 0
    assert "tracks" in res


def test_time_series_forecasting():
    forecast = forecasting_engine.generate_timeline_forecast(
        current_density=65.0, location_name="Connaught Place"
    )
    assert forecast["location"] == "Connaught Place"
    assert len(forecast["timeline"]) == 5
    assert forecast["timeline"][0]["label"] == "Now"


def test_ai_explainability():
    exp = explainability_engine.explain_prediction(
        congestion_level="High", vehicle_count=40
    )
    assert "prediction_summary" in exp
    assert exp["prediction_summary"]["confidence_score_pct"] > 0
    assert len(exp["attribution_breakdown"]) == 4


def test_system_performance_health():
    health = performance_monitor.get_system_health()
    assert health["status"] == "HEALTHY"
    assert "performance_metrics" in health
    assert health["performance_metrics"]["api_latency_p50_ms"] > 0


def test_model_benchmarks():
    bm = benchmark_engine.get_model_benchmarks()
    assert len(bm["models_comparison"]) == 3
    assert len(bm["sla_benchmark_table"]) > 0


def test_dataset_explorer():
    ds = dataset_explorer.get_dataset_metadata()
    assert len(ds["datasets"]) >= 2
