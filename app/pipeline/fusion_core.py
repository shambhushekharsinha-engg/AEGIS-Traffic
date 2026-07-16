# app/pipeline/fusion_core.py

import time
from transformers import pipeline

try:
    print("🤖 Booting Production Zero-Shot Traffic Fusion Transformer...")
    # Using the existing model for zero-shot text classification
    classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")
    TRANSFORMER_ONLINE = True
except Exception as e:
    print(f"⚠️ Neural network instantiation failure. Activating Circuit Breaker Backup: {str(e)}")
    TRANSFORMER_ONLINE = False

class MultimodalFusionCore:
    def __init__(self):
        # Specific traffic fusion states
        self.candidate_labels = [
            "Traffic Accident Scene", 
            "Emergency Transit Priority", 
            "Severe Intersection Congestion", 
            "Normal Traffic Flow"
        ]

    def fuse_and_classify(self, visual_data: list, audio_data: dict, scenario: str,
                           operational_mode: str = "AI Automated Fusion",
                           manual_active_phase: str = None,
                           manual_signal_timing: int = None):
        """
        Fuses visual object detections with acoustic frequency diagnostics 
        to calculate adaptive traffic signal timings and emergency priorities,
        under a multi-mode state-machine architecture.
        """
        # Count vehicles (cars, trucks, buses, motorcycles) and check for camera blockage
        vehicle_labels = ["car", "truck", "bus", "motorcycle"]
        vehicle_count = sum(1 for item in visual_data if item["label"] in vehicle_labels)
        
        has_tamper = any(item["label"] == "CAMERA_BLOCKED_TAMPER" for item in visual_data)
        
        # Audio status details
        audio_type = audio_data.get("type", "Ambient")
        db_level = audio_data.get("db_level", 40.0)
        peak_freq = audio_data.get("peak_frequency", 0.0)
        
        fused_context = (
            f"Traffic visual queue: {vehicle_count} vehicles. "
            f"Acoustic feedback: {audio_type} detected at {db_level} dB, peak frequency {peak_freq} Hz."
        )

        # Apply state-machine operating modes
        if operational_mode == "Security Lockdown":
            priority = "🔒 SECURITY LOCKDOWN (CRITICAL)"
            risk_score = 90
            active_phase = "ALL RED (LOCKDOWN)"
            signal_timing = 0
            report = "[Aegis Security Guard]: Emergency manual lockdown engaged. All traffic pathways blocked."
            advisory = "LOCKDOWN ACTIVE: Intersection locked down. Traffic operations suspended. Cryptographic keys isolating database."
            
        elif operational_mode == "Manual Override":
            priority = "🎛️ MANUAL CONTROL OVERRIDE"
            risk_score = 15
            active_phase = manual_active_phase if manual_active_phase else "North-South Green"
            signal_timing = manual_signal_timing if manual_signal_timing is not None else 20
            report = "Manual dispatch override engaged by system operator."
            advisory = f"MANUAL CONTROL ACTIVE: System executing operator instruction set. Phase: {active_phase}."

        elif operational_mode == "Predictive Optimization":
            priority = "🔮 PREDICTIVE OPTIMIZATION ACTIVE"
            risk_score = 25
            # Simulate a time-of-day predictive shift:
            # Under predictive model, we extend green timing to handle the upcoming traffic wave
            active_phase = "North-South Green (Predictive Shift)"
            signal_timing = 40
            report = "[Aegis Forecasting Engine]: ARIMA model predicts 45% traffic wave increase. Proactively extending green window."
            advisory = "PREDICTIVE ADAPTATION: Green phase adjusted pre-emptively to 40s to clear historical evening rush hour queues."

        else: # Standard "AI Automated Fusion" Mode
            # Run zero-shot classification if transformer is online
            top_prediction = "Normal Traffic Flow"
            if TRANSFORMER_ONLINE and not has_tamper:
                try:
                    model_prediction = classifier(fused_context, self.candidate_labels)
                    top_prediction = model_prediction['labels'][0]
                except Exception:
                    top_prediction = self._deterministic_fallback_logic(scenario, vehicle_count, audio_type)
            else:
                top_prediction = self._deterministic_fallback_logic(scenario, vehicle_count, audio_type)

            # Heuristic Guardrail: Override deep learning NLP noise for clear low-density scenarios
            if vehicle_count <= 2 and audio_type == "Ambient" and scenario not in ["accident", "emergency"]:
                top_prediction = "Normal Traffic Flow"

            # Decision Matrix & Adaptive Traffic Signal Control (ATSC) Rules
            signal_timing = 15 # Default green light countdown (seconds)
            active_phase = "North-South Green"
            
            if has_tamper:
                priority = "🛡️ TAMPER WARNING (PRIORITY 3)"
                risk_score = 75
                active_phase = "ALL FLASHING YELLOW (CAUTION)"
                signal_timing = 0
                report = "[Aegis Hardware Guard]: Visual traffic stream lost. Hardware obscuration/tamper detected."
                advisory = "CRITICAL: Visual feed lost. Intersection switched to caution mode (Flashing Yellow). Maintenance dispatched."
                
            elif scenario == "emergency" or audio_type == "Siren" or top_prediction == "Emergency Transit Priority":
                priority = "🚨 EMERGENCY OVERRIDE (PRIORITY 1)"
                risk_score = 95
                active_phase = "EMERGENCY VEHICLE PRIORITY (GREEN)"
                signal_timing = 25 # Force 25s green priority window
                report = f"[Aegis Traffic Engine]: Priority preemption override engaged. Sirens heard at {db_level} dB."
                advisory = "EMERGENCY TRANSIT ACTIVE: Priority path clearing active for approaching emergency vehicles. Pull over safely."

            elif scenario == "accident" or audio_type == "Collision" or top_prediction == "Traffic Accident Scene":
                priority = "🚨 COLLISION ALERT (PRIORITY 2)"
                risk_score = 99
                active_phase = "ALL RED (CONTAINMENT)"
                signal_timing = 0
                report = f"[Aegis Traffic Engine]: Incident detected. Waveform: '{fused_context}'."
                advisory = "ACCIDENT DETECTED: Emergency vehicles dispatched. Rerouting traffic via Expressway Bypass B."
                
            else:
                # Normal adaptive signal timings
                priority = "✅ NOMINAL CONTROL"
                if vehicle_count >= 9 or top_prediction == "Severe Intersection Congestion":
                    signal_timing = 45 # High density lane gets 45s green
                    risk_score = 30
                    report = f"[Aegis Traffic Engine]: High congestion adaptive signal timing engaged ({vehicle_count} cars)."
                    advisory = "HIGH DENSITY: Intersection timing extended to 45s to clear traffic queues."
                elif 5 <= vehicle_count <= 8:
                    signal_timing = 30 # Medium density
                    risk_score = 15
                    report = f"[Aegis Traffic Engine]: Medium congestion adaptive timing engaged ({vehicle_count} cars)."
                    advisory = "MEDIUM DENSITY: Intersection timing adjusted dynamically to 30s."
                else:
                    signal_timing = 15 # Low density
                    risk_score = 5
                    report = "[Aegis Traffic Engine]: Baselines stable. Standard 15s adaptive timing cycle."
                    advisory = "NOMINAL: Low volume. Intersection cycling on standard 15s green intervals."

        return {
            "priority": priority,
            "risk_score": risk_score,
            "fused_context": fused_context,
            "report": report,
            "advisory": advisory,
            "signal_timing_seconds": signal_timing,
            "active_phase": active_phase,
            "vehicle_count": vehicle_count
        }

    def _deterministic_fallback_logic(self, scenario: str, vehicle_count: int, audio_type: str) -> str:
        """Fallback heuristics to maintain system integrity during hardware/NLP exceptions."""
        print("⚡ [CIRCUIT BREAKER ENGAGED]: Running deterministic traffic fusion heuristics...")
        if scenario == "accident" or audio_type == "Collision":
            return "Traffic Accident Scene"
        if scenario == "emergency" or audio_type == "Siren":
            return "Emergency Transit Priority"
        if vehicle_count >= 7:
            return "Severe Intersection Congestion"
        return "Normal Traffic Flow"