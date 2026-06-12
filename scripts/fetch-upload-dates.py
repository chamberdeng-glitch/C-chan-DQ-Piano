"""YouTube動画の公開日(uploadDate)を取得して /tmp/upload-dates.json に保存する。

song-page-content.js を生成するための一回限りの補助スクリプト。
取得済みのIDはスキップするので、中断しても再実行で続きから取れる。
"""
from __future__ import annotations

import importlib.util
import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path('/tmp/upload-dates.json')

_spec = importlib.util.spec_from_file_location('build_seo_pages', ROOT / 'build-seo-pages.py')
seo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(seo)


def video_id(url: str) -> str:
    match = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})', url or '')
    return match.group(1) if match else ''


def fetch_date(vid: str) -> str:
    req = urllib.request.Request(
        f'https://www.youtube.com/watch?v={vid}',
        headers={'User-Agent': 'Mozilla/5.0', 'Accept-Language': 'ja'},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        html = res.read().decode('utf-8', 'ignore')
    match = re.search(r'"uploadDate":"([^"]+)"', html)
    return match.group(1) if match else ''


def main() -> None:
    songs = seo.load_js('song-reference-data.js', 'window.songReferenceData = ')
    dates = json.loads(OUT.read_text()) if OUT.exists() else {}
    todo = []
    for rows in songs.values():
        for row in rows:
            vid = video_id(row.get('videoUrl', ''))
            if vid and row['id'] not in dates:
                todo.append((row['id'], vid))
    print(f'{len(todo)} videos to fetch ({len(dates)} cached)')
    for i, (song_id, vid) in enumerate(todo, 1):
        try:
            dates[song_id] = fetch_date(vid)
        except Exception as exc:
            print(f'ERROR {song_id} {vid}: {exc}')
            dates[song_id] = ''
        if i % 10 == 0 or i == len(todo):
            OUT.write_text(json.dumps(dates, ensure_ascii=False, indent=1))
            print(f'{i}/{len(todo)} done')
        time.sleep(0.4)
    missing = [k for k, v in dates.items() if not v]
    print('missing dates:', missing or 'none')


if __name__ == '__main__':
    main()
