#!/usr/bin/env python3
"""Refresh medley view counts from public YouTube watch pages.

This updater intentionally needs no API key, so every site deployment can refresh
the homepage counts without copying a local credential into GitHub Actions.
"""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "medley-data.json"
USER_AGENT = "Mozilla/5.0 (compatible; dqpiano-view-counter/1.0)"


def fetch_view_count(video_id: str) -> int:
    query = urllib.parse.urlencode({"v": video_id, "hl": "en", "gl": "US"})
    request = urllib.request.Request(
        f"https://www.youtube.com/watch?{query}",
        headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        page = response.read().decode("utf-8", errors="replace")

    # Match the target video's own player metadata, not a recommended video's count.
    pattern = re.compile(
        rf'"videoDetails":\{{.*?"videoId":"{re.escape(video_id)}".*?'
        r'"viewCount":"([0-9]+)"',
        re.DOTALL,
    )
    match = pattern.search(page)
    if not match:
        raise ValueError("target video viewCount was not found")
    return int(match.group(1))


def main() -> None:
    catalog = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    items = catalog.get("items", [])
    if not items:
        raise SystemExit("No medley videos were found")

    fetched: dict[str, int] = {}
    failures: list[tuple[str, str]] = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(fetch_view_count, item["videoId"]): item["videoId"]
            for item in items
        }
        for future in as_completed(futures):
            video_id = futures[future]
            try:
                fetched[video_id] = future.result()
            except Exception as error:
                failures.append((video_id, str(error)))

    if failures:
        details = ", ".join(f"{video_id}: {error}" for video_id, error in failures)
        raise SystemExit(f"Failed to refresh {len(failures)} medley view count(s): {details}")

    for item in items:
        # YouTube's public watch pages can be cached briefly. Never replace a newer
        # stored count with an older cached value.
        item["views"] = max(int(item.get("views", 0)), fetched[item["videoId"]])

    items.sort(key=lambda item: (-item["views"], item.get("title", "")))
    catalog["updatedAt"] = (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    )
    DATA_FILE.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Updated view counts for {len(items)} medley videos")


if __name__ == "__main__":
    main()
