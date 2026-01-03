import subprocess
from pathlib import Path
import random

BASE = Path("assets/finance_psychology")
RAW_CLIPS = BASE / "clips_raw"
OUT_CLIPS = BASE / "clips"

RAW_MUSIC = BASE / "music_raw"
OUT_MUSIC = BASE / "music"

OUT_CLIPS.mkdir(exist_ok=True)
OUT_MUSIC.mkdir(exist_ok=True)

def run(cmd):
    subprocess.run(cmd, check=True)

def process_clips():
    for clip in RAW_CLIPS.glob("*.mp4"):
        out = OUT_CLIPS / clip.name
        if out.exists():
            continue

        cmd = [
            "ffmpeg", "-y",
            "-i", str(clip),
            "-t", "7",
            "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-an",
            str(out)
        ]
        run(cmd)

def process_music():
    for music in RAW_MUSIC.glob("*.m4a"):
        out = OUT_MUSIC / music.name
        if out.exists():
            continue

        cmd = [
            "ffmpeg", "-y",
            "-i", str(music),
            "-t", "15",
            "-c:a", "aac",
            "-b:a", "128k",
            str(out)
        ]
        run(cmd)

if __name__ == "__main__":
    process_clips()
    process_music()
