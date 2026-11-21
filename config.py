import os
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "800"))
DEFAULT_CLIP_SECONDS = int(os.getenv("DEFAULT_CLIP_SECONDS", "30"))
