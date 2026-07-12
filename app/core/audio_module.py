import torch
import torchaudio
import numpy as np

class AudioAnalyzer:
    def __init__(self):
        # Simple threshold-based decibel checker for rapid prototyping
        pass

    def check_anomaly(self, audio_path):
        waveform, sample_rate = torchaudio.load(audio_path)
        # Calculate Root Mean Square (RMS) to find sudden spike in volume
        rms = torch.sqrt(torch.mean(waveform**2))
        db = 20 * torch.log10(rms)
        
        # If sound is louder than normal ambient noise floor (-30dB threshold)
        if db > -20: 
            return {"status": "Anomaly Detected", "db_level": float(db), "type": "High-Decibel Impact/Scream"}
        return {"status": "Normal", "db_level": float(db), "type": "Ambient"}