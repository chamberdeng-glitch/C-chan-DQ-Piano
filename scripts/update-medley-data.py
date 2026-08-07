#!/usr/bin/env python3
"""Refresh the public medley catalogue from the YouTube Data API."""

from __future__ import annotations

import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"
OUTPUT_FILE = ROOT / "medley-data.json"
API_BASE = "https://www.googleapis.com/youtube/v3"
PLAYLIST_DATA_FILE = ROOT / "playlist-data.js"
SERIES_PATTERN = re.compile(
    r"(?:ドラクエ|ドラゴンクエスト|DQ|Dragon Quest).{0,20}全曲|全曲.{0,20}(?:ドラクエ|ドラゴンクエスト|DQ|Dragon Quest)|Complete Piano",
    re.IGNORECASE,
)
PURPOSE_PATTERN = re.compile(r"作業用BGM|睡眠用BGM", re.IGNORECASE)

TRACK_COUNT_OVERRIDES = {
    "yj95f0WFc-0": 8,
    "IlH4hTSrmUk": 17,
    "Qnpxjoa6Eyw": 23,
    "62ch8sY8DaA": 28,
    "kSOvI-RcJac": 25,
    "daTrvg7jg9k": 26,
    "EofaXaPTK-8": 28,
    "aMaaqQwvwsM": 35,
}

EN_TITLE_OVERRIDES = {
    "T8FJPYoGva0": "Dragon Quest Town & Village Piano Medley",
    "Pu9o2vfflx4": "Dragon Quest Field Piano Medley",
    "yj95f0WFc-0": "Dragon Quest I Complete Piano Medley",
    "IlH4hTSrmUk": "Dragon Quest II Complete Piano Medley",
    "Qnpxjoa6Eyw": "Dragon Quest III Complete Piano Medley",
    "62ch8sY8DaA": "Dragon Quest IV Complete Piano Medley",
    "kSOvI-RcJac": "Dragon Quest V Complete Piano Medley",
    "daTrvg7jg9k": "Dragon Quest VI Complete Piano Medley",
    "EofaXaPTK-8": "Dragon Quest VII Complete Piano Medley",
    "aMaaqQwvwsM": "Dragon Quest VIII Complete Piano Medley",
}


def load_env() -> None:
    if not ENV_FILE.exists():
        return
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value)


def api_get(path: str, api_key: str, **params: object) -> dict:
    params["key"] = api_key
    url = f"{API_BASE}/{path}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": "dqpiano-medley-updater/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def is_medley_playlist(title: str) -> bool:
    return "medley" in title.lower() or "メドレー" in title


def load_medley_page_tracks() -> list[dict]:
    raw = PLAYLIST_DATA_FILE.read_text(encoding="utf-8-sig")
    prefix = "window.playlistData = "
    if not raw.startswith(prefix):
        raise SystemExit(f"Unexpected format: {PLAYLIST_DATA_FILE.name}")
    playlists = json.loads(raw[len(prefix) :].strip().rstrip(";"))
    tracks = []
    seen_video_ids = set()
    for playlist in playlists:
        if not is_medley_playlist(playlist.get("title", "")):
            continue
        for track in playlist.get("tracks", []):
            match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", track.get("url", ""))
            if not match or match.group(1) in seen_video_ids:
                continue
            video_id = match.group(1)
            seen_video_ids.add(video_id)
            tracks.append(
                {
                    **track,
                    "videoId": video_id,
                    "playlistTitle": playlist.get("title", ""),
                }
            )
    return tracks


def fetch_video_details(api_key: str, video_ids: list[str]) -> dict[str, dict]:
    details: dict[str, dict] = {}
    for start in range(0, len(video_ids), 50):
        batch = video_ids[start : start + 50]
        data = api_get(
            "videos",
            api_key,
            part="snippet,statistics,contentDetails",
            id=",".join(batch),
            maxResults=50,
        )
        details.update({item["id"]: item for item in data.get("items", [])})
    return details


def duration_seconds(value: str) -> int:
    match = re.fullmatch(r"P(?:([0-9]+)D)?T(?:([0-9]+)H)?(?:([0-9]+)M)?(?:([0-9]+)S)?", value or "")
    if not match:
        return 0
    days, hours, minutes, seconds = (int(part or 0) for part in match.groups())
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def duration_label(total_seconds: int) -> str:
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def track_count(video_id: str, title: str) -> int | None:
    if video_id in TRACK_COUNT_OVERRIDES:
        return TRACK_COUNT_OVERRIDES[video_id]
    match = re.search(r"(?:全)?([0-9]{1,3})曲", title)
    return int(match.group(1)) if match else None


def category_for(title: str, playlist_title: str) -> str:
    if PURPOSE_PATTERN.search(title):
        return "purpose"
    if "タイトル別" in playlist_title or SERIES_PATTERN.search(title):
        return "series"
    return "scene"


def best_thumbnail(snippet: dict, video_id: str) -> str:
    thumbnails = snippet.get("thumbnails", {})
    for size in ("maxres", "standard", "high", "medium", "default"):
        if thumbnails.get(size, {}).get("url"):
            return thumbnails[size]["url"]
    return f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"


def build_catalog(api_key: str) -> dict:
    source_tracks = load_medley_page_tracks()
    details = fetch_video_details(api_key, [track["videoId"] for track in source_tracks])
    items = []
    for source_track in source_tracks:
        video_id = source_track["videoId"]
        detail = details.get(video_id)
        if not detail:
            continue
        snippet = detail.get("snippet", {})
        title = source_track.get("title") or snippet.get("title", "").strip()
        seconds = duration_seconds(detail.get("contentDetails", {}).get("duration", ""))
        items.append(
            {
                "videoId": video_id,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "title": title,
                "titleEn": EN_TITLE_OVERRIDES.get(video_id, title),
                "category": category_for(title, source_track.get("playlistTitle", "")),
                "trackCount": track_count(video_id, title),
                "duration": duration_label(seconds),
                "durationSeconds": seconds,
                "views": int(detail.get("statistics", {}).get("viewCount", 0)),
                "publishedAt": snippet.get("publishedAt", ""),
                "thumbnail": best_thumbnail(snippet, video_id),
            }
        )

    items.sort(key=lambda item: (-item["views"], item["title"]))
    return {
        "updatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source": "current medley page playlists",
        "count": len(items),
        "items": items,
    }


def main() -> None:
    load_env()
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise SystemExit("YOUTUBE_API_KEY is required")
    catalog = build_catalog(api_key)
    OUTPUT_FILE.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {OUTPUT_FILE.name} with {catalog['count']} videos")


if __name__ == "__main__":
    main()
