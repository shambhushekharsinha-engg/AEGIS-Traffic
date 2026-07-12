# app/pipeline/simulate_pipeline.py
import numpy as np
import time

class SimulatedVisionModule:
    def __init__(self):
        print("[System] Vision Subsystem Initialized (Simulated Mode).")

    def get_mock_frame_data(self, scenario="normal"):
        time.sleep(0.1) 
        if scenario == "accident":
            return [{"label": "car", "confidence": 0.89}, {"label": "person", "confidence": 0.94}]
        elif scenario == "fire":
            return [{"label": "fire", "confidence": 0.76}, {"label": "person", "confidence": 0.62}]
        elif scenario == "tamper":
            return [{"label": "CAMERA_BLOCKED_TAMPER", "confidence": 0.99}]
        else:
            return [{"label": "person", "confidence": 0.45}]

class SimulatedAudioModule:
    def __init__(self):
        print("[System] Audio Subsystem Initialized (Simulated Mode).")

    def get_mock_audio_data(self, scenario="normal"):
        if scenario == "accident":
            return {"status": "Anomaly Detected", "db_level": 88.4, "type": "High-Decibel Crash/Impact"}
        elif scenario == "fire":
            return {"status": "Anomaly Detected", "db_level": 92.1, "type": "Industrial Fire Alarm"}
        elif scenario == "tamper":
            return {"status": "Line Static", "db_level": 12.0, "type": "Microphone Calibrating"}
        else:
            return {"status": "Normal", "db_level": 42.8, "type": "Ambient Traffic Hum"}

class AegisFusionCore:
    def __init__(self):
        self.vision = SimulatedVisionModule()
        self.audio = SimulatedAudioModule()

    def run_diagnostics(self, scenario):
        print(f"\n=============================================")
        print(f"📢 RUNNING LIVE SCENARIO SIMULATION: {scenario.upper()}")
        print("=============================================\n")
        
        visual_entities = self.vision.get_mock_frame_data(scenario)
        audio_profile = self.audio.get_mock_audio_data(scenario)
        labels = [item["label"] for item in visual_entities]
        
        print("--- 🧠 CROSS-MODAL LAYER INTERFACE ---")
        print(f"[VISION]: Detected Entities -> {labels}")
        print(f"[AUDIO] : Registered Profile -> {audio_profile['type']} ({audio_profile['db_level']} dB)")
        
        is_visual_hazard = any(x in ['car', 'fire', 'CAMERA_BLOCKED_TAMPER'] for x in labels)
        is_audio_hazard = audio_profile["status"] == "Anomaly Detected"
        
        if "CAMERA_BLOCKED_TAMPER" in labels:
            alert = "🛡️ TAMPER WARNING (PRIORITY 3)"
            desc = "Hardware asset obscuration event verified by local edge sensors."
        elif is_visual_hazard and is_audio_hazard:
            alert = "🚨 CRITICAL HAZARD (PRIORITY 1)"
            desc = f"Immediate response requested. Visual threat cross-verified via acoustic event."
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
    engine.run_diagnostics(scenario="normal")
    engine.run_diagnostics(scenario="accident")