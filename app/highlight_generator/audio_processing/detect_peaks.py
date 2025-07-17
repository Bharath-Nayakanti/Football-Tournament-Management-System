import librosa
import numpy as np

def detect_audio_peaks(audio_path, threshold=0.6, min_peak_distance=3.0, frame_size=1024):
    """
    Detects peaks in the audio volume to identify exciting moments.
    Returns timestamps (in seconds) where peaks occur.
    """
    try:
        y, sr = librosa.load(audio_path)
        energy = np.array([
            sum(abs(y[i:i+frame_size]**2))
            for i in range(0, len(y), frame_size)
        ])

        energy = energy / max(energy)  # Normalize
        peaks = np.where(energy > threshold)[0]
        timestamps = peaks * frame_size / sr  # Convert to seconds

        # Merge peaks closer than min_peak_distance
        merged = []
        for ts in timestamps:
            if not merged or ts - merged[-1] > min_peak_distance:
                merged.append(ts)
            else:
                merged[-1] = max(merged[-1], ts)
        
        if not merged:
            print("⚠️ No peaks detected.")

        return merged

    except Exception as e:
        print(f"❌ Error detecting peaks: {e}")
        return []
