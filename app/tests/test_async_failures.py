import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import kombu.exceptions
from app.main import app
from app.auth.dependencies import get_current_user

client = TestClient(app)

def override_get_current_user():
    return {"username": "admin", "role": "admin", "sub": "1"}

app.dependency_overrides[get_current_user] = override_get_current_user

def test_redis_offline_graceful_degradation():
    """Verify that when Redis is unreachable, the API returns a 503 instead of crashing."""
    with patch('app.worker.analyze_traffic_task.delay') as mock_delay:
        mock_delay.side_effect = kombu.exceptions.OperationalError("Connection refused")
        
        response = client.post(
            "/api/v1/analyze",
            json={"scenario": "normal", "vision_threshold": 0.4, "model_tier": "YOLOv8-Nano"}
        )
        
        assert response.status_code == 503
        data = response.json()
        assert data["error"] == "Task Queue Unavailable"


def test_task_status_redis_offline():
    """Verify that when checking task status and Redis is unreachable, it returns 503."""
    with patch('celery.result.AsyncResult') as mock_result:
        mock_result.side_effect = Exception("Redis connection error")
        
        response = client.get("/tasks/1234")
        
        assert response.status_code == 503
        data = response.json()
        assert data["error"] == "Task State Unavailable"


def test_task_failure_propagation():
    """Verify that if the worker task fails (e.g. YOLO crash), the API reports the error."""
    with patch('celery.result.AsyncResult') as mock_result_class:
        mock_result = MagicMock()
        mock_result.state = "FAILURE"
        mock_result.info = Exception("YOLO CUDA out of memory")
        mock_result_class.return_value = mock_result
        
        response = client.get("/tasks/5678")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failure"
        assert "error" in data
        assert "YOLO CUDA" in data["error"]
