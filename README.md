
# AI Viral Clip Cutter

A GitHub-ready starter app to analyse publicly available YouTube comment timestamps and create vertical MP4 clips from video files you own or are authorised to edit.

## Features
- YouTube Data API v3 comment retrieval
- Explicit timestamp extraction and ranking
- YouTube Live Chat analysis
- Local video upload
- 9:16 MP4 export using FFmpeg
- Optional Whisper subtitle generation
- Flask web dashboard
- Docker and Render deployment configuration

## Important limitations
Ordinary YouTube comments are not guaranteed to contain playback timestamps. This app only ranks timestamps explicitly written in retrieved comments. Likes/replies are engagement signals, not proof that a specific video moment is popular. Transcript/topic-based moment detection is not yet included in this starter release.

Live Chat analysis requires an active YouTube Live stream with Live Chat enabled. Chat message time is not necessarily the exact time of the video event.

The app does not download YouTube videos or bypass platform restrictions. To cut a video, upload a source file you own or have permission to edit. YouTube API access is subject to API quotas and comment availability.

## Run locally
1. Install Python 3.11+ and FFmpeg.
2. Clone the repository.
3. Create a virtual environment:
   `python -m venv .venv`
4. Activate it and install:
   `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your YouTube Data API v3 key.
6. Run:
   `python app.py`
7. Open `http://localhost:5000`.

## YouTube API key
In Google Cloud Console, create a project, enable **YouTube Data API v3**, create an API key and put it in `.env` as `YOUTUBE_API_KEY`. Restrict the key where practical. Never commit `.env` to GitHub.

## Clip workflow
- Paste a YouTube URL and click Analyse comments.
- Note the ranked timestamps.
- Upload your authorised local source video on the home page.
- Enter start positions in seconds, comma-separated (for example `75, 180, 320`).
- Choose clip count and duration, then generate.
- Download the resulting MP4 files.

If you leave start times blank, the app creates one clip from the beginning. To generate clips at multiple positions, enter their start times.

## Subtitles (optional)
Install `requirements-whisper.txt` and use the Whisper module. Whisper models can be large and CPU-intensive. The current dashboard does not expose subtitle generation as a one-click workflow; the module is available for integration.

## Free hosting notes
Render's free services may sleep, have limited CPU/RAM, ephemeral storage and request timeouts. Video rendering and Whisper may exceed free-tier limits. For reliable processing, run the worker locally or use a paid/appropriately sized worker. Do not rely on ephemeral hosting storage for permanent video files.

## Docker
`docker build -t ai-viral-clip-cutter .`
`docker run --rm -p 5000:5000 --env-file .env ai-viral-clip-cutter`

## Security checklist
- Set a strong `FLASK_SECRET_KEY`.
- Keep `.env` private.
- Add authentication before exposing the dashboard publicly.
- Set upload limits appropriate to your host.
- Delete generated files periodically.
- Only process content you own or are authorised to edit.

## Current scope
This is a functional starter project, not a fully autonomous viral-moment prediction engine. Automatic ranking beyond explicit comment timestamps, face tracking, animated captions, and direct Instagram publishing require additional implementation and platform permissions.

## Deployment update
Flask deployment configuration updated.
Deployment trigger update
