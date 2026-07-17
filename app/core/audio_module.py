import os
import numpy as np
import math
import wave
import struct

class AudioAnalyzer:
    def __init__(self):
        self.sample_rate = 16000
        self.duration_seconds = 2.0
        
        # Ensure directories exist.
        # On Vercel the task root is read-only; /tmp is the only writable path.
        # We try the preferred paths first and silently fall back to /tmp variants.
        for path in ["data/audio_samples", "dataset/Audio_Samples"]:
            try:
                os.makedirs(path, exist_ok=True)
            except OSError:
                # Read-only filesystem (Vercel) — create equivalent under /tmp instead
                tmp_path = "/tmp/" + path.replace("/", "_")
                try:
                    os.makedirs(tmp_path, exist_ok=True)
                except OSError:
                    pass  # /tmp itself always exists; nothing more to do

    def _generate_synthetic_wav(self, scenario: str, file_path: str):
        """
        Synthesizes realistic traffic sounds using NumPy and saves them as WAV using 
        standard Python wave/struct.
        """
        n_samples = int(self.sample_rate * self.duration_seconds)
        t = np.linspace(0, self.duration_seconds, n_samples, endpoint=False)
        waveform = np.zeros(n_samples)

        if scenario == "normal":
            # Normal: Low amplitude brown/white ambient noise
            waveform = np.random.normal(0, 0.02, n_samples)
            # Add a very low frequency motor rumble (50 Hz)
            waveform += 0.01 * np.sin(2 * np.pi * 50 * t)
            
        elif scenario == "congested":
            # Congested: Ambient traffic noise + periodic honking
            waveform = np.random.normal(0, 0.03, n_samples)
            # Add two car honks (duration 0.25s each at 400Hz + 440Hz dual tone)
            # First honk at t=0.3s
            honk_mask_1 = (t >= 0.3) & (t <= 0.6)
            waveform[honk_mask_1] += 0.15 * np.sin(2 * np.pi * 400 * t[honk_mask_1])
            waveform[honk_mask_1] += 0.15 * np.sin(2 * np.pi * 450 * t[honk_mask_1])
            # Second honk at t=1.2s
            honk_mask_2 = (t >= 1.2) & (t <= 1.4)
            waveform[honk_mask_2] += 0.18 * np.sin(2 * np.pi * 400 * t[honk_mask_2])
            waveform[honk_mask_2] += 0.18 * np.sin(2 * np.pi * 450 * t[honk_mask_2])

        elif scenario == "emergency":
            # Emergency: Continuous frequency-swept siren wail (600Hz to 1200Hz)
            # Siren wail frequency w(t) = 900 + 300 * sin(2 * pi * 0.75 * t)
            phase = 2 * np.pi * (900 * t + (300 / (2 * np.pi * 0.75)) * (1 - np.cos(2 * np.pi * 0.75 * t)))
            waveform = 0.25 * np.sin(phase)
            # Add a bit of background traffic noise
            waveform += np.random.normal(0, 0.01, n_samples)

        elif scenario == "accident":
            # Accident: Sudden loud impact crash burst followed by silence/low hum
            crash_start_idx = int(0.2 * self.sample_rate)
            decay_constant = 8.0 # Decay rate
            for i in range(n_samples):
                if i < crash_start_idx:
                    waveform[i] = np.random.normal(0, 0.01)
                else:
                    t_decay = (i - crash_start_idx) / self.sample_rate
                    decay = math.exp(-decay_constant * t_decay)
                    waveform[i] = 0.6 * np.random.normal(0, 1.0) * decay
                    waveform[i] += 0.15 * np.sin(2 * np.pi * 3000 * t_decay) * decay
        else: # Default fallback
            waveform = np.random.normal(0, 0.01, n_samples)

        # Write WAV using standard library
        with wave.open(file_path, 'wb') as wav_file:
            wav_file.setnchannels(1) # mono
            wav_file.setsampwidth(2) # 16-bit
            wav_file.setframerate(self.sample_rate)
            for sample in waveform:
                # Clip values between -1.0 and 1.0, then scale to 16-bit signed integer
                val = int(max(-1.0, min(1.0, sample)) * 32767)
                wav_file.writeframesraw(struct.pack('<h', val))
                
        print(f"🎵 Synthesized {scenario.upper()} traffic sound to {file_path} (Pure Wave)")

    def _load_wav_pure(self, file_path: str):
        """
        Loads a WAV file using standard Python wave/struct libraries.
        Returns (waveform_numpy, sample_rate).
        """
        with wave.open(file_path, 'rb') as wav_file:
            n_channels = wav_file.getnchannels()
            sampwidth = wav_file.getsampwidth()
            sr = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            
            data = wav_file.readframes(n_frames)
            
            if sampwidth == 2:
                raw_data = np.frombuffer(data, dtype=np.int16)
                normalized = raw_data.astype(np.float32) / 32768.0
            elif sampwidth == 1:
                raw_data = np.frombuffer(data, dtype=np.uint8)
                normalized = (raw_data.astype(np.float32) - 128.0) / 128.0
            else:
                raise ValueError(f"Unsupported sample width: {sampwidth}")
                
            # Handle multi-channel
            if n_channels > 1:
                normalized = normalized.reshape(-1, n_channels)
                normalized = normalized[:, 0] # take first channel
                
            waveform = np.expand_dims(normalized, axis=0)
            return waveform, sr

    def check_anomaly(self, audio_path: str):
        """
        Loads the WAV audio file, calculates RMS (dB), performs FFT frequency analysis,
        classifies the sound profile, and returns comprehensive telemetry data.
        """
        # Determine scenario name from filename path
        filename = os.path.basename(audio_path).lower()
        if "accident" in filename:
            scenario = "accident"
        elif "fire" in filename or "emergency" in filename:
            scenario = "emergency"
        elif "congest" in filename or "tamper" in filename:
            scenario = "congested"
        else:
            scenario = "normal"

        # Check if the file exists. If not, synthesize it on the fly!
        if not os.path.exists(audio_path):
            # Try to write to the requested path; if the filesystem is read-only
            # (Vercel), redirect the WAV to /tmp and load from there.
            try:
                os.makedirs(os.path.dirname(audio_path) or ".", exist_ok=True)
                self._generate_synthetic_wav(scenario, audio_path)
            except OSError:
                # Fall back to /tmp for WAV synthesis
                tmp_audio_path = "/tmp/" + os.path.basename(audio_path)
                if not os.path.exists(tmp_audio_path):
                    try:
                        self._generate_synthetic_wav(scenario, tmp_audio_path)
                    except Exception:
                        pass
                audio_path = tmp_audio_path

        try:
            waveform, sr = self._load_wav_pure(audio_path)
        except Exception as e:
            print(f"⚠️ Pure wave load failed: {e}. Trying torchaudio fallback.")
            try:
                import torch
                import torchaudio
                torch_waveform, sr = torchaudio.load(audio_path)
                waveform = torch_waveform.numpy()
            except Exception as e2:
                # Absolute fallback if reading fails
                print(f"⚠️ Waveform load error: {e2}. Generating in-memory array.")
                waveform = np.random.randn(1, int(self.sample_rate * self.duration_seconds)) * 0.01
                sr = self.sample_rate

        # Calculate decibels (RMS)
        rms = np.sqrt(np.mean(waveform**2))
        db = 20 * np.log10(rms + 1e-6)
        db_level = float(db)
        
        # Map DB levels to positive sound pressure scale (0 to 120 dB)
        # where -60dB FS is ambient (~40 dB SPL) and 0dB FS is maximum (~100 dB SPL)
        spl_db = round(spl_db_scale(db_level), 1)

        # Analyze frequency spectrum (FFT)
        # Extract first channel
        signal = waveform[0]
        n_samples = len(signal)
        
        # Run Real FFT using NumPy
        fft_res = np.fft.rfft(signal)
        fft_amplitude = np.abs(fft_res)
        frequencies = np.fft.rfftfreq(n_samples, d=1.0/sr)
        
        # Spot peak frequencies (excluding very low sub-bass < 80Hz)
        valid_mask = frequencies > 80
        valid_freqs = frequencies[valid_mask]
        valid_amps = fft_amplitude[valid_mask]
        
        peak_idx = np.argmax(valid_amps)
        peak_freq = float(valid_freqs[peak_idx])
        
        # Classification heuristics based on SPL and Peak Frequency
        sound_type = "Ambient"
        status = "Normal"
        
        if spl_db > 80:
            if peak_freq > 2000:
                sound_type = "Collision"
                status = "Anomaly Detected"
            elif 500 <= peak_freq <= 1500:
                sound_type = "Siren"
                status = "Anomaly Detected"
            else:
                sound_type = "Collision"
                status = "Anomaly Detected"
        elif spl_db > 65:
            if 350 <= peak_freq <= 500:
                sound_type = "Horn"
                status = "Normal"
            else:
                sound_type = "Ambient"
                status = "Normal"
        else:
            sound_type = "Ambient"
            status = "Normal"
            
        # Decimate waveform and FFT data for Plotly dashboard visualization
        # Waveform: take 200 points
        step_wave = max(1, n_samples // 200)
        wave_pts = signal[::step_wave][:200].tolist()
        
        # FFT: take 100 points from 0 to 4000Hz (where interesting things happen)
        freq_limit_mask = frequencies < 4000
        freqs_limited = frequencies[freq_limit_mask]
        amps_limited = fft_amplitude[freq_limit_mask]
        
        step_fft = max(1, len(freqs_limited) // 100)
        fft_freq_pts = freqs_limited[::step_fft][:100].tolist()
        fft_amp_pts = (amps_limited[::step_fft][:100] / (amps_limited.max() + 1e-6)).tolist() # Normalize

        return {
            "status": status,
            "db_level": spl_db,
            "type": sound_type,
            "waveform": wave_pts,
            "fft_frequencies": fft_freq_pts,
            "fft_amplitudes": fft_amp_pts,
            "peak_frequency": round(peak_freq, 1)
        }

def spl_db_scale(db_fs):
    """
    Maps Decibels Full Scale (dBFS, which are negative) to standard Sound Pressure Level (dBSPL).
    """
    # -60 dBFS -> 40 dBSPL (ambient quiet road)
    # 0 dBFS -> 100 dBSPL (very loud crash/siren)
    spl = db_fs + 100
    return max(35.0, min(115.0, spl))