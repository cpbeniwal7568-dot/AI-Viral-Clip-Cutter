import re
import requests

def extract_video_id(url):
    patterns = [
        r"(?:youtube\.com/watch\?v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Valid YouTube video URL nahi mila.")

def fetch_comments(video_id, api_key, max_pages=5):
    comments, token = [], None
    for _ in range(max_pages):
        params = {"part": "snippet", "videoId": video_id, "key": api_key,
                  "maxResults": 100, "order": "relevance", "textFormat": "plainText"}
        if token: params["pageToken"] = token
        response = requests.get("https://www.googleapis.com/youtube/v3/commentThreads",
                                params=params, timeout=25)
        if response.status_code == 403:
            raise RuntimeError("YouTube API quota/permissions issue. API key aur quota check karein.")
        response.raise_for_status()
        data = response.json()
        for item in data.get("items", []):
            top = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({"text": top.get("textDisplay", ""),
                             "likes": int(top.get("likeCount", 0)),
                             "replies": int(item["snippet"].get("totalReplyCount", 0))})
        token = data.get("nextPageToken")
        if not token: break
    return comments
