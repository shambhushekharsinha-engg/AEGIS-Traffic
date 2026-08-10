$ErrorActionPreference = "Stop"

Write-Host "============================================="
Write-Host "AEGIS-Traffic Scalability Benchmark Harness"
Write-Host "============================================="

$runs = 1..3

function Run-Locust-Tests {
    param(
        [string]$Directory,
        [int]$Users,
        [int]$SpawnRate
    )
    New-Item -ItemType Directory -Force -Path "results/$Directory" | Out-Null
    foreach ($run in $runs) {
        Write-Host "  -> Iteration $run..."
        locust -f locustfile.py --headless -u $Users -r $SpawnRate -t 1m --host http://localhost --csv="results/$Directory/run-$run"
    }
}

Write-Host "`n[1] Baseline (1 API, 1 Worker, 10 Users)..."
docker compose down -v
docker compose up -d --build --scale backend=1 --scale inference-worker=1
Start-Sleep -Seconds 15
Write-Host "Running Locust for Baseline (3 runs of 1m)..."
Run-Locust-Tests -Directory "baseline" -Users 10 -SpawnRate 2
Write-Host "Baseline Complete."

Write-Host "`n[2] API Scaling (3 API, 1 Worker, 10 Users)..."
docker compose up -d --scale backend=3 --scale inference-worker=1
Start-Sleep -Seconds 10
Write-Host "Running Locust for API Scaling (3 runs of 1m)..."
Run-Locust-Tests -Directory "api-scale" -Users 10 -SpawnRate 2
Write-Host "API Scaling Complete."

Write-Host "`n[3] Worker Scaling (3 API, 1 Worker, 30 Users)..."
docker compose up -d --scale backend=3 --scale inference-worker=1
Start-Sleep -Seconds 5
Write-Host "Running Locust for Worker Scaling 1x (3 runs of 1m)..."
Run-Locust-Tests -Directory "worker-1" -Users 30 -SpawnRate 5
Write-Host "Worker Scaling 1x Complete."

Write-Host "`n[4] Worker Scaling (3 API, 2 Workers, 30 Users)..."
docker compose up -d --scale backend=3 --scale inference-worker=2
Start-Sleep -Seconds 10
Write-Host "Running Locust for Worker Scaling 2x (3 runs of 1m)..."
Run-Locust-Tests -Directory "worker-2" -Users 30 -SpawnRate 5
Write-Host "Worker Scaling 2x Complete."

Write-Host "`n[5] Worker Scaling (3 API, 3 Workers, 30 Users)..."
docker compose up -d --scale backend=3 --scale inference-worker=3
Start-Sleep -Seconds 10
Write-Host "Running Locust for Worker Scaling 3x (3 runs of 1m)..."
Run-Locust-Tests -Directory "worker-3" -Users 30 -SpawnRate 5
Write-Host "Worker Scaling 3x Complete."

Write-Host "`nCleaning up..."
docker compose down
Write-Host "Done! Extract the medians from the CSV files in the 'results' directory to populate scaling_report.md."
