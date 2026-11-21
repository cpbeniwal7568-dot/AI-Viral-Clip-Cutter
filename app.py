import re
import requests
from collections import Counter

API = "https://www.googleapis.com/youtube/v3"


def extract_video_id(url):
    patterns = [
        r"(?:youtube\.com/watch\?v=)([A-Za-z0-9_-]{11})",
        r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/live/)([A-Za-z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError("Valid YouTube Live URL nahi mila.")


def analyze_live_chat(url, api_key):
    video_id = extract_video_id(url)

    response = requests.get(
        f"{API}/videos",
        params={
            "part": "liveStreamingDetails,snippet",
            "id": video_id,
            "key": api_key
        },
        timeout=20
    )
    response.raise_for_status()

    items = response.json().get("items", [])
    if not items:
        raise ValueError("Video nahi mila ya API access available nahi hai.")

    details = items[0].get("liveStreamingDetails", {})
    chat_id = details.get("activeLiveChatId")

    if not chat_id:
        raise ValueError(
            "Active Live Chat nahi mila. Stream live honi chahiye "
            "aur Live Chat enabled hona chahiye."
        )

    response = requests.get(
        f"{API}/liveChat/messages",
        params={
            "part": "snippet,authorDetails",
            "liveChatId": chat_id,
            "maxResults": 200,
            "key": api_key
        },
        timeout=25
    )
    response.raise_for_status()

    messages = []
    for item in response.json().get("items", []):
        snippet = item.get("snippet", {})
        if snippet.get("type") == "textMessageEvent":
            text = snippet.get("textMessageDetails", {}).get(
                "messageText", ""
            )
            messages.append({
                "text": text,
                "published_at": snippet.get("publishedAt", "")
            })

    keywords = [
        "gta", "police", "chase", "clutch",
        "kill", "car", "race", "mission",
        "explosion", "funny", "win"
    ]

    counts = Counter()
    for message in messages:
        text = message["text"].lower()
        for word in keywords:
            if word in text:
                counts[word] += 1

    return {
        "video_id": video_id,
        "messages_count": len(messages),
        "messages": messages,
        "highlights": counts.most_common(10)
    }
    
