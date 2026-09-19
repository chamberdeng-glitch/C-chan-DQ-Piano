#!/usr/bin/env python3
"""Download YouTube's English-localized thumbnails for the medley catalogue."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "medley-data.json"
OUTPUT_DIR = ROOT / "assets" / "medley-thumbnails"
USER_AGENT = "Mozilla/5.0 (compatible; dqpiano-localized-thumbnail-updater/1.0)"


class LocalizedThumbnailUnavailable(Exception):
    pass


def find_initial_data(html: str) -> dict:
    match = re.search(r"var ytInitialData = ({.*?});</script>", html, re.DOTALL)
    if not match:
        raise ValueError("ytInitialData was not found")
    return json.loads(match.group(1))


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def localized_thumbnail_url(video_id: str, title_en: str) -> str:
    search_terms = [term for term in (title_en, video_id) if term]
    for search_term in dict.fromkeys(search_terms):
        query = urllib.parse.urlencode({"search_query": search_term, "hl": "en", "gl": "US"})
        request = urllib.request.Request(
            f"https://www.youtube.com/results?{query}",
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"},
        )
        with urllib.request.urlopen(request, timeout=45) as response:
            data = find_initial_data(response.read().decode("utf-8", errors="replace"))

        candidates = []
        for node in walk(data):
            if node.get("videoId") != video_id:
                continue
            for thumbnail in node.get("thumbnail", {}).get("thumbnails", []):
                url = thumbnail.get("url", "").replace(r"\u0026", "&")
                if f"/vi_lc/{video_id}/" in url and "_en." in url:
                    candidates.append((int(thumbnail.get("width", 0)), url))
        if candidates:
            return max(candidates)[1]
    raise LocalizedThumbnailUnavailable("not available in YouTube's English results")


def download_one(video_id: str, title_en: str) -> tuple[str, int]:
    url = localized_thumbnail_url(video_id, title_en)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        image = response.read()
    if not image.startswith(b"\xff\xd8"):
        raise ValueError("Downloaded response is not a JPEG")
    target = OUTPUT_DIR / f"{video_id}-en.jpg"
    target.write_bytes(image)
    return video_id, len(image)


def main() -> None:
    catalogue = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    videos = [(item["videoId"], item.get("titleEn", "")) for item in catalogue.get("items", [])]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    failures = []
    unavailable = []
    downloaded = 0
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(download_one, video_id, title_en): video_id
            for video_id, title_en in videos
        }
        for future in as_completed(futures):
            video_id = futures[future]
            try:
                _, size = future.result()
                downloaded += 1
                print(f"Downloaded {video_id}-en.jpg ({size} bytes)")
            except LocalizedThumbnailUnavailable as error:
                unavailable.append(video_id)
                print(f"Unavailable {video_id}: {error}")
            except Exception as error:
                failures.append((video_id, str(error)))
                print(f"Failed {video_id}: {error}")
    if failures:
        raise SystemExit(f"Failed to download {len(failures)} localized thumbnails")
    print(f"Updated {downloaded} English-localized thumbnails; {len(unavailable)} unavailable")


if __name__ == "__main__":
    main()
