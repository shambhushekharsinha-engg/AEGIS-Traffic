import numpy as np
import time

class SimulatedVisionModule:
    def __init__(self):
        print("[System] Vision Subsystem Initialized (Simulated Mode).")

    def get_mock_frame_data(self, scenario="normal"):
        """Generates mock object detections based on the chosen scenario."""
        # Simulating frame processing delay
        time.sleep(0.1) 
        
        if scenario == "accident":
            return [{"label": "car", "confidence": 0.89}, {"label": "person", "confidence": 0.94}]
        elif scenario == "fire":
            return [{"label": "fire", "confidence": 0.76}, {"label": "person", "confidence": 0.62}]
        else:
            return [{"label": "person", "confidence": 0.45}] # Normal ambient street view

class SimulatedAudioModule:
    def __init__(self):
        print("[System] Audio Subsystem Initialized (Simulated Mode).")

    def get_mock_audio_data(self, scenario="normal"):
        """Generates synthetic decibel levels and audio classifications."""
        if scenario == "accident":
            return {"status": "Anomaly Detected", "db_level": -12.4, "type": "High-Decibel Crash/Impact"}
        elif scenario == "fire":
            return {"status": "Anomaly Detected", "db_level": -15.1, "type": "Industrial Fire Alarm"}
        else:
            return {"status": "Normal", "db_level": -42.8, "type": "Ambient Traffic Hum"}

class AegisFusionCore:
    def __init__(self):
        self.vision = SimulatedVisionModule()
        self.audio = SimulatedAudioModule()

    def run_diagnostics(self, scenario):
        print(f"\n=============================================")
        # 2026 Date placeholder for simulated live logs
        print(f"📢 RUNNING LIVE SCENARIO SIMULATION: {scenario.upper()}")
        print("=============================================\n")
        
        # 1. Pipeline execution
        visual_entities = self.vision.get_mock_frame_data(scenario)
        audio_profile = self.audio.get_mock_audio_data(scenario)
        
        # Extract plain labels for fusion matrix
        labels = [item["label"] for item in visual_entities]
        
        print("--- 🧠 CROSS-MODAL LAYER INTERFACE ---")
        print(f"[VISION]: Detected Entities -> {labels}")
        print(f"[AUDIO] : Registered Profile -> {audio_profile['type']} ({audio_profile['db_level']} dB)")
        
        # 2. Decision Logic
        is_visual_hazard = any(x in ['car', 'fire'] for x in labels)
        is_audio_hazard = audio_profile["status"] == "Anomaly Detected"
        
        if is_visual_hazard and is_audio_hazard:
            alert = "🚨 CRITICAL HAZARD (PRIORITY 1)"
            desc = f"Immediate response requested. Visual threat '{labels[0]}' cross-verified via acoustic event ({audio_profile['type']})."
        elif is_visual_hazard or is_audio_hazard:
            alert = "⚠️ UNVERIFIED THREAT (PRIORITY 2)"
            desc = "Single-channel anomaly registered. Awaiting multi-sensory confirmation."
        else:
            alert = "✅ CLEAR (SYSTEM NOMINAL)"
            desc = "No actionable cross-modal threat vectors observed."
            
        print(f"\n[📝 AUTOMATED INCIDENT REPORT]")
        print(f"Status   : {alert}")
        print(f"Analysis : {desc}")
        print("\n=============================================")

if __name__ == "__main__":
    engine = AegisFusionCore()
    
    # Test a completely normal day
    engine.run_diagnostics(scenario="normal")
    
    # Test a simulated crash event
    engine.run_diagnostics(scenario="accident")