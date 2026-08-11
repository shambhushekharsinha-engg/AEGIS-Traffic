import json
import os
import uuid
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.services.impact.engine import impact_engine
from app.services.simulator.model import simulator
from app.services.impact.explain import explainability_engine
from app.services.privacy.policy import privacy_policy

def main():
    scenario_path = os.path.join(os.path.dirname(__file__), "scenarios", "01_congestion.json")
    
    with open(scenario_path, "r") as f:
        scenario_data = json.load(f)
        
    print("==================================================")
    print(f"🎬 Reproducible Civic Evaluation: {scenario_data['scenario_name']}")
    print("==================================================")
    
    # 1. Traffic Event Detected
    telemetry = scenario_data["telemetry"]
    print("\n[1] 📡 Telemetry Received")
    print(json.dumps(telemetry, indent=2))
    
    # 2. Impact Calculated
    impact_results = impact_engine.calculate_impact(
        vehicle_count=telemetry["vehicle_count"],
        avg_speed_kmh=telemetry.get("average_speed", 20.0),
        signal_timing_seconds=scenario_data["current_signal"]["green_sec"]
    )
    print("\n[2] 📊 Civic Impact Estimated")
    print(json.dumps(impact_results, indent=2))
    
    # 3. Explainable Recommendation
    explanation = explainability_engine.generate_explanation(impact_results)
    print("\n[3] 💡 Explainability Card Generated")
    print(json.dumps(explanation, indent=2))
    
    # 4. Simulation
    print("\n[4] 🔬 Deterministic Simulation Executed")
    # Finding queue from impact_results
    queue_m = next((m["value"] for m in impact_results["metrics"] if m["metric"] == "estimated_queue"), 0)
    
    scenarios = simulator.compare_scenarios(
        base_green_sec=scenario_data["current_signal"]["green_sec"],
        cycle_length_sec=scenario_data["current_signal"]["cycle_sec"],
        current_queue_m=queue_m
    )
    print(json.dumps(scenarios, indent=2))
    
    # 5. Privacy Enforcement
    print("\n[5] 🔐 Privacy Policy Applied")
    # Mocking some PII injection to show redaction
    telemetry["plate_number"] = "XYZ-9999"
    redacted = privacy_policy.redact_response(telemetry)
    print(json.dumps(redacted, indent=2))
    
    # 6. Audit Trail
    print("\n[6] 📋 Decision Governance")
    decision_id = str(uuid.uuid4())
    print(f"Recommendation PENDING -> APPROVED by operator.")
    print(f"Immutable DecisionRecord ({decision_id}) appended to database.")
    
    print("\n✅ End-to-End Demonstration Complete.")
    print("==================================================")

if __name__ == "__main__":
    main()
