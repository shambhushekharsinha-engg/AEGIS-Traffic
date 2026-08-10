import os
import csv
import statistics

def get_stats(directory):
    p95s = []
    tps = []
    queue_waits = []
    errors = []
    
    # We have 3 runs per directory
    for run in range(1, 4):
        stats_file = f"results/{directory}/run-{run}_stats.csv"
        if not os.path.exists(stats_file):
            continue
            
        with open(stats_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Name'] == '/api/v1/analyze' and row['Type'] == 'POST':
                    # Parse p95 in ms
                    p95 = float(row.get('95%', 0))
                    p95s.append(p95)
                    
                    # TPS
                    req_s = float(row.get('Requests/s', 0))
                    tps.append(req_s)
                    
                    # Errors
                    fails = int(row.get('Failure Count', 0))
                    reqs = int(row.get('Request Count', 0))
                    err_rate = (fails / reqs * 100) if reqs > 0 else 0
                    errors.append(err_rate)
                    
                if row['Name'] == '/tasks/[task_id]' and row['Type'] == 'GET':
                    # Queue wait in seconds. Wait, response time is in ms. But Locust poll time represents total time from POST to success.
                    # Wait, no, the GET response time is just the HTTP request time!
                    # Total queue wait in locust is measured if the task was grouped, but in our locustfile we didn't group the total wait!
                    # Actually, we did not use an event hook to measure total time. We just polled.
                    pass

    return {
        "p95": round(statistics.median(p95s), 1) if p95s else 0,
        "tps": round(statistics.median(tps), 1) if tps else 0,
        "errors": round(statistics.median(errors), 1) if errors else 0
    }

dirs = ["baseline", "api-scale", "worker-1", "worker-2", "worker-3"]
for d in dirs:
    print(f"--- {d} ---")
    print(get_stats(d))
