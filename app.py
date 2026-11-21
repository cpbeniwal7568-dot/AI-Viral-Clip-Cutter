
import os
import uuid
import re
import requests
from pathlib import Path

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, send_from_directory, jsonify
)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from modules.youtube_api import extract_video_id, fetch_comments
from modules.comment_analyzer import rank_moments
from modules.video_processor import make_clip, get_duration
from modules.subtitle_generator import generate_srt
from modules.live_chat import analyze_live_chat


load_dotenv()

BASE = Path(__file__).resolve().parent
UPLOAD = BASE / "uploads"
OUTPUT = BASE / "output"

UPLOAD.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)

ALLOWED = {"mp4", "mov", "mkv", "webm"}

app = Flask(__name__)
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "change-this-before-deployment"
)

app.config["MAX_CONTENT_LENGTH"] = (
    int(os.getenv("MAX_UPLOAD_MB", "800")) * 1024 * 1024
)


def allowed_file(name):
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED


@app.get("/")
def index():
    return render_template("index.html")


# NEW: YouTube Live Chat Analysis
@app.post("/analyze-live")
def analyze_live():
    url = request.form.get("youtube_url", "").strip()
    key = os.getenv("YOUTUBE_API_KEY", "")

    if not url:
        return jsonify({
            "error": "YouTube Live URL enter karein."
        }), 400

    if not key:
        return jsonify({
            "error": "YOUTUBE_API_KEY configured nahi hai."
        }), 500

    try:
        result = analyze_live_chat(url, key)

        return jsonify({
            "success": True,
            "video_id": result["video_id"],
            "messages_count": result["messages_count"],
            "highlights": result["highlights"],
            "messages": result["messages"]
        })

    except requests.exceptions.HTTPError as exc:
        return jsonify({
            "error": "YouTube API error: " + str(exc)
        }), 400

    except requests.exceptions.RequestException as exc:
        return jsonify({
            "error": "Network error: " + str(exc)
        }), 502

    except Exception as exc:
        return jsonify({
            "error": str(exc)
        }), 400


# Existing YouTube Comments Analysis
@app.post("/analyze")
def analyze():
    url = request.form.get("youtube_url", "").strip()
    key = os.getenv("YOUTUBE_API_KEY", "")

    if not url:
        flash("YouTube URL enter karein.")
        return redirect(url_for("index"))

    try:
        video_id = extract_video_id(url)

        if not key:
            flash(
                "YOUTUBE_API_KEY set nahi hai. "
                ".env mein API key add karein."
            )
            return redirect(url_for("index"))

        comments = fetch_comments(video_id, key, max_pages=5)
        moments = rank_moments(comments)

        return render_template(
            "dashboard.html",
            video_id=video_id,
            moments=moments,
            comments_count=len(comments)
        )

    except Exception as exc:
        flash(f"Analysis error: {exc}")
        return redirect(url_for("index"))


# Existing Video Clip Processing
@app.post("/process")
def process():
    video = request.files.get("video")

    if not video or not video.filename:
        flash("Pehle apni permitted video file upload karein.")
        return redirect(url_for("index"))

    if not allowed_file(video.filename):
        flash("Supported formats: MP4, MOV, MKV, WEBM.")
        return redirect(url_for("index"))

    try:
        job = uuid.uuid4().hex[:10]
        name = secure_filename(video.filename)
        source = UPLOAD / f"{job}_{name}"

        video.save(source)

        count = max(
            1,
            min(int(request.form.get("count", "5")), 30)
        )

        duration = max(
            5,
            min(int(request.form.get("duration", "30")), 180)
        )

        starts_raw = request.form.get("starts", "").strip()
        starts = []

        for item in starts_raw.split(","):
            item = item.strip()
            if item:
                starts.append(float(item))

        total_duration = get_duration(str(source))

        if not starts:
            last_start = max(0, total_duration - duration)

            if count == 1:
                starts = [0.0]
            else:
                starts = [
                    round(last_start * i / (count - 1), 2)
                    for i in range(count)
                ]

        starts = starts[:count]
        results = []

        for i, start in enumerate(starts, 1):
            out = OUTPUT / f"{job}_clip_{i}.mp4"

            make_clip(
                str(source),
                str(out),
                start,
                duration
            )

            results.append(out.name)

        return render_template(
            "results.html",
            files=results,
            job=job
        )

    except Exception as exc:
        flash(
            f"Processing error: {exc}. "
            "Check FFmpeg installation and video duration."
        )
        return redirect(url_for("index"))


# Existing Subtitle Generator
@app.post("/subtitles")
def subtitles():
    video = request.files.get("video")

    if not video or not video.filename or not allowed_file(video.filename):
        return jsonify({
            "error": "Valid video upload required"
        }), 400

    job = uuid.uuid4().hex[:10]

    source = UPLOAD / f"{job}_{secure_filename(video.filename)}"
    video.save(source)

    try:
        srt_path = generate_srt(
            str(source),
            str(OUTPUT / f"{job}.srt")
        )

        return send_from_directory(
            OUTPUT,
            Path(srt_path).name,
            as_attachment=True
        )

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.get("/output/<path:filename>")
def download(filename):
    return send_from_directory(
        OUTPUT,
        filename,
        as_attachment=True
    )


@app.errorhandler(413)
def too_large(_):
    flash("File upload limit exceed ho gayi. MAX_UPLOAD_MB badhayein.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=False
    )
    
