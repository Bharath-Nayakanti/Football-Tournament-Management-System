import os
import subprocess

def extract_highlight_clips(video_path, peaks, output_folder, base_duration=4):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    ffmpeg_path = "/opt/homebrew/bin/ffmpeg"
    max_clips = 300  # Safety limit
    
    for i, peak_time in enumerate(peaks[:max_clips]):  # Enforce limit
        try:
            start_time = max(0, peak_time - base_duration/2)
            output_clip_path = os.path.join(output_folder, f"clip_{i+1}.mp4")  # Changed to clip_ prefix

            cmd = [
                ffmpeg_path,
                "-ss", str(start_time),
                "-i", video_path,
                "-t", str(base_duration),
                "-c:v", "libx264",
                "-crf", "23",
                "-preset", "fast",
                "-c:a", "aac",
                "-b:a", "192k",
                "-avoid_negative_ts", "make_zero",
                output_clip_path,
                "-y",
                "-loglevel", "error"
            ]

            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                print(f"✅ Extracted clip at {peak_time:.2f}s")
            else:
                print(f"⚠️ Warning: Clip at {peak_time:.2f}s may not have processed correctly")
                
        except Exception as clip_error:
            print(f"❌ Failed to extract clip at {peak_time:.2f}s: {str(clip_error)}")
            continue