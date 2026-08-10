from locust import HttpUser, task, between
import time

class TrafficUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """On start, we authenticate if required."""
        response = self.client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@AEGIS2024!"})
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {token}"}
        else:
            self.headers = {}

    @task
    def analyze_traffic(self):
        # 1. Start the task (simulating client POST /analyze)
        payload = {
            "scenario": "normal",
            "vision_threshold": 0.4,
            "model_tier": "YOLOv8-Nano"
        }
        
        with self.client.post("/api/v1/analyze", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 202:
                data = response.json()
                task_id = data.get("task_id")
                response.success()
            elif response.status_code == 503:
                response.failure("Task Queue Unavailable (503)")
                return
            else:
                response.failure(f"Failed to start task: {response.status_code}")
                return

        # 2. Poll the status until completion
        while True:
            # Poll every 2 seconds
            time.sleep(2)
            with self.client.get(f"/tasks/{task_id}", headers=self.headers, catch_response=True, name="/tasks/[task_id]") as poll_response:
                if poll_response.status_code == 200:
                    poll_data = poll_response.json()
                    status = poll_data.get("status")
                    
                    if status == "success":
                        poll_response.success()
                        break
                    elif status == "failure":
                        poll_response.failure(f"Task failed: {poll_data.get('error')}")
                        break
                    # Otherwise, it's 'queued' or 'running', keep polling
                else:
                    poll_response.failure(f"Failed to poll task: {poll_response.status_code}")
                    break
