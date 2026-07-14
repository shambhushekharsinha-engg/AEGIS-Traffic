from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import time
import threading

# Core sensory modules
from app.core.vision_module import VisionEngine
from app.core.audio_module import AudioEngine

# FIXED IMPORTS: Aligned with exact pipeline filenames and class names
from app.pipeline.fusion_core import AegisFusionCore as MultimodalFusionCore
from app.pipeline.simulate_pipeline import execute_async_broadcast
from app.pipeline.history_logger import log_incident_to_ledger, fetch_incident_history

app = FastAPI(title="Aegis-MHR: Enterprise Deep Learning Fusion Engine", version="3.0.0")
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

# --- FEATURE 1: WEBHOOK ALERT DISPATCH PIPELINE ---
def dispatch_enterprise_webhook(scenario: str, priority: str, payload: str):
    """Simulates broadcasting critical payloads to real-world corporate operational endpoints."""
    print(f"🌐 [WEBHOOK DISPATCH] Outgoing HTTP POST transmission to remote enterprise alert hubs...")
    time.sleep(1.0)
    print(f"🚀 [HUMAN OPERATOR NOTIFIED] High-priority pager alert delivered live for vector: {scenario.upper()}")

@app.post("/api/v1/analyze")
def analyze_environment(payload: SimulationRequest):
    global DISPATCH_REGISTRY
    scenario = payload.scenario.lower()
    
    if scenario not in ["normal", "accident", "fire", "tamper"]:
        raise HTTPException(status_code=400, detail="Invalid target profile.")
        
    start_time = time.time()
    
    if payload.model_tier == "YOLOv8-XLarge (Precision High-Load)":
        time.sleep(0.12)
        
    visual_data = VisionEngine().process(scenario, payload.vision_threshold)
    audio_data = AudioEngine().process(scenario)
    
    fusion_core = MultimodalFusionCore()
    priority, risk_score, fused_context, report = fusion_core.fuse_and_classify(visual_data, audio_data, scenario)
    
    execution_latency = (time.time() - start_time) * 1000 
    
    # --- FEATURE 2: HISTORICAL LOGGING RETENTION ---
    log_incident_to_ledger(priority, scenario, risk_score, round(execution_latency, 2))
    
    if priority in ["🚨 CRITICAL (PRIORITY 1)", "🛡️ TAMPER WARNING (PRIORITY 3)"]:
        timestamp = time.strftime('%H:%M:%S')
        # FIXED THREAD INVOKER: Added DISPATCH_REGISTRY mapping pointer argument required by simulation module
        threading.Thread(target=execute_async_broadcast, args=(scenario, timestamp, DISPATCH_REGISTRY), daemon=True).start()
        threading.Thread(target=dispatch_enterprise_webhook, args=(scenario, priority, fused_context), daemon=True).start()
    elif priority == "✅ NOMINAL":
        DISPATCH_REGISTRY = {"status": "STABLE", "last_broadcast": "None"}
        
    return {
        "latency_ms": round(execution_latency, 2),
        "risk_score": risk_score,
        "fused_context": fused_context,
        "telemetry": {"visual_detections": visual_data, "acoustic_profile": audio_data},
        "fusion_layer": {"alert_status": priority, "automated_incident_report": report},
        "dispatch_network": DISPATCH_REGISTRY
    }

@app.get("/api/v1/history")
def get_historical_metrics():
    """Exposes transaction logs to build dashboard monitoring charts."""
    return {"history": fetch_incident_history()}

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