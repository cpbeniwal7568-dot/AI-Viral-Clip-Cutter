import re
from collections import defaultdict

# Extract explicit video-position timestamps such as 1:25 or 01:02:15.
TIME_RE = re.compile(r"(?<!\d)(\d{1,2}):([0-5]\d)(?::([0-5]\d))?(?!\d)")

def parse_time(match):
    a, b, c = match.groups()
    if c is None:
        return int(a) * 60 + int(b)
    return int(a) * 3600 + int(b) * 60 + int(c)

def rank_moments(comments, bucket_seconds=15):
    buckets = defaultdict(lambda: {"mentions": 0, "likes": 0, "replies": 0, "examples": []})
    for comment in comments:
        text = comment.get("text", "")
        for match in TIME_RE.finditer(text):
            seconds = parse_time(match)
            key = (seconds // bucket_seconds) * bucket_seconds
            row = buckets[key]
            row["mentions"] += 1
            row["likes"] += comment.get("likes", 0)
            row["replies"] += comment.get("replies", 0)
            if len(row["examples"]) < 2:
                row["examples"].append(text[:180])
    ranked = []
    for seconds, row in buckets.items():
        score = row["mentions"] * 5 + row["likes"] * 0.5 + row["replies"] * 1.5
        ranked.append({"seconds": seconds, "time": f"{seconds//60:02d}:{seconds%60:02d}",
                       "score": round(score, 1), **row})
    return sorted(ranked, key=lambda x: x["score"], reverse=True)
