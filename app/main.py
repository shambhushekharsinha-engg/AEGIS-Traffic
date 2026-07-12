from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import time
import threading

# Importing the modular Simulation Engine components cleanly from the core subdirectory
from app.core.vision_module import VisionEngine
from app.core.audio_module import AudioEngine

app = FastAPI(
    title="Aegis-MHR: Enterprise Deep Learning Fusion Engine",
    version="2.1.0",
    description="Centralized Fusion Core orchestrating modular sensory engines and local transformer inference chains."
)

# Global memory state to track background dispatch notifications for the UI
DISPATCH_REGISTRY = {"status": "STABLE", "last_broadcast": "None"}

print("🤖 Ingesting Local Threat Anomaly Classifier (DistilBERT)...")
classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")

print("💬 Ingesting Local Interactive System Assistant (Qwen)...")
assistant = pipeline("text-generation", model="Qwen/Qwen2.5-0.5B-Instruct", max_new_tokens=100)
print("✅ All Advanced AI Components Active!")

class SimulationRequest(BaseModel):
    scenario: str
    vision_threshold: float
    model_tier: str

class ChatbotRequest(BaseModel):
    user_message: str
    incident_context: str
    
# =====================================================================
# 🕹️ SIMULATION PIPELINE: Asynchronous Threat Dispatch Worker
# =====================================================================
def execute_async_broadcast(scenario_type: str, timestamp: str):
    """Asynchronous background worker simulating encrypted emergency notifications."""
    global DISPATCH_REGISTRY
    DISPATCH_REGISTRY["status"] = "BROADCASTING"
    time.sleep(1.5)  # Simulating secure network handshake routing delay
    DISPATCH_REGISTRY["status"] = "SUCCESS"
    DISPATCH_REGISTRY["last_broadcast"] = f"SMS/Email emergency packets deployed at {timestamp} for {scenario_type.upper()}"

# =====================================================================
# 🔥 THE FUSION CORE: Multimodal Threat Ingestion Endpoint
# =====================================================================
@app.post("/api/v1/analyze")
def analyze_environment(payload: SimulationRequest):
    global DISPATCH_REGISTRY
    scenario = payload.scenario.lower()
    
    if scenario not in ["normal", "accident", "fire", "tamper"]:
        raise HTTPException(status_code=400, detail="Invalid target stream profile configuration selected.")
    
    # Instantiate the modular engine subcomponents
    vision = VisionEngine()
    audio = AudioEngine()
    
    start_time = time.time()
    
    # Feature 2: Hot-Swapping Compute Profiles (Simulating hardware processing scaling weights)
    if payload.model_tier == "YOLOv8-XLarge (Precision High-Load)":
        time.sleep(0.12)  # Extra processing lag for complex network parameters
        
    visual_data = vision.process(scenario, payload.vision_threshold)
    audio_data = audio.process(scenario)
    
    labels = [item["label"] for item in visual_data]
    
    # Check for hardware line exceptions first
    if "CAMERA_BLOCKED_TAMPER" in labels:
        priority = "🛡️ TAMPER WARNING (PRIORITY 3)"
        fused_context_string = "SECURITY CRITICAL: Video channel telemetry completely obscured or disconnected. Audio profile running baseline diagnostics."
        report_summary = "[Aegis Hardware Guard]: Video data pipeline lost. Hardware tamper detected at local node. Dispatching facility technicians immediately."
        risk_score = 75
    elif not labels and scenario in ["accident", "fire"]:
        # Scenario triggered but dropped below confidence filter sliders
        priority = "⚠️ MASKED UNVERIFIED RISK"
        fused_context_string = "Anomalous acoustics captured, but visual analytics dropped below confidence cutoff levels."
        report_summary = "[Aegis Core Neural Engine]: Acoustic anomaly detected, but visual tracking parameters filtered by dashboard settings. Standing by for cross-channel confirmation."
        risk_score = 40
    elif scenario in ["accident", "fire"]:
        priority = "🚨 CRITICAL (PRIORITY 1)"
        fused_context_string = f"Visual elements detected: {', '.join(labels)}. Audio status: {audio_data['type']} at sound pressure level {audio_data['db_level']} dB."
        report_summary = f"[Aegis Core Neural Engine]: High-priority threat patterns confirmed. Footprint: '{fused_context_string}'. Routing data arrays to municipal emergency nodes."
        risk_score = 98
        
        # Trigger background multi-threaded dispatcher
        timestamp = time.strftime('%H:%M:%S')
        threading.Thread(target=execute_async_broadcast, args=(scenario, timestamp), daemon=True).start()
    else:
        priority = "✅ NOMINAL"
        fused_context_string = f"Visual elements detected: {', '.join(labels)}. Audio status: {audio_data['type']} at standard levels."
        report_summary = "[Aegis Core Neural Engine]: System baselines stable. Environment secure."
        risk_score = 5
        DISPATCH_REGISTRY = {"status": "STABLE", "last_broadcast": "None"}
        
    execution_latency = (time.time() - start_time) * 1000 
    
    return {
        "latency_ms": round(execution_latency, 2),
        "risk_score": risk_score,
        "fused_context": fused_context_string,
        "telemetry": {"visual_detections": visual_data, "acoustic_profile": audio_data},
        "fusion_layer": {"alert_status": priority, "automated_incident_report": report_summary},
        "dispatch_network": DISPATCH_REGISTRY
    }

@app.post("/api/v1/chat")
def system_assistant_chat(payload: ChatbotRequest):
    prompt = (
        f"<|im_start|>system\nYou are the Aegis-MHR Tactical AI Assistant. Provide helpful, short, tactical crisis instructions based on the context.<|im_end|>\n"
        f"<|im_start|>context\n{payload.incident_context}<|im_end|>\n"
        f"<|im_start|>user\n{payload.user_message}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )
    response = assistant(prompt, clean_up_tokenization_spaces=True)
    clean_reply = response[0]['generated_text'].split("<|im_start|>assistant\n")[-1].strip()
    return {"reply": clean_reply}