def generate_srt(video_path, output_path):
    try:
        import whisper
    except ImportError:
        raise RuntimeError("Whisper install nahi hai. pip install -r requirements-whisper.txt karein.")
    model = whisper.load_model("base")
    result = model.transcribe(video_path, fp16=False)
    def stamp(seconds):
        ms = int(seconds * 1000)
        h, rem = divmod(ms, 3600000)
        m, rem = divmod(rem, 60000)
        s, milli = divmod(rem, 1000)
        return f"{h:02}:{m:02}:{s:02},{milli:03}"
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result.get("segments", []), 1):
            f.write(f"{i}\\n{stamp(seg['start'])} --> {stamp(seg['end'])}\\n{seg['text'].strip()}\\n\\n")
    return output_path
