from vision_module import FolderStreamAnalyzer
from audio_module import AudioAnalyzer  # Uses the decibel/RMS pipeline created earlier

def test_aegis_pipeline(ucf_folder_path, test_audio_path):
    vision_engine = FolderStreamAnalyzer()
    audio_engine = AudioAnalyzer()
    
    print("\n=============================================")
    print("📢 ACTIVATING AEGIS-MHR MULTIMODAL BENCHMARK")
    print("=============================================\n")
    
    # 1. Gather Visual context from image sequences
    detected_objects = vision_engine.process_frame_sequence(ucf_folder_path)
    
    # 2. Gather Acoustic context
    audio_result = audio_engine.check_anomaly(test_audio_path)
    
    # 3. Cross-Modal Analysis & Report Generation
    print("\n--- 🧠 CROSS-MODAL FUSION LAYER ---")
    print(f"[VISION CONTEXT]: Active scene objects detected -> {detected_objects}")
    print(f"[AUDIO CONTEXT]: Acoustic Profile -> {audio_result['type']} ({round(audio_result['db_level'], 2)} dB)")
    
    # Fusion Logic Matrix
    is_visual_anomaly = "car" in detected_objects or "person" in detected_objects
    is_audio_anomaly = audio_result["status"] == "Anomaly Detected"
    
    if is_visual_anomaly and is_audio_anomaly:
        alert_level = "🚨 CRITICAL (PRIORITY 1) ALERT"
        summary = f"High probability hazard confirmed. Visual signatures of dynamic elements matched with a synchronous {audio_result['type']} event."
    elif is_visual_anomaly or is_audio_anomaly:
        alert_level = "⚠️ WARNING (PRIORITY 2)"
        summary = "Single-channel anomaly registered. Unverified by secondary data stream; standby for verification."
    else:
        alert_level = "✅ NORMAL"
        summary = "Environmental baselines stable. No actionable data patterns detected."
        
    print(f"\n[📝 AUTOMATED INCIDENT REPORT]")
    print(f"Classification Status : {alert_level}")
    print(f"System Analysis       : {summary}")
    print("\n=============================================")

if __name__ == "__main__":
    # Point this to one of your extracted UCF-Crime category test subfolders
    TARGET_UCF_FOLDER = "dataset/Test/Explosion" 
    TARGET_AUDIO_FILE = "dataset/Audio_Samples/explosion_sound.wav" 
    
    test_aegis_pipeline(TARGET_UCF_FOLDER, TARGET_AUDIO_FILE)