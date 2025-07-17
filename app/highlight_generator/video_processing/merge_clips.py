import os
import subprocess
from pathlib import Path

def merge_clips(clips_folder, output_path):
    try:
        clips_folder = os.path.abspath(clips_folder)
        output_path = os.path.abspath(output_path)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Only process files with clip_ prefix
        clips = [f for f in os.listdir(clips_folder) 
                if f.startswith('clip_') and f.endswith('.mp4')]
        
        if not clips:
            print("❌ No clips found to merge.")
            return False

        # Sort clips numerically (clip_1.mp4, clip_2.mp4, etc.)
        def sort_key(filename):
            try:
                return int(filename.split('_')[1].split('.')[0])
            except (IndexError, ValueError):
                return float('inf')  # Put invalid files at end
                
        clips.sort(key=sort_key)

        file_list_path = os.path.join(clips_folder, "clips.txt")
        with open(file_list_path, "w") as f:
            for clip in clips:
                clip_path = os.path.join(clips_folder, clip)
                f.write(f"file '{clip_path.replace("'", "'\\''")}'\n")

        ffmpeg_path = "/opt/homebrew/bin/ffmpeg"
        cmd = [
            ffmpeg_path,
            "-f", "concat",
            "-safe", "0",
            "-i", file_list_path,
            "-c:v", "libx264",
            "-crf", "23",
            "-preset", "fast",
            "-c:a", "aac",
            "-b:a", "192k",
            output_path,
            "-y",
            "-loglevel", "error"
        ]

        print(f"⏳ Merging {len(clips)} clips...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Successfully saved to: {output_path}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg failed (code {e.returncode}):")
        print("Error output:", e.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if 'file_list_path' in locals() and os.path.exists(file_list_path):
            os.remove(file_list_path)