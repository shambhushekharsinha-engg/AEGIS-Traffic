# app/pipeline/fusion_core.py

# Explicit imports pointing to your core module layouts
from app.core.vision_module import VisionEngine as FolderStreamAnalyzer
from app.core.audio_module import AudioEngine as AudioAnalyzer 

def test_aegis_pipeline(ucf_folder_path, test_audio_path):
    vision_engine = FolderStreamAnalyzer()
    audio_engine = AudioAnalyzer()
    
    print("\n=============================================")
    print("📢 ACTIVATING AEGIS-MHR MULTIMODAL BENCHMARK")
    print("=============================================\n")
    
    # 1. Gather Visual context from image sequences (uses dynamic threshold default 0.50)
    detected_objects = vision_engine.process(ucf_folder_path, 0.50)
    # Map back labels cleanly for legacy string structure parsing
    detected_labels = [item["label"] for item in detected_objects]
    
    # 2. Gather Acoustic context
    audio_result = audio_engine.process(ucf_folder_path) # Dynamic check
    
    # 3. Cross-Modal Analysis & Report Generation
    print("\n--- 🧠 CROSS-MODAL FUSION LAYER ---")
    print(f"[VISION CONTEXT]: Active scene objects detected -> {detected_labels}")
    print(f"[AUDIO CONTEXT]: Acoustic Profile -> {audio_result['type']} ({round(audio_result['db_level'], 2)} dB)")
    
    # Fusion Logic Matrix
    is_visual_anomaly = "car" in detected_labels or "person" in detected_labels or "fire" in detected_labels
    is_audio_anomaly = audio_result["status"] == "Anomaly Detected"
    
    if is_visual_anomaly and is_audio_anomaly:
        alert_level = "🚨 CRITICAL (PRIORITY 1) ALERT"
        summary = f"High probability hazard confirmed. Visual signatures matched with a synchronous {audio_result['type']} event."
    elif is_visual_anomaly or is_audio_anomaly:
        alert_level = "⚠️ WARNING (PRIORITY 2)"
        summary = "Single-channel anomaly registered. Unverified by secondary data stream."
    else:
        alert_level = "✅ NORMAL"
        summary = "Environmental baselines stable. No actionable data patterns detected."
        
    print(f"\n[📝 AUTOMATED INCIDENT REPORT]")
    print(f"Classification Status : {alert_level}")
    print(f"System Analysis       : {summary}")
    print("\n=============================================")

if __name__ == "__main__":
    TARGET_UCF_FOLDER = "dataset/Test/Explosion" 
    TARGET_AUDIO_FILE = "dataset/Audio_Samples/explosion_sound.wav" 
    test_aegis_pipeline(TARGET_UCF_FOLDER, TARGET_AUDIO_FILE)