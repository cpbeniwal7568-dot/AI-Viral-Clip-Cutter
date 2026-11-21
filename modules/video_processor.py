import subprocess
from pathlib import Path

def get_duration(source):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
           "-of", "default=noprint_wrappers=1:nokey=1", source]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError("ffprobe failed: " + result.stderr[-800:])
    return float(result.stdout.strip())

def make_clip(source, destination, start, duration):
    if start < 0 or duration <= 0:
        raise ValueError("Start time/duration invalid.")
    Path(destination).parent.mkdir(parents=True, exist_ok=True)
    vf = ("scale=1080:1920:force_original_aspect_ratio=increase,"
          "crop=1080:1920,setsar=1")
    cmd = ["ffmpeg", "-y", "-ss", str(start), "-i", source, "-t", str(duration),
           "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", destination]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-1200:])
    return destination
