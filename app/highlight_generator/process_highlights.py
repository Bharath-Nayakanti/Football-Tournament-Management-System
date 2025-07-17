import os
import subprocess
from .audio_processing.detect_peaks import detect_audio_peaks
from .video_processing.extract_clips import extract_highlight_clips
from .video_processing.merge_clips import merge_clips
from .video_processing.detect_actions import detect_visual_excitement

def extract_audio(video_path, audio_output_path):
    ffmpeg_path = "/opt/homebrew/bin/ffmpeg"
    cmd = [
        ffmpeg_path,
        '-i', video_path,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '44100',
        '-ac', '2',
        audio_output_path,
        '-y'
    ]
    subprocess.run(cmd, check=True)

def cleanup_temp_files(output_folder):
    temp_files = [
        os.path.join(output_folder, "extracted_audio.wav"),
        os.path.join(output_folder, "highlights", "clips.txt")
    ]

    highlight_folder = os.path.join(output_folder, "highlights")
    if os.path.exists(highlight_folder):
        for file in os.listdir(highlight_folder):
            if file.startswith("clip_") and file.endswith(".mp4"):  # Changed from highlight_ to clip_
                temp_files.append(os.path.join(highlight_folder, file))

    for file in temp_files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception as e:
            print(f"⚠️ Could not delete {file}: {e}")

def generate_highlights(video_path):
    try:
        base_output_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'output')
        os.makedirs(base_output_folder, exist_ok=True)
        
        highlight_folder = os.path.join(base_output_folder, "highlights")
        os.makedirs(highlight_folder, exist_ok=True)

        audio_output_path = os.path.join(base_output_folder, "extracted_audio.wav")
        extract_audio(video_path, audio_output_path)
    
        peak_timestamps = detect_audio_peaks(audio_output_path)
        visual_timestamps = detect_visual_excitement(video_path)

        all_timestamps = sorted(list(set(peak_timestamps + visual_timestamps)))
        
        # Limit number of clips to prevent excessive processing
        max_clips = 50
        if len(all_timestamps) > max_clips:
            all_timestamps = all_timestamps[:max_clips]
            print(f"⚠️ Limiting to {max_clips} highlight clips")

        extract_highlight_clips(video_path, all_timestamps, output_folder=highlight_folder, base_duration=4)
        
        final_output_path = os.path.join(highlight_folder, "final_highlight.mp4")
        success = merge_clips(highlight_folder, final_output_path)

        if success:
            cleanup_temp_files(base_output_folder)
            return final_output_path
        return None

    except Exception as e:
        print(f"❌ Error during highlight generation: {e}")
        return None