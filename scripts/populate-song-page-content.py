"""song-page-content.js を全曲分に充填する一回限りのスクリプト。

- slug: 英語タイトル(song-title-translations.js)から自動生成。既存エントリのslugは保持。
  シリーズ内で重複した場合は -2, -3 を付ける。
- uploadDate: /tmp/upload-dates.json (scripts/fetch-upload-dates.py の出力) から取り込み。
- lead / description / timestamps: 既存値を保持。なければ空のまま（ビルド側でフォールバック）。

slugはURLそのものなので、一度公開したら変えないこと。このスクリプトは既存slugを
上書きしない。
"""
from __future__ import annotations

import importlib.util
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATES = Path('/tmp/upload-dates.json')

_spec = importlib.util.spec_from_file_location('build_seo_pages', ROOT / 'build-seo-pages.py')
seo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(seo)


def slugify(value: str) -> str:
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-zA-Z0-9]+', '-', value).strip('-').lower()


def main() -> None:
    songs = seo.load_js('song-reference-data.js', 'window.songReferenceData = ')
    titles = seo.load_titles()
    existing = seo.load_js('song-page-content.js', 'window.songPageContent = ')
    dates = json.loads(DATES.read_text()) if DATES.exists() else {}

    out: dict[str, dict] = {}
    for key in seo.SERIES_ORDER:
        rows = sorted(songs[key], key=lambda r: r['sortNumber'])
        used = {meta['slug'] for sid, meta in existing.items()
                if sid.split('-')[0] == key and meta.get('slug')}
        for row in rows:
            if not row.get('videoUrl'):
                continue
            entry = dict(existing.get(row['id'], {}))
            if not entry.get('slug'):
                en = titles['by_id'].get(row['id']) or titles['by_title'].get(row['songTitle'], row['songTitle'])
                base = slugify(en) or row['id'].lower()
                slug = base
                n = 2
                while slug in used:
                    slug = f'{base}-{n}'
                    n += 1
                entry['slug'] = slug
            used.add(entry['slug'])
            if not entry.get('uploadDate'):
                entry['uploadDate'] = dates.get(row['id'], '')
            entry.setdefault('lead', '')
            entry.setdefault('description', '')
            entry.setdefault('timestamps', [])
            out[row['id']] = entry

    body = json.dumps(out, ensure_ascii=False, indent=2)
    (ROOT / 'song-page-content.js').write_text(f'window.songPageContent = {body};\n', encoding='utf-8')
    no_date = [sid for sid, meta in out.items() if not meta['uploadDate']]
    print(f'{len(out)} entries written, missing uploadDate: {no_date or "none"}')


if __name__ == '__main__':
    main()
