from __future__ import annotations
import json
import re
from pathlib import Path

BASE = 'https://dqpiano.com'
ROOT = Path(__file__).resolve().parent
JA_LIBRARY_NAME = 'ドラゴンクエスト ピアノ演奏・BGMライブラリー'
EN_LIBRARY_NAME = 'Dragon Quest Piano Music Library'

SERIES = [
    ('I', 'dq1', 'ドラゴンクエストI', 'Dragon Quest I', 'DQ1'),
    ('II', 'dq2', 'ドラゴンクエストII', 'Dragon Quest II', 'DQ2'),
    ('III', 'dq3', 'ドラゴンクエストIII', 'Dragon Quest III', 'DQ3'),
    ('IV', 'dq4', 'ドラゴンクエストIV', 'Dragon Quest IV', 'DQ4'),
    ('V', 'dq5', 'ドラゴンクエストV', 'Dragon Quest V', 'DQ5'),
    ('VI', 'dq6', 'ドラゴンクエストVI', 'Dragon Quest VI', 'DQ6'),
    ('VII', 'dq7', 'ドラゴンクエストVII', 'Dragon Quest VII', 'DQ7'),
    ('VIII', 'dq8', 'ドラゴンクエストVIII', 'Dragon Quest VIII', 'DQ8'),
    ('IX', 'dq9', 'ドラゴンクエストIX', 'Dragon Quest IX', 'DQ9'),
    ('X', 'dq10', 'ドラゴンクエストX', 'Dragon Quest X', 'DQ10'),
    ('XI', 'dq11', 'ドラゴンクエストXI', 'Dragon Quest XI', 'DQ11'),
]
SERIES_MAP = {k: {'slug': slug, 'ja': ja, 'en': en, 'code': code} for k, slug, ja, en, code in SERIES}
SERIES_ORDER = [key for key, *_ in SERIES]

SPECIAL_COLLECTIONS = {
    'X': [
        {'sourceId': 'IV-2', 'songTitle': 'インテルメッツォ'},
        {'sourceId': 'IV-17'},
        {'sourceId': 'VIII-14', 'songTitle': 'この想いを…'},
        {'sourceId': 'VIII-26'},
        {'sourceId': 'VIII-18', 'songTitle': '急げ！ピンチだ'},
        {'sourceId': 'VII-19'},
        {'sourceId': 'V-7'},
        {'sourceId': 'IV-18'},
        {'sourceId': 'VIII-5'},
        {'sourceId': 'VIII-12'},
        {'sourceId': 'IX-21'},
        {'sourceId': 'VIII-25'},
        {'sourceId': 'IV-11'},
        {'sourceId': 'II-2'},
    ],
    'XI': [
        {'sourceId': 'I-3'},
        {'sourceId': 'III-9'},
        {'sourceId': 'III-5'},
        {'sourceId': 'III-14'},
        {'sourceId': 'III-15'},
        {'sourceId': 'III-22'},
        {'sourceId': 'IV-20'},
        {'sourceId': 'V-17'},
        {'sourceId': 'V-16'},
        {'sourceId': 'V-22'},
        {'sourceId': 'V-3'},
        {'sourceId': 'VI-6'},
        {'sourceId': 'VI-11'},
        {'sourceId': 'VII-23'},
        {'sourceId': 'VII-6'},
        {'sourceId': 'VIII-30'},
        {'sourceId': 'X-17'},
    ],
}

SCORE_LIBRARY = [
    {
        'slug': 'best-album',
        'ja': 'ドラゴンクエスト オフィシャル・ベスト・アルバム',
        'en': 'Dragon Quest Official Best Album',
        'amazonUrl': 'https://www.amazon.co.jp/%E3%83%94%E3%82%A2%E3%83%8E%E6%9B%B2%E9%9B%86-%E3%83%89%E3%83%A9%E3%82%B4%E3%83%B3%E3%82%AF%E3%82%A8%E3%82%B9%E3%83%88-%E3%82%AA%E3%83%95%E3%82%A3%E3%82%B7%E3%83%A3%E3%83%AB%E3%83%BB%E3%83%99%E3%82%B9%E3%83%88%E3%83%BB%E3%82%A2%E3%83%AB%E3%83%90%E3%83%A0-%E6%A5%BD%E8%AD%9C-%E3%81%99%E3%81%8E%E3%82%84%E3%81%BE%E3%81%93%E3%81%86%E3%81%84%E3%81%A1/dp/4773243848',
        'cover': '/assets/score-best-album-cover.jpg',
        'sourceIds': [
            'I-2', 'I-3', 'I-4', 'I-7', 'I-8',
            'II-2', 'II-4', 'II-5', 'II-9', 'II-8', 'II-16',
            'III-3', 'III-9', 'III-10', 'III-14', 'III-17', 'III-23',
            'IV-2', 'IV-3', 'IV-5', 'IV-12', 'IV-16', 'IV-19', 'IV-20',
            'V-3', 'V-4', 'V-9', 'V-11', 'V-18', 'V-24', 'V-25',
            'VI-3', 'VI-8', 'VI-11', 'VI-13', 'VI-19', 'VI-20', 'VI-26',
            'VII-9', 'VII-10', 'VII-7', 'VII-11', 'VII-19', 'VII-20', 'VII-24', 'VII-28',
            'VIII-4', 'VIII-6', 'VIII-10', 'VIII-14', 'VIII-21', 'VIII-30', 'VIII-35',
            'IX-3', 'IX-5', 'IX-8', 'IX-10', 'IX-13', 'IX-19', 'IX-30',
            'X-2', 'X-12', 'X-14', 'X-15', 'X-16', 'X-17', 'X-21', 'X-22', 'X-23',
            'XI-1', 'XI-4', 'XI-5', 'XI-12', 'XI-7', 'XI-21', 'XI-23', 'XI-24',
        ],
    },
]

CATS = {
    'opening': {'ja': '\u30aa\u30fc\u30d7\u30cb\u30f3\u30b0', 'en': 'Opening', 'match': ['\u30aa\u30fc\u30d7\u30cb\u30f3\u30b0']},
    'prologue': {'ja': '\u30d7\u30ed\u30ed\u30fc\u30b0', 'en': 'Prologue', 'match': ['\u30d7\u30ed\u30ed\u30fc\u30b0']},
    'interlude': {'ja': '\u5834\u9762\u8ee2\u63db', 'en': 'Interlude', 'match': ['\u5834\u9762\u8ee2\u63db']},
    'field': {'ja': '\u30d5\u30a3\u30fc\u30eb\u30c9', 'en': 'Field', 'match': ['\u30d5\u30a3\u30fc\u30eb\u30c9']},
    'sea': {'ja': '\u6d77', 'en': 'Sea', 'match': ['\u6d77']},
    'sky': {'ja': '\u7a7a', 'en': 'Sky', 'match': ['\u7a7a']},
    'town-village': {'ja': '\u8857\u30fb\u6751', 'en': 'Towns & Villages', 'match': ['\u8857\u30fb\u6751']},
    'castle': {'ja': '\u57ce', 'en': 'Castle', 'match': ['\u57ce']},
    'church-shrine': {'ja': '\u6559\u4f1a\u30fb\u307b\u3053\u3089', 'en': 'Churches & Shrines', 'match': ['\u6559\u4f1a\u30fb\u307b\u3053\u3089']},
    'casino': {'ja': '\u30ab\u30b8\u30ce', 'en': 'Casino', 'match': ['\u30ab\u30b8\u30ce']},
    'dungeon': {'ja': '\u30c0\u30f3\u30b8\u30e7\u30f3', 'en': 'Dungeon', 'match': ['\u30c0\u30f3\u30b8\u30e7\u30f3']},
    'tower': {'ja': '\u5854', 'en': 'Tower', 'match': ['\u5854']},
    'event': {'ja': '\u30a4\u30d9\u30f3\u30c8', 'en': 'Event', 'match': ['\u30a4\u30d9\u30f3\u30c8']},
    'character-theme': {'ja': '\u30ad\u30e3\u30e9\u30af\u30bf\u30fc\u30c6\u30fc\u30de', 'en': 'Character Theme', 'match': ['\u30ad\u30e3\u30e9\u30af\u30bf\u30fc\u30c6\u30fc\u30de']},
    'normal-battle': {'ja': '\u901a\u5e38\u6226\u95d8', 'en': 'Normal Battle', 'match': ['\u901a\u5e38\u6226\u95d8']},
    'boss-battle': {'ja': '\u30dc\u30b9\u6226\u95d8', 'en': 'Boss Battle', 'match': ['\u30dc\u30b9\u6226\u95d8']},
    'ending': {'ja': '\u30a8\u30f3\u30c7\u30a3\u30f3\u30b0', 'en': 'Ending', 'match': ['\u30a8\u30f3\u30c7\u30a3\u30f3\u30b0']},
    'game-over': {'ja': '\u5168\u6ec5', 'en': 'Game Over', 'match': ['\u5168\u6ec5']},
    'medley': {'ja': '\u30e1\u30c9\u30ec\u30fc', 'en': 'Medleys', 'match': []},
}

CAT_EN = {
    'イベント': 'Event',
    'エンディング': 'Ending',
    'オープニング': 'Opening',
    'カジノ': 'Casino',
    'キャラクターテーマ': 'Character Theme',
    'ダンジョン': 'Dungeon',
    'フィールド': 'Field',
    'プロローグ': 'Prologue',
    'ボス戦闘': 'Boss Battle',
    '全滅': 'Game Over',
    '城': 'Castle',
    '場面転換': 'Interlude',
    '塔': 'Tower',
    '教会・ほこら': 'Churches & Shrines',
    '海': 'Sea',
    '空': 'Sky',
    '街・村': 'Towns & Villages',
    '通常戦闘': 'Normal Battle',
}

DIFF_EN = {
    '初級': 'Beginner',
    '初中級': 'Beginner-Intermediate',
    '中級': 'Intermediate',
    '中上級': 'Upper-Intermediate',
    '上級': 'Advanced',
    '未設定': 'Not set',
}

LOCAL_PREVIEW = """<script>
(() => {
  if (location.protocol !== 'file:') return;
  const mapAsset = (value) => {
    if (!value || !value.startsWith('/') || value.startsWith('//')) return value;
    const clean = value.replace(/^\//, '');
    const root = location.href.replace(/[^/]*$/, '');
    if (!clean) return root;
    if (clean.endsWith('/')) return new URL(clean + 'index.html', root).href;
    return new URL(clean, root).href;
  };
  const rewrite = () => {
    document.querySelectorAll('a[href^="/"]').forEach((node) => {
      node.setAttribute('href', mapAsset(node.getAttribute('href')));
    });
    document.querySelectorAll('link[href^="/"]').forEach((node) => {
      node.setAttribute('href', mapAsset(node.getAttribute('href')));
    });
    document.querySelectorAll('img[src^="/"]').forEach((node) => {
      node.setAttribute('src', mapAsset(node.getAttribute('src')));
    });
  };
  rewrite();
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href]');
    if (!link) return;
    const raw = link.getAttribute('href');
    if (!raw || !raw.startsWith('/')) return;
    event.preventDefault();
    location.href = mapAsset(raw);
  }, true);
  new MutationObserver(rewrite).observe(document.documentElement, { childList: true, subtree: true });
})();
</script>"""


def load_js(filename: str, prefix: str):
    raw = (ROOT / filename).read_text(encoding='utf-8-sig')
    return json.loads(raw[len(prefix):].strip().rstrip(';'))


def load_titles():
    raw = (ROOT / 'song-title-translations.js').read_text(encoding='utf-8-sig')
    by_id_match = re.search(r'en:\s*\{\s*titlesById:\s*(\{.*?\})\s*,\s*titles:', raw, re.S)
    titles_match = re.search(r'en:\s*\{\s*titlesById:\s*\{.*?\}\s*,\s*titles:\s*(\{.*?\})\s*,\s*categories:', raw, re.S)
    return {
        'by_id': json.loads(by_id_match.group(1)) if by_id_match else {},
        'by_title': json.loads(titles_match.group(1)) if titles_match else {},
    }


def esc(value=''):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def infer_series(title: str) -> str:
    match = re.search(r'DRAGON QUEST\s*(XI|X|IX|VIII|VII|VI|V|IV|III|II|I)\b', title.upper())
    return match.group(1) if match else ''


def is_medley(title: str) -> bool:
    lowered = title.lower()
    return 'medley' in lowered or 'メドレー' in title


def normalize_thumb(src: str | None) -> str:
    if not src:
        return ''
    if src.startswith(('http://', 'https://')):
        return src
    return '/' + src.lstrip('./').lstrip('/')


def youtube_video_thumb(url: str | None) -> str:
    if not url:
        return ''
    match = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})', url)
    if not match:
        return ''
    return f'https://i.ytimg.com/vi/{match.group(1)}/hqdefault.jpg'


def youtube_video_id(url: str | None) -> str:
    match = re.search(r'(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})', url or '')
    return match.group(1) if match else ''


def youtube_start_seconds(url: str | None) -> int:
    """videoUrl の t= / start= パラメータを秒に変換する(例 t=540s, t=1h2m3s)。"""
    match = re.search(r'[?&#](?:t|start)=(\d+h)?(\d+m)?(\d+s?)?(?=[&#]|$)', url or '')
    if not match or not any(match.groups()):
        return 0
    hours, minutes, seconds = (int(g.rstrip('hms')) if g else 0 for g in match.groups())
    return hours * 3600 + minutes * 60 + seconds


# 曲別ページを持つ曲のID -> ページパス。build() 冒頭で song-page-content.js から作る。
SONG_PAGE_PATHS: dict[str, str] = {}

# 動画サイトマップ用エントリ。ページURL(canonical) -> video メタ。write_song_pageで登録。
SONG_VIDEO_ENTRIES: dict[str, dict] = {}


def make_head(lang: str, title: str, desc: str, canon: str, ja_href: str, en_href: str, graph: list[dict]) -> str:
    locale = 'ja_JP' if lang == 'ja' else 'en_US'
    html_lang = 'ja' if lang == 'ja' else 'en'
    analytics_tag = (
        '<!-- Google tag (gtag.js) -->'
        '<script async src="https://www.googletagmanager.com/gtag/js?id=G-S51EBHNVZ3"></script>'
        '<script>'
        'window.dataLayer = window.dataLayer || [];'
        'function gtag(){dataLayer.push(arguments);}'
        "gtag('js', new Date());"
        "gtag('config', 'G-S51EBHNVZ3');"
        '</script>'
        '<script src="/analytics.js" defer></script>'
    )
    return (
        '<!DOCTYPE html>'
        f'<html lang="{html_lang}"><head>'
        f'{analytics_tag}'
        '<meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f'<title>{esc(title)}</title>'
        f'<meta name="description" content="{esc(desc)}">'
        '<meta name="robots" content="index, follow">'
        f'<link rel="canonical" href="{canon}">'
        f'<link rel="alternate" hreflang="ja" href="{ja_href}">'
        f'<link rel="alternate" hreflang="en" href="{en_href}">'
        f'<link rel="alternate" hreflang="x-default" href="{ja_href}">'
        f'<meta property="og:title" content="{esc(title)}">'
        f'<meta property="og:description" content="{esc(desc)}">'
        '<meta property="og:type" content="website">'
        f'<meta property="og:locale" content="{locale}">'
        f'<meta property="og:url" content="{canon}">'
        '<meta name="twitter:card" content="summary_large_image">'
        f'<meta name="twitter:title" content="{esc(title)}">'
        f'<meta name="twitter:description" content="{esc(desc)}">'
        '<link rel="stylesheet" href="/styles.css?v=20260625-2">'
        f'{LOCAL_PREVIEW}'
        f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)}</script>'
        '</head>'
    )


def website_json(lang: str) -> dict:
    if lang == 'ja':
        return {
            '@type': 'WebSite',
            '@id': BASE + '/#website',
            'name': JA_LIBRARY_NAME,
            'url': BASE + '/',
            'inLanguage': 'ja',
        }
    return {
        '@type': 'WebSite',
        '@id': BASE + '/en/#website',
        'name': EN_LIBRARY_NAME,
        'url': BASE + '/en/',
        'inLanguage': 'en',
    }


def breadcrumbs(items: list[tuple[str, str]]) -> str:
    parts = []
    for i, (label, href) in enumerate(items):
        if i == len(items) - 1:
            parts.append(f'<span aria-current="page">{esc(label)}</span>')
        else:
            parts.append(f'<a href="{href}">{esc(label)}</a>')
    return '<nav class="breadcrumbs" aria-label="Breadcrumb">' + '<span> / </span>'.join(parts) + '</nav>'


def breadcrumb_json(items: list[tuple[str, str]]) -> dict:
    elements = []
    for i, (label, href) in enumerate(items, start=1):
        row = {
            '@type': 'ListItem',
            'position': i,
            'name': label,
            'item': BASE + href if href.startswith('/') else href,
        }
        elements.append(row)
    return {'@type': 'BreadcrumbList', 'itemListElement': elements}


def music_playlist_json(lang: str, title: str, desc: str, page: str, rows: list[dict]) -> dict:
    tracks = []
    for row in rows:
        recording = {
            '@type': 'MusicRecording',
            'name': row['songTitle'] if lang == 'ja' else row['songTitleEn'],
            'identifier': row['id'],
        }
        if row.get('videoUrl'):
            recording['url'] = row['videoUrl']
        tracks.append(recording)
    return {
        '@type': 'MusicPlaylist',
        'name': title,
        'description': desc,
        'url': BASE + page,
        'inLanguage': 'ja-JP' if lang == 'ja' else 'en-US',
        'numTracks': len(tracks),
        'track': tracks,
    }


def topbar(lang: str, current: str, alt: str) -> str:
    is_home = current in ('/', '/en/')
    ja_brand = f'<a class="brand" href="/" aria-label="{JA_LIBRARY_NAME} ホーム"><img class="brand-logo" src="/assets/channel-logo.jpg" alt="" width="64" height="64"><span class="brand-text">{JA_LIBRARY_NAME}</span></a>'
    en_brand = f'<a class="brand" href="/en/" aria-label="{EN_LIBRARY_NAME} home"><img class="brand-logo" src="/assets/channel-logo.jpg" alt="" width="64" height="64"><span class="brand-text">{EN_LIBRARY_NAME}</span></a>'
    if lang == 'ja':
        home_link = '' if is_home else '<a class="topbar-home" href="/">ホーム</a>'
        return (
            '<nav class="topbar" aria-label="主要ナビゲーション">'
            f'{ja_brand}{home_link}'
            '<div class="topbar-right"><div class="topbar-links">'
            '<a href="/series-index/">作品別ページ</a>'
            '<a class="topbar-shortcut" href="/category-index/">カテゴリ別ページ</a>'
            '<a class="topbar-cta" href="https://www.youtube.com/@chamberd_piano" target="_blank" rel="noreferrer">YouTubeチャンネルを見る</a>'
            '</div><div class="language-switch" aria-label="言語切り替え">'
            f'<a class="lang-pill is-active" href="{current}">日本語</a>'
            f'<a class="lang-pill" href="{alt}">English</a>'
            '</div></div></nav>'
        )
    home_link = '' if is_home else '<a class="topbar-home" href="/en/">Home</a>'
    return (
        '<nav class="topbar" aria-label="Primary navigation">'
        f'{en_brand}{home_link}'
        '<div class="topbar-right"><div class="topbar-links">'
        '<a href="/en/series-index/">Browse by Series</a>'
        '<a class="topbar-shortcut" href="/en/category-index/">Browse by Category</a>'
        '<a class="topbar-cta" href="https://www.youtube.com/@chamberd_piano" target="_blank" rel="noreferrer">Visit the YouTube channel</a>'
        '</div><div class="language-switch" aria-label="Language switch">'
        f'<a class="lang-pill" href="{alt}">日本語</a>'
        f'<a class="lang-pill is-active" href="{current}">English</a>'
        '</div></div></nav>'
    )


def metric(label: str, value: str) -> str:
    return f'<div><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>'


def action(href: str, label: str, primary: bool = False, external: bool = False) -> str:
    cls = 'video-link page-action is-primary' if primary else 'video-link page-action'
    rel = ' rel="noreferrer"' if external else ''
    target = ' target="_blank"' if external else ''
    return f'<a class="{cls}" href="{href}"{target}{rel}>{esc(label)}</a>'


def entry_card(href: str, title: str, body: str, meta: str = '', thumb: str = '') -> str:
    extra = f'<span class="entry-card-meta">{esc(meta)}</span>' if meta else ''
    thumb_html = f'<img class="entry-card-thumb" src="{thumb}" alt="{esc(title)}" loading="lazy">' if thumb else ''
    return f'<a class="entry-card" href="{href}">{thumb_html}<span class="entry-card-title">{esc(title)}</span><span class="entry-card-body">{esc(body)}</span>{extra}</a>'


def entry_grid(cards: list[str]) -> str:
    return '<div class="entry-link-grid">' + ''.join(cards) + '</div>'


def playlist_cards(items: list[dict], lang: str, hero: bool = False) -> str:
    wrap = 'seo-card-grid seo-card-grid-hero' if hero else 'seo-card-grid'
    body = []
    for playlist in items:
        thumb = normalize_thumb(playlist.get('thumbnail'))
        thumb_html = f'<img class="playlist-thumb" src="{thumb}" alt="{esc(playlist["title"])}" loading="lazy">' if thumb else ''
        count = playlist.get('itemCountText') or ''
        desc = playlist.get('description') or ''
        link_label = 'プレイリストを開く' if lang == 'ja' else 'Open playlist'
        body.append(
            '<article class="video-card video-card-grid seo-card">'
            f'{thumb_html}'
            f'<p class="video-meta">{esc(count)}</p>'
            f'<h3>{esc(playlist["title"])}</h3>'
            f'{f"<p>{esc(desc)}</p>" if desc else ""}'
            f'<a class="video-link" href="{playlist["url"]}" target="_blank" rel="noreferrer">{link_label}</a>'
            '</article>'
        )
    return f'<div class="{wrap}">' + ''.join(body) + '</div>'


def medley_video_cards(items: list[dict], lang: str) -> str:
    body = []
    for item in items:
        thumb = normalize_thumb(item.get('thumbnail'))
        thumb_html = f'<img class="playlist-thumb" src="{thumb}" alt="{esc(item["title"])}" loading="lazy">' if thumb else ''
        link_label = '動画を開く' if lang == 'ja' else 'Open video'
        body.append(
            '<article class="video-card video-card-grid seo-card">'
            f'{thumb_html}'
            f'<p class="video-meta">{esc(item["playlistTitle"])}</p>'
            f'<h3>{esc(item["title"])}</h3>'
            f'<a class="video-link" href="{item["url"]}" target="_blank" rel="noreferrer">{link_label}</a>'
            '</article>'
        )
    return '<div class="seo-card-grid">' + ''.join(body) + '</div>'


def hero_playlist_thumb(playlist: dict, lang: str) -> str:
    thumb = normalize_thumb(playlist.get('thumbnail'))
    if not thumb:
        return ''
    label = '\u4f5c\u54c1\u5225\u30dd\u30c3\u30c9\u30ad\u30e3\u30b9\u30c8' if lang == 'ja' else 'Series podcast'
    count = playlist.get('itemCountText') or ''
    title = playlist.get('title') or ''
    count_html = f'<p class="video-meta">{esc(count)}</p>' if count else ''
    title_html = f'<p class="hero-playlist-title">{esc(title)}</p>' if title else ''
    return (
        '<aside class="hero-playlist-thumb">'
        f'<p class="hero-playlist-kicker">{esc(label)}</p>'
        f'<a class="hero-playlist-image-link" href="{playlist["url"]}" target="_blank" rel="noreferrer">'
        f'<img class="hero-playlist-image" src="{thumb}" alt="{esc(title)}" loading="lazy">'
        '</a>'
        '<div class="hero-playlist-meta">'
        f'{count_html}'
        f'{title_html}'
        '</div>'
        '</aside>'
    )


def song_table(rows: list[dict], lang: str, song_content: dict | None = None) -> str:
    headers = ('曲番号', '曲名', 'カテゴリ', '難易度') if lang == 'ja' else ('No.', 'Title', 'Category', 'Difficulty')
    body = []
    for row in rows:
        title = row['songTitle'] if lang == 'ja' else row['songTitleEn']
        category = row['category'] if lang == 'ja' else row['categoryEn']
        difficulty = (row.get('difficultyLabel') or '未設定') if lang == 'ja' else (row.get('difficultyEn') or 'Not set')
        difficulty_stars = row.get('difficultyStars')
        meta = (song_content or {}).get(row['id'], {})
        duration = meta.get('performanceDuration', '')
        page_path = SONG_PAGE_PATHS.get(row['id'])
        if page_path and lang == 'en':
            page_path = '/en' + page_path
        if page_path:
            title_html = f'<a class="song-link" href="{page_path}">{esc(title)}</a>'
            number_html = f'<a class="song-link song-number-link" href="{page_path}">{esc(row["id"])}</a>'
        elif row.get('videoUrl'):
            title_html = f'<a class="song-link" href="{row["videoUrl"]}" target="_blank" rel="noreferrer">{esc(title)}</a>'
            number_html = f'<a class="song-link song-number-link" href="{row["videoUrl"]}" target="_blank" rel="noreferrer">{esc(row["id"])}</a>'
        else:
            title_html = esc(title)
            number_html = esc(row['id'])
        body.append(
            '<tr>'
            f'<td data-label="{esc(headers[0])}">{number_html}</td>'
            f'<td data-label="{esc(headers[1])}">{title_html}</td>'
            f'<td data-label="{esc(headers[2])}">{esc(category)}</td>'
            f'<td data-label="{esc(headers[3])}">{render_difficulty_html(difficulty, difficulty_stars, duration, lang)}</td>'
            '</tr>'
        )
    return (
        '<div class="song-table-wrap seo-song-table-wrap"><div class="song-table-scroll">'
        '<table class="song-table"><thead><tr>'
        f'<th>{headers[0]}</th><th>{headers[1]}</th><th>{headers[2]}</th><th>{headers[3]}</th>'
        '</tr></thead><tbody>' + ''.join(body) + '</tbody></table></div></div>'
    )


def render_difficulty_html(label: str, stars: int | None, duration: str = '', lang: str = 'ja') -> str:
    filled = max(0, min(5, stars)) if isinstance(stars, int) else 0
    empty = 5 - filled
    star_text = ('★' * filled) + ('☆' * empty)
    extra_class = ' is-empty' if filled == 0 else ''
    aria = f'{label} {filled}/5' if filled else label
    duration_label = '演奏時間' if lang == 'ja' else 'Duration'
    duration_html = (
        '<span class="performance-duration">'
        f'<span class="performance-duration-label">{esc(duration_label)}</span>'
        f'<span class="performance-duration-value">{esc(duration)}</span>'
        '</span>'
    ) if duration else ''
    return (
        '<span class="difficulty-cell">'
        '<span class="difficulty-main">'
        f'<span class="difficulty-text">{esc(label)}</span>'
        f'<span class="difficulty-stars{extra_class}" aria-label="{esc(aria)}">{star_text}</span>'
        '</span>'
        f'{duration_html}'
        '</span>'
    )


def section(kicker: str, title: str, inner: str, copy: str = '') -> str:
    copy_html = f'<p class="section-copy">{esc(copy)}</p>' if copy else ''
    return (
        '<section class="section">'
        '<div class="section-heading">'
        f'<p class="section-kicker">{esc(kicker)}</p>'
        f'<h2>{esc(title)}</h2>'
        f'{copy_html}'
        '</div>'
        f'{inner}'
        '</section>'
    )


def shell(lang: str, current: str, alt: str, crumb_html: str, title: str, lead: str, metrics_html: str, actions_html: str, feature_html: str, main: str) -> str:
    footer = '© しーちゃんピアノ' if lang == 'ja' else '© C-chan piano'
    feature_block = f'<div class="page-hero-feature">{feature_html}</div>' if feature_html else ''
    return (
        '<body><div class="site-bg" aria-hidden="true"></div>'
        f'<header class="hero hero-simple">{topbar(lang, current, alt)}'
        '<section class="page-hero seo-hero-panel">'
        '<div class="seo-hero-copy">'
        f'{crumb_html}'
        f'<p class="eyebrow">{"Dragon Quest Piano Library" if lang == "ja" else "Dragon Quest Piano Library"}</p>'
        f'<h1>{esc(title)}</h1>'
        f'<p class="lead">{esc(lead)}</p>'
        f'<dl class="hero-metrics page-hero-metrics">{metrics_html}</dl>'
        f'<div class="page-hero-actions">{actions_html}</div>'
        '</div>'
        f'{feature_block}'
        '</section></header>'
        f'<main class="page seo-page">{main}</main>'
        f'<footer class="seo-footer"><p>{footer}</p></footer></body></html>'
    )


def write(path: str | Path, content: str) -> None:
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding='utf-8')


BOOK_TONES = ['green', 'wine', 'navy', 'brown', 'purple', 'olive']


def book_spine_card(href: str, title: str, body: str, tone_index: int, code: str = '', icon: str = '', variant: str = 'series') -> str:
    code_html = f'<span class="book-spine-code">{esc(code)}</span>' if code else ''
    icon_html = f'<span class="book-spine-icon" aria-hidden="true">{esc(icon)}</span>' if icon else ''
    link_label = f'{title} {code}'.strip() if code else title
    return (
        f'<a class="book-spine book-spine-{esc(variant)} tone-{BOOK_TONES[tone_index % len(BOOK_TONES)]}" style="--book-index:{tone_index}" href="{esc(href)}" aria-label="{esc(link_label)}">'
        '<span class="book-spine-ornament" aria-hidden="true"></span>'
        f'<span class="book-spine-title">{esc(title)}</span> '
        f'{icon_html}'
        f'{code_html}'
        f'<span class="book-spine-subtitle">{esc(body)}</span>'
        '</a>'
    )


def book_shelf(cards: list[str], label: str, variant: str) -> str:
    return (
        f'<div class="bookcase-scroll bookcase-scroll-{esc(variant)}" aria-label="{esc(label)}">'
        f'<div class="bookcase-shelf bookcase-shelf-{esc(variant)}">'
        f'{"".join(cards)}'
        '</div>'
        '</div>'
    )


def score_cards(lang: str) -> list[str]:
    cards = []
    for index, score in enumerate(SCORE_LIBRARY):
        href = f'/score/{score["slug"]}/' if lang == 'ja' else f'/en/score/{score["slug"]}/'
        title = 'ベストアルバム' if lang == 'ja' else 'Best Album'
        body = '楽譜別ページ' if lang == 'ja' else 'Score page'
        cards.append(book_spine_card(href, title, body, index, icon='♪', variant='score'))
    return cards


CATEGORY_LIBRARY = [
    ('opening', 'オープニング', 'Opening', '◇'),
    ('prologue', 'プロローグ', 'Prologue', '♩'),
    ('interlude', '場面転換', 'Transition', '↔'),
    ('field', 'フィールド', 'Field', '♪'),
    ('sea', '海', 'Ocean', '〜'),
    ('sky', '空', 'Sky', '◇'),
    ('town-village', '街・村', 'Town & Village', '⌂'),
    ('castle', '城', 'Castle', '⌂'),
    ('church-shrine', '教会・ほこら', 'Church & Shrine', '◇'),
    ('casino', 'カジノ', 'Casino', '♬'),
    ('dungeon', 'ダンジョン', 'Dungeon', '◇'),
    ('tower', '塔', 'Tower', '⌂'),
    ('event', 'イベント', 'Event', '◇'),
    ('character-theme', 'キャラクターテーマ', 'Character', '♩'),
    ('normal-battle', '通常戦闘', 'Regular Battle', '♬'),
    ('boss-battle', 'ボス戦闘', 'Boss Battle', '♭'),
    ('ending', 'エンディング', 'Ending', '♩'),
    ('game-over', '全滅', 'Defeat', '◇'),
    ('medley', 'メドレー', 'Medley', '♫'),
    ('medley', '作業用BGM', 'Work & Study BGM', '♨'),
]


def category_cards(items: list[tuple[str, str, str, str]], lang: str) -> list[str]:
    cards = []
    for index, (slug, ja_label, en_label, icon) in enumerate(items):
        href = f'/category/{slug}/' if lang == 'ja' else f'/en/category/{slug}/'
        title = ja_label if lang == 'ja' else en_label
        body = 'カテゴリ別ページ' if lang == 'ja' else 'Category page'
        cards.append(book_spine_card(href, title, body, index, icon=icon, variant='category'))
    return cards


def patch_home(path_str: str, lang: str, series_playlists: dict[str, dict]) -> None:
    path = ROOT / path_str
    text = path.read_text(encoding='utf-8')
    text = text.replace('https://chamberd-piano.github.io', BASE)
    text = text.replace('https://c-chan-dq-piano.chamberdeng.workers.dev', BASE)
    text = re.sub(r'\s*<meta\s+name="keywords"[^>]*>\n?', '\n', text, flags=re.I)
    text = text.replace('href="./series-index.html"', 'href="/series-index/"')
    text = text.replace('href="./category-index.html"', 'href="/category-index/"')
    text = text.replace('href="/en/series-index.html"', 'href="/en/series-index/"')
    text = text.replace('href="/en/category-index.html"', 'href="/en/category-index/"')
    text = text.replace('href="/en.html"', 'href="/en/"')
    text = text.replace(
        '<section class="section performer-profile" aria-labelledby="performer-profile-title">',
        '<section class="section performer-profile" id="performer-profile" aria-labelledby="performer-profile-title">'
    )
    if 'performer-profile-name' not in text and lang == 'ja':
        text = text.replace(
            '<h2 id="performer-profile-title">演奏者プロフィール</h2>',
            '<h2 id="performer-profile-title">演奏者プロフィール</h2>\n          <p class="performer-profile-name">しーちゃん</p>'
        )
    elif 'performer-profile-name' not in text:
        text = text.replace(
            '<h2 id="performer-profile-title">Performer Profile</h2>',
            '<h2 id="performer-profile-title">Performer Profile</h2>\n          <p class="performer-profile-name">C-chan</p>'
        )
    series_cards = []
    for index, (key, meta) in enumerate(SERIES_MAP.items()):
        href = f'/{meta["slug"]}/' if lang == 'ja' else f'/en/{meta["slug"]}/'
        title = 'DQ'
        body = meta['ja'] if lang == 'ja' else meta['en']
        series_cards.append(book_spine_card(href, title, body, index, code=key, variant='series'))

    category_library_cards = category_cards(CATEGORY_LIBRARY, lang)
    if lang == 'ja':
        s_title = 'シリーズ別ライブラリー'
        c_title = 'カテゴリ別ライブラリー'
        score_title = '楽譜別ライブラリー'
    else:
        s_title = 'Series Library'
        c_title = 'Category Library'
        score_title = 'Score Library'
    hub = (
        '<section class="section seo-hub-links bookcase-library" id="seo-links">'
        f'<div class="seo-hub-block bookcase-block"><div class="section-heading compact-heading shelf-heading"><p class="section-kicker">Series</p><h3>{esc(s_title)}</h3></div>{book_shelf(series_cards, s_title, "series")}</div>'
        f'<div class="seo-hub-block bookcase-block"><div class="section-heading compact-heading shelf-heading"><p class="section-kicker">Categories</p><h3>{esc(c_title)}</h3></div>{book_shelf(category_library_cards, c_title, "category-en" if lang == "en" else "category")}</div>'
        f'<div class="seo-hub-block bookcase-block"><div class="section-heading compact-heading shelf-heading"><p class="section-kicker">Scores</p><h3>{esc(score_title)}</h3></div>{book_shelf(score_cards(lang), score_title, "score-en" if lang == "en" else "score")}</div>'
        '</section>'
    )
    if 'seo-hub-links' in text:
        text = re.sub(r'<section class="section seo-hub-links[^"]*" id="seo-links">.*?</section>', hub, text, count=1, flags=re.S)
    else:
        text = text.replace('<main class="page">', '<main class="page">\n    ' + hub, 1)
    path.write_text(text, encoding='utf-8')


def series_feature_playlist(key: str, series_playlists: dict[str, dict]) -> list[dict]:
    playlist = series_playlists.get(key)
    return [playlist] if playlist else []


def related_category_cards(lang: str) -> str:
    cards = []
    for slug, info in CATS.items():
        href = f'/category/{slug}/' if lang == 'ja' else f'/en/category/{slug}/'
        body = '関連カテゴリ' if lang == 'ja' else 'Related category'
        cards.append(entry_card(href, info['ja'] if lang == 'ja' else info['en'], body))
    return entry_grid(cards)


def special_collection_rows(key: str, rows_by_id: dict[str, dict], en_titles: dict) -> list[dict]:
    rows = []
    for spec in SPECIAL_COLLECTIONS.get(key, []):
        source = rows_by_id.get(spec['sourceId'])
        if not source:
            continue
        row = dict(source)
        if spec.get('songTitle'):
            row['songTitle'] = spec['songTitle']
            row['songTitleEn'] = en_titles['by_title'].get(spec['songTitle']) or source['songTitleEn']
        rows.append(row)
    return rows


def score_collection_rows(score: dict, rows_by_id: dict[str, dict]) -> list[dict]:
    rows = []
    for source_id in score['sourceIds']:
        source = rows_by_id.get(source_id)
        if source:
            rows.append(dict(source))
    return rows


def score_cover_card(score: dict, lang: str) -> str:
    label = '楽譜写真' if lang == 'ja' else 'Score Cover'
    title = score['ja'] if lang == 'ja' else score['en']
    return (
        '<aside class="score-cover-card">'
        f'<p class="hero-playlist-kicker">{esc(label)}</p>'
        f'<a class="score-cover-link" href="{esc(score["amazonUrl"])}" target="_blank" rel="noreferrer">'
        f'<img class="score-cover-image" src="{esc(score["cover"])}" alt="{esc(title)}" loading="lazy">'
        '</a>'
        '</aside>'
    )


SONG_STYLES = (
    '<style>'
    '.yt-facade{position:relative;aspect-ratio:16/9;border-radius:var(--radius-md);overflow:hidden;'
    'background:#000;border:1px solid var(--line);box-shadow:var(--shadow)}'
    '.yt-facade-btn{all:unset;cursor:pointer;display:block;width:100%;height:100%}'
    '.yt-facade-btn:focus-visible{outline:2px solid var(--brand-deep);outline-offset:2px}'
    '.yt-facade img{width:100%;height:100%;object-fit:cover;display:block}'
    '.yt-facade iframe{position:absolute;inset:0;width:100%;height:100%;border:0}'
    '.yt-facade-play{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);'
    'width:74px;height:50px;border-radius:14px;background:rgba(3,3,2,.74);'
    'border:1px solid var(--line);display:grid;place-items:center;transition:background .2s ease}'
    '.yt-facade-btn:hover .yt-facade-play{background:rgba(20,50,77,.9)}'
    '.yt-facade-play::after{content:"";display:block;border-style:solid;'
    'border-width:11px 0 11px 18px;border-color:transparent transparent transparent var(--brand-deep)}'
    '</style>'
)

SONG_FACADE_SCRIPT = (
    '<script>'
    'document.querySelectorAll(".yt-facade-btn").forEach((btn)=>{'
    'btn.addEventListener("click",()=>{'
    'const wrap=btn.closest(".yt-facade");'
    'const id=wrap.dataset.videoId;'
    'const iframe=document.createElement("iframe");'
    'const start=parseInt(wrap.dataset.start||"0",10);'
    'iframe.src="https://www.youtube-nocookie.com/embed/"+id+"?autoplay=1"+(start>0?"&start="+start:"");'
    'iframe.title=wrap.dataset.videoTitle||"YouTube video";'
    'iframe.allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";'
    'iframe.allowFullscreen=true;'
    'wrap.replaceChildren(iframe);'
    '},{once:true});'
    '});'
    '</script>'
)


def song_facade(vid: str, video_title: str, thumb: str, play_label: str, image_alt: str, start: int = 0) -> str:
    start_attr = f' data-start="{start}"' if start > 0 else ''
    return (
        f'<div class="yt-facade" data-video-id="{esc(vid)}" data-video-title="{esc(video_title)}"{start_attr}>'
        f'<button class="yt-facade-btn" type="button" aria-label="{esc(play_label)}">'
        f'<img src="{thumb}" alt="{esc(image_alt)}" width="480" height="360" loading="eager" fetchpriority="high">'
        '<span class="yt-facade-play" aria-hidden="true"></span>'
        '</button></div>'
    )


def song_difficulty_text(row: dict, lang: str) -> str:
    stars = row.get('difficultyStars')
    if lang == 'ja':
        label = row.get('difficultyLabel') or '未設定'
    else:
        label = row.get('difficultyEn') or 'Not set'
    if not stars:
        return label
    return f'{label} ' + '★' * stars + '☆' * (5 - stars)


def song_neighbor_card(neighbor: dict | None, label: str, lang: str) -> str:
    if not neighbor:
        return ''
    title = neighbor['songTitle'] if lang == 'ja' else neighbor['songTitleEn']
    category = neighbor['category'] if lang == 'ja' else neighbor['categoryEn']
    page_path = SONG_PAGE_PATHS.get(neighbor['id'])
    if page_path:
        href = page_path if lang == 'ja' else '/en' + page_path
        return entry_card(href, f'{label}: {title}', f'{neighbor["id"]} / {category}')
    if neighbor.get('videoUrl'):
        watch = 'YouTubeで見る' if lang == 'ja' else 'Watch on YouTube'
        return (
            f'<a class="entry-card" href="{neighbor["videoUrl"]}" target="_blank" rel="noreferrer">'
            f'<span class="entry-card-title">{label}: {esc(title)}</span>'
            f'<span class="entry-card-body">{esc(neighbor["id"])} / {esc(category)} / {watch}</span></a>'
        )
    return ''


# =========================================================================
# 曲別ページ(リッチデザイン)。データ(song-reference-data.js + song-page-content.js)
# を流し込むだけで全曲に反映される。HTML直書きは禁止。
# 曲別ページはrich版を標準出力する。旧write_song_pageは保守用に残す。
# =========================================================================
SERIES_RELEASE = {'I': 1986, 'II': 1987, 'III': 1988, 'IV': 1990, 'V': 1992,
                  'VI': 1995, 'VII': 2000, 'VIII': 2004, 'IX': 2009, 'X': 2012, 'XI': 2017}
SONG_COMPOSER = 'すぎやまこういち'
SONG_RICH_IDS = set()  # 互換用。曲別ページは全件rich版で生成する。

SONG_PROFILE = {
    'name': 'しーちゃんピアノ',
    'avatar': '/assets/channel-logo.jpg',
    'body': '元クラシックピアニストとしての技術を活かし、ドラゴンクエスト1〜11の楽曲を丁寧に演奏しています。'
            'フィールド曲・戦闘曲・エンディング・メドレーと幅広い曲調をカバーし、作業用BGMから本格的な視聴まで対応できます。',
    'link': 'https://www.youtube.com/@chamberd_piano',
    'link_label': 'YouTubeチャンネルを見る',
}


def stars_html(stars, lang: str = 'ja') -> str:
    """difficulty の数字から ★★★☆☆ を描画。0/未設定は未設定表示。"""
    n = stars if isinstance(stars, int) and 0 <= stars <= 5 else 0
    if not n:
        label = '未設定' if lang == 'ja' else 'Not set'
        return f'<span class="sr-stars is-empty">{label}</span>'
    return '<span class="sr-stars">' + '★' * n + f'<span class="is-empty">{"☆" * (5 - n)}</span></span>'


def score_arranger(meta: dict, lang: str = 'ja') -> str:
    """ピアノ編曲者。現行の使用楽譜は一律で今村康として表示する。"""
    return '今村 康' if lang == 'ja' else 'Yasushi Imamura'


def sr_video_card(row: dict, lang: str = 'ja') -> str:
    """関連/前後の曲カード。曲ページが有れば内部リンク、無ければYouTube直リンク。"""
    series = SERIES_MAP[row['seriesKey']]
    vid = youtube_video_id(row.get('videoUrl', ''))
    thumb = f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg' if vid else ''
    page = SONG_PAGE_PATHS.get(row['id'])
    href = (page if lang == 'ja' else '/en' + page) if page else (row.get('videoUrl') or '#')
    ext = '' if page else ' target="_blank" rel="noreferrer"'
    title = row['songTitle'] if lang == 'ja' else row['songTitleEn']
    category = row['category'] if lang == 'ja' else row['categoryEn']
    thumb_html = f'<img class="sr-card-thumb" src="{thumb}" alt="" loading="lazy" width="480" height="270">' if thumb else ''
    return (
        f'<a class="sr-card" href="{href}"{ext}>{thumb_html}'
        '<span class="sr-card-body">'
        f'<span class="sr-card-eyebrow">{esc(series["code"])}</span>'
        f'<span class="sr-card-title">{esc(title)}</span>'
        f'<span class="sr-card-sub">{esc(category)}</span>'
        '</span></a>'
    )


def sr_section(kicker: str, title: str, inner: str, foot: str = '') -> str:
    foot_html = f'<div class="sr-section-foot">{foot}</div>' if foot else ''
    return (
        '<section class="sr-section"><div class="sr-section-head">'
        f'<p class="sr-kicker">{esc(kicker)}</p><h2>{esc(title)}</h2></div>'
        f'{inner}{foot_html}</section>'
    )


def write_song_page_rich(row: dict, prev_row: dict | None, next_row: dict | None,
                         meta: dict, rows_by_id: dict, lang: str = 'ja') -> None:
    series = SERIES_MAP[row['seriesKey']]
    ja_page = SONG_PAGE_PATHS[row['id']]
    en_page = '/en' + ja_page
    page = ja_page if lang == 'ja' else en_page
    alt = en_page if lang == 'ja' else ja_page
    canon = BASE + page
    vid = youtube_video_id(row['videoUrl'])
    start = youtube_start_seconds(row['videoUrl'])
    thumb = f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'

    if lang == 'ja':
        song_title = row['songTitle']
        song_subtitle = row.get('songTitleEn', '')
        video_title = f'{song_title}（{series["ja"]}）ピアノ演奏'
        title = f'{song_title} ピアノ | {series["ja"]} | {JA_LIBRARY_NAME}'
        desc = (f'{series["ja"]}の「{song_title}」のピアノ演奏ページです。'
                f'演奏動画と曲の情報、参考楽譜、同シリーズや同カテゴリの曲への入口をまとめています。')
        crumbs = [('ホーム', '/'), (series['ja'], f'/{series["slug"]}/'), (song_title, page)]
        tags = (f'<li class="sr-tag">{esc(series["ja"])}</li>'
                f'<li class="sr-tag is-cat">{esc(row["category"])}曲</li>')
        labels = {
            'composer': '作曲', 'arranger': 'ピアノ編曲', 'category': 'カテゴリ', 'difficulty': '難易度',
            'duration': '演奏時間', 'series': '収録作品', 'info': '曲の基本情報', 'score': '参考楽譜', 'amazon': 'Amazonで見る',
            'rakuten': '楽天ブックスで見る', 'same': '同シリーズの前後の曲', 'medleys': 'この曲を含むメドレー・関連動画',
            'takes': '別テイク・バージョン', 'related': f'関連する楽曲（{row["category"]}）',
            'related_foot': f'{row["category"]}曲一覧を見る →', 'performer_head': '演奏者',
            'performed_by': '演奏：しーちゃん', 'profile_link': '演奏者プロフィールを見る →',
            'profile_href': '/#performer-profile', 'footer': '© しーちゃんピアノ',
        }
        category_text = row['category']
        series_text = f'{series["ja"]}（{SERIES_RELEASE.get(row["seriesKey"], "")}年）'
        play_label = f'{video_title}を再生'
    else:
        song_title = row['songTitleEn']
        song_subtitle = row['songTitle']
        video_title = f'{song_title} ({series["en"]}) Piano Performance'
        title = f'{song_title} Piano | {series["en"]} | {EN_LIBRARY_NAME}'
        desc = (f'A piano performance of "{song_title}" from {series["en"]}, '
                f'with score references and links to related pieces from the same game and category.')
        crumbs = [('Home', '/en/'), (series['en'], f'/en/{series["slug"]}/'), (song_title, page)]
        tags = (f'<li class="sr-tag">{esc(series["en"])}</li>'
                f'<li class="sr-tag is-cat">{esc(row["categoryEn"])}</li>')
        labels = {
            'composer': 'Composer', 'arranger': 'Piano arrangement', 'category': 'Category', 'difficulty': 'Difficulty',
            'duration': 'Performance duration', 'series': 'Series', 'info': 'Song Information', 'score': 'Reference Score', 'amazon': 'View on Amazon',
            'rakuten': 'View on Rakuten Books', 'same': 'Previous / Next in Series', 'medleys': 'Medleys and Related Videos',
            'takes': 'Other Takes', 'related': f'Related Pieces ({row["categoryEn"]})',
            'related_foot': f'Browse {row["categoryEn"]} pieces →', 'performer_head': 'Performer',
            'performed_by': 'Performed by C-chan', 'profile_link': 'View performer profile →',
            'profile_href': '/en/#performer-profile', 'footer': '© C-chan Piano',
        }
        category_text = row['categoryEn']
        series_text = f'{series["en"]} ({SERIES_RELEASE.get(row["seriesKey"], "")})'
        play_label = f'Play {video_title}'

    video_json = {
        '@type': 'VideoObject', 'name': video_title, 'description': desc,
        'thumbnailUrl': [thumb], 'contentUrl': row['videoUrl'],
        'embedUrl': f'https://www.youtube.com/embed/{vid}' + (f'?start={start}' if start > 0 else ''),
    }
    if meta.get('uploadDate'):
        video_json['uploadDate'] = meta['uploadDate']
    graph = [website_json(lang), breadcrumb_json(crumbs), video_json]

    head = make_head(lang, title, desc, canon, BASE + ja_page, BASE + en_page, graph)
    head = head.replace('<meta property="og:type" content="website">',
                        '<meta property="og:type" content="video.other">')
    og_image = (f'<meta property="og:image" content="{thumb}">'
                '<meta property="og:image:width" content="480"><meta property="og:image:height" content="360">'
                f'<meta property="og:image:alt" content="{esc(video_title)} thumbnail">'
                f'<meta name="twitter:image" content="{thumb}">')
    head = head.replace('<meta name="twitter:card"', og_image + '<meta name="twitter:card"')
    head = head.replace('</head>',
        '<link rel="stylesheet" href="/assets/lite-yt-embed.css">'
        '<link rel="stylesheet" href="/assets/song-page.css">'
        '<script src="/assets/lite-yt-embed.js" defer></script></head>')

    params = f'start={start}' if start > 0 else ''
    embed = (f'<lite-youtube videoid="{vid}" playlabel="{esc(play_label)}"'
             + (f' params="{params}"' if params else '') + '></lite-youtube>')

    rows_info = ''.join([
        f'<tr><th scope="row">{esc(labels["composer"])}</th><td>{esc(SONG_COMPOSER if lang == "ja" else "Koichi Sugiyama")}</td></tr>',
        f'<tr><th scope="row">{esc(labels["arranger"])}</th><td>{esc(score_arranger(meta, lang))}</td></tr>',
        f'<tr><th scope="row">{esc(labels["duration"])}</th><td>{esc(meta.get("performanceDuration", ""))}</td></tr>' if meta.get('performanceDuration') else '',
        f'<tr><th scope="row">{esc(labels["category"])}</th><td>{esc(category_text)}</td></tr>',
        f'<tr><th scope="row">{esc(labels["difficulty"])}</th><td>{stars_html(row.get("difficultyStars"), lang)}</td></tr>',
        f'<tr><th scope="row">{esc(labels["series"])}</th><td>{esc(series_text)}</td></tr>',
    ])
    info = (f'<details class="sr-info" open><summary>{esc(labels["info"])}</summary>'
            f'<p class="sr-info-title">{esc(labels["info"])}</p>'
            f'<table class="sr-info-table"><tbody>{rows_info}</tbody></table></details>')

    score_html = ''
    sb = meta.get('scorebook')
    if sb:
        buttons = ''
        if sb.get('amazon'):
            buttons += f'<a class="sr-buy is-amazon" href="{sb["amazon"]}" target="_blank" rel="noreferrer sponsored">{esc(labels["amazon"])}</a>'
        if sb.get('rakuten'):
            buttons += f'<a class="sr-buy is-rakuten" href="{sb["rakuten"]}" target="_blank" rel="noreferrer sponsored">{esc(labels["rakuten"])}</a>'
        cover = sb.get('cover')
        cover_html = f'<img class="sr-score-cover" src="{cover}" alt="{esc(sb.get("name", ""))}" loading="lazy">' if cover else ''
        nocover = '' if cover else ' sr-score-nocover'
        meta_line = f'<p class="sr-score-meta">{esc(sb.get("publisher", ""))}</p>' if sb.get('publisher') else ''
        score_html = (f'<aside class="sr-score{nocover}" aria-label="{esc(labels["score"])}">{cover_html}'
                      f'<div><p class="sr-score-label">{esc(labels["score"])}</p>'
                      f'<p class="sr-score-name">{esc(sb.get("name", ""))}</p>{meta_line}'
                      f'<div class="sr-score-buttons">{buttons}</div></div></aside>')

    info_stack = f'<div class="sr-info-stack">{info}{score_html}</div>'
    body_sections = []

    neigh = [sr_video_card(r, lang) for r in (prev_row, next_row) if r and r.get('videoUrl')]
    if neigh:
        body_sections.append(sr_section('Same Series', labels['same'], f'<div class="sr-cards">{"".join(neigh)}</div>'))

    medleys = meta.get('medleys') or []
    if medleys:
        cards = ''.join(
            f'<a class="sr-card" href="https://www.youtube.com/watch?v={esc(m["youtube"])}" target="_blank" rel="noreferrer">'
            f'<img class="sr-card-thumb" src="https://i.ytimg.com/vi/{esc(m["youtube"])}/hqdefault.jpg" alt="" loading="lazy" width="480" height="270">'
            f'<span class="sr-card-body"><span class="sr-card-title">{esc(m["title"] or "")}</span>'
            f'<span class="sr-card-sub">{esc(m.get("time", ""))}</span></span></a>'
            for m in medleys)
        body_sections.append(sr_section('Medleys', labels['medleys'], f'<div class="sr-cards">{cards}</div>'))

    takes = meta.get('takes') or []
    if takes:
        items = ''.join(
            f'<a class="sr-take" href="https://www.youtube.com/watch?v={esc(t["youtube"])}" target="_blank" rel="noreferrer">'
            f'<span class="sr-take-time">{esc(t.get("time", ""))}</span><span>{esc(t["label"])}</span></a>'
            for t in takes)
        body_sections.append(sr_section('Other Takes', labels['takes'], f'<div class="sr-takes">{items}</div>'))

    same_cat = [r for r in rows_by_id.values()
                if r['category'] == row['category'] and r['id'] != row['id'] and r.get('videoUrl')]
    same_cat.sort(key=lambda r: (r['seriesKey'] != row['seriesKey'], SERIES_ORDER.index(r['seriesKey']), r['sortNumber']))
    rel = [sr_video_card(r, lang) for r in same_cat[:6]]
    if rel:
        cat_slug = next((s for s, info2 in CATS.items() if row['category'] in info2['match']), '')
        href = f'/category/{cat_slug}/' if lang == 'ja' else f'/en/category/{cat_slug}/'
        foot = f'<a class="sr-textlink" href="{href}">{esc(labels["related_foot"])}</a>' if cat_slug else ''
        body_sections.append(sr_section('Related', labels['related'], f'<div class="sr-cards">{"".join(rel)}</div>', foot))

    p = SONG_PROFILE
    body_sections.append(sr_section('Performer', labels['performer_head'],
        f'<div class="sr-profile sr-profile-compact"><img class="sr-profile-avatar" src="{p["avatar"]}" alt="{esc(p["name"])}" loading="lazy">'
        f'<div><p class="sr-profile-name">{esc(labels["performed_by"])}</p>'
        f'<a class="sr-textlink" href="{labels["profile_href"]}">{esc(labels["profile_link"])}</a></div></div>'))

    main = (
        '<div class="song-rich"><div class="sr-wrap">'
        f'{breadcrumbs(crumbs)}'
        f'<h1 class="sr-title">{esc(song_title)}</h1>'
        f'<p class="sr-subtitle">{esc(song_subtitle)}</p>'
        f'<ul class="sr-tags">{tags}</ul>'
        '<div class="sr-lead-grid">'
        f'<div>{embed}<p class="sr-embed-cap">{esc(video_title)}</p></div>'
        f'{info_stack}</div>'
        f'{"".join(body_sections)}'
        '</div></div>'
    )

    html = (head +
        '<body><div class="site-bg" aria-hidden="true"></div>'
        f'<header class="hero hero-simple">{topbar(lang, page, alt)}</header>'
        f'<main class="page">{main}</main>'
        f'<footer class="seo-footer"><p>{esc(labels["footer"])}</p></footer></body></html>')
    write(Path(page[1:]) / 'index.html', html)

    SONG_VIDEO_ENTRIES[canon] = {
        'thumbnail': thumb, 'title': video_title, 'description': desc,
        'player_loc': f'https://www.youtube.com/embed/{vid}' + (f'?start={start}' if start > 0 else ''),
        'publication_date': meta.get('uploadDate', ''),
    }


def write_song_page(row: dict, prev_row: dict | None, next_row: dict | None, meta: dict, lang: str) -> None:
    series = SERIES_MAP[row['seriesKey']]
    ja_page = SONG_PAGE_PATHS[row['id']]
    en_page = '/en' + ja_page
    page = ja_page if lang == 'ja' else en_page
    canon = BASE + page
    vid = youtube_video_id(row['videoUrl'])
    start = youtube_start_seconds(row['videoUrl'])
    thumb = f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'

    if lang == 'ja':
        song_title = row['songTitle']
        video_title = f'{song_title}（{series["ja"]}）ピアノ演奏'
        title = f'{song_title} ピアノ | {series["ja"]} | {JA_LIBRARY_NAME}'
        desc = (
            f'{series["ja"]}の「{song_title}」のピアノ演奏ページです。'
            f'演奏動画と曲の情報、同シリーズや同カテゴリの曲への入口をまとめています。'
        )
        lead = meta.get('lead') or f'{series["ja"]}の{row["category"]}曲「{song_title}」のピアノ演奏です。'
        crumbs = [('ホーム', '/'), (series['code'], f'/{series["slug"]}/'), (song_title, page)]
        play_label = f'{video_title}を再生'
        image_alt = f'{video_title}のサムネイル'
        about_text = meta.get('description', '')
    else:
        song_title = row['songTitleEn']
        video_title = f'{song_title} ({series["en"]}) Piano Performance'
        title = f'{song_title} Piano | {series["en"]} | {EN_LIBRARY_NAME}'
        desc = (
            f'A piano performance of "{song_title}" from {series["en"]}, '
            f'with links to related pieces from the same game and category.'
        )
        lead = meta.get('leadEn') or f'A piano performance of "{song_title}" from {series["en"]}.'
        crumbs = [('Home', '/en/'), (series['code'], f'/en/{series["slug"]}/'), (song_title, page)]
        play_label = f'Play {video_title}'
        image_alt = f'Thumbnail of {video_title}'
        about_text = meta.get('descriptionEn', '')

    video_json = {
        '@type': 'VideoObject',
        'name': video_title,
        'description': desc,
        'thumbnailUrl': [thumb],
        'contentUrl': row['videoUrl'],
        'embedUrl': f'https://www.youtube.com/embed/{vid}' + (f'?start={start}' if start > 0 else ''),
    }
    if meta.get('uploadDate'):
        video_json['uploadDate'] = meta['uploadDate']
    graph = [website_json(lang), breadcrumb_json(crumbs), video_json]

    head = make_head(lang, title, desc, canon, BASE + ja_page, BASE + en_page, graph)
    head = head.replace(
        '<meta property="og:type" content="website">',
        '<meta property="og:type" content="video.other">',
    )
    og_image = (
        f'<meta property="og:image" content="{thumb}">'
        '<meta property="og:image:width" content="480">'
        '<meta property="og:image:height" content="360">'
        f'<meta property="og:image:alt" content="{esc(image_alt)}">'
        f'<meta name="twitter:image" content="{thumb}">'
    )
    head = head.replace('<meta name="twitter:card"', og_image + '<meta name="twitter:card"')
    head = head.replace('</head>', SONG_STYLES + '</head>')

    if lang == 'ja':
        metrics = ''.join([
            metric('カテゴリ', row['category']),
            metric('難易度', song_difficulty_text(row, lang)),
            metric('収録作品', series['ja']),
        ])
        actions = ''.join([
            action(row['videoUrl'], 'YouTubeで見る', primary=True, external=True),
            action(f'/{series["slug"]}/', f'{series["code"]}の曲一覧'),
            action('https://www.youtube.com/@chamberd_piano', 'YouTubeチャンネルを見る', external=True),
        ])
    else:
        metrics = ''.join([
            metric('Category', row['categoryEn']),
            metric('Difficulty', song_difficulty_text(row, lang)),
            metric('Series', series['en']),
        ])
        actions = ''.join([
            action(row['videoUrl'], 'Watch on YouTube', primary=True, external=True),
            action(f'/en/{series["slug"]}/', f'{series["code"]} song list'),
            action('https://www.youtube.com/@chamberd_piano', 'Visit the YouTube channel', external=True),
        ])

    main = ''
    if about_text:
        main += section('About', 'この曲について' if lang == 'ja' else 'About This Piece', f'<p class="section-copy">{esc(about_text)}</p>')
    if lang == 'ja' and meta.get('timestamps'):
        items = ''.join(
            f'<li><span class="song-link">{esc(ts["time"])}</span> {esc(ts["label"])}</li>'
            for ts in meta['timestamps']
        )
        main += section('Chapters', '演奏の流れ', f'<ul>{items}</ul>')

    related = [card for card in (
        song_neighbor_card(prev_row, '前の曲' if lang == 'ja' else 'Previous', lang),
        song_neighbor_card(next_row, '次の曲' if lang == 'ja' else 'Next', lang),
    ) if card]
    if lang == 'ja':
        related.append(entry_card(f'/{series["slug"]}/', f'{series["ja"]} の曲一覧', '作品別ページへ'))
    else:
        related.append(entry_card(f'/en/{series["slug"]}/', f'{series["en"]} song list', 'Series page'))
    cat_slug = next((slug for slug, info in CATS.items() if row['category'] in info['match']), '')
    if cat_slug:
        if lang == 'ja':
            related.append(entry_card(f'/category/{cat_slug}/', f'{row["category"]}の曲', 'カテゴリ別ページへ'))
        else:
            related.append(entry_card(f'/en/category/{cat_slug}/', f'{row["categoryEn"]} pieces', 'Category page'))
    main += section(
        'Related',
        '関連の曲とページ' if lang == 'ja' else 'Related Songs & Pages',
        entry_grid(related),
        '同じ作品・同じカテゴリの曲をたどれます。' if lang == 'ja' else 'Browse pieces from the same game and category.',
    )

    html = head + shell(
        lang, page, en_page if lang == 'ja' else ja_page,
        breadcrumbs(crumbs),
        song_title, lead, metrics, actions,
        song_facade(vid, video_title, thumb, play_label, image_alt, start),
        main,
    )
    html = html.replace('</body></html>', SONG_FACADE_SCRIPT + '</body></html>')
    write(Path(page[1:]) / 'index.html', html)

    SONG_VIDEO_ENTRIES[canon] = {
        'thumbnail': thumb,
        'title': video_title,
        'description': desc,
        'player_loc': f'https://www.youtube.com/embed/{vid}' + (f'?start={start}' if start > 0 else ''),
        'publication_date': meta.get('uploadDate', ''),
    }


def build() -> None:
    songs = load_js('song-reference-data.js', 'window.songReferenceData = ')
    playlists = load_js('playlist-data.js', 'window.playlistData = ')
    en_titles = load_titles()

    all_rows = []
    by_series = {}
    rows_by_id = {}
    for skey, rows in songs.items():
        cooked = []
        for row in rows:
            item = dict(row)
            item['seriesKey'] = skey
            item['songTitleEn'] = en_titles['by_id'].get(row['id']) or en_titles['by_title'].get(row['songTitle'], row['songTitle'])
            item['categoryEn'] = CAT_EN.get(row['category'], row['category'])
            item['difficultyEn'] = DIFF_EN.get(row.get('difficultyLabel', ''), row.get('difficultyLabel', ''))
            cooked.append(item)
            all_rows.append(item)
            rows_by_id[item['id']] = item
        by_series[skey] = cooked

    song_content = load_js('song-page-content.js', 'window.songPageContent = ')
    scorebook_by_series = {
        'I': {
            'name': 'ピアノ曲集 ドラゴンクエスト I・II・III オフィシャル・スコア・ブック',
            'publisher': 'KMP / すぎやまこういち 監修',
            'amazon': 'https://amzn.to/4pOvadt',
            'rakuten': 'https://a.r10.to/hkH1j5',
        },
        'II': {
            'name': 'ピアノ曲集 ドラゴンクエスト I・II・III オフィシャル・スコア・ブック',
            'publisher': 'KMP / すぎやまこういち 監修',
            'amazon': 'https://amzn.to/4pOvadt',
            'rakuten': 'https://a.r10.to/hkH1j5',
        },
        'III': {
            'name': 'ピアノ曲集 ドラゴンクエスト I・II・III オフィシャル・スコア・ブック',
            'publisher': 'KMP / すぎやまこういち 監修',
            'amazon': 'https://amzn.to/4pOvadt',
            'rakuten': 'https://a.r10.to/hkH1j5',
        },
        'IV': {
            'name': 'ピアノ曲集 ドラゴンクエストIV 導かれし者たち オフィシャルスコアブック',
            'publisher': 'KMP / すぎやまこういち 監修',
            'amazon': 'https://amzn.to/3O84bJ1',
            'rakuten': 'https://a.r10.to/hNSett',
        },
        'V': {
            'name': 'ピアノ曲集 「ドラゴンクエストV」 天空の花嫁 オフィシャル・スコア・ブック',
            'publisher': 'KMP / すぎやまこういち 監修',
            'amazon': 'https://amzn.to/4qrEMLf',
            'rakuten': 'https://a.r10.to/hkDh76',
        },
        'VI': {
            'name': 'ピアノ曲集 「ドラゴンクエストVI」幻の大地 オフィシャルスコアブック',
            'publisher': 'KMP',
            'amazon': 'https://amzn.to/3PUNSRB',
        },
        'VII': {
            'name': 'ピアノ曲集 「ドラゴンクエストVII」エデンの戦士たち オフィシャル・スコア・ブック',
            'publisher': 'KMP / すぎやまこういち 監修',
            'amazon': 'https://amzn.to/3WBggKa',
            'rakuten': 'https://a.r10.to/h5OMp9',
        },
        'VIII': {
            'name': 'ピアノ曲集 ドラゴンクエストVIII 空と海と大地と呪われし姫君 オフィシャルスコアブック',
            'publisher': 'KMP',
            'amazon': 'https://amzn.to/4eRm7lv',
        },
        'IX': {
            'name': 'ピアノ曲集 「ドラゴンクエストIX」 オフィシャル・スコア・ブック',
            'publisher': 'KMP / すぎやまこういち 監修',
            'amazon': 'https://amzn.to/48SuKwF',
            'rakuten': 'https://a.r10.to/h51OhG',
        },
        'X': {
            'name': 'ピアノ曲集 ドラゴンクエストX 目覚めし五つの種族 オフィシャルスコアブック',
            'publisher': 'すぎやまこういち 監修',
            'amazon': 'https://amzn.to/45bWh93',
        },
        'XI': {
            'name': 'ピアノ曲集 「ドラゴンクエストXI」 過ぎ去りし時を求めて オフィシャル・スコア・ブック',
            'publisher': 'すぎやまこういち 監修',
            'amazon': 'https://amzn.to/3IM5yNP',
        },
    }
    for song_id, meta in song_content.items():
        series_key = song_id.split('-')[0]
        if series_key in scorebook_by_series:
            meta.setdefault('scorebook', dict(scorebook_by_series[series_key]))
    SONG_PAGE_PATHS.clear()
    for song_id, meta in song_content.items():
        skey = song_id.split('-')[0]
        if meta.get('slug') and rows_by_id.get(song_id, {}).get('videoUrl'):
            SONG_PAGE_PATHS[song_id] = f'/{SERIES_MAP[skey]["slug"]}/{meta["slug"]}/'

    series_playlists = {}
    medley_playlists = []
    for playlist in playlists:
        playlist = dict(playlist)
        playlist['thumbnail'] = normalize_thumb(playlist.get('thumbnail'))
        key = infer_series(playlist['title'])
        if key and key not in series_playlists and not is_medley(playlist['title']):
            series_playlists[key] = playlist
        if is_medley(playlist['title']):
            medley_playlists.append(playlist)
    medley_tracks = []
    seen_medley_urls = set()
    for playlist in medley_playlists:
        for track in playlist.get('tracks', []):
            url = track.get('url')
            if not url or url in seen_medley_urls:
                continue
            seen_medley_urls.add(url)
            medley_tracks.append({
                'title': track.get('title') or track.get('rawTitle') or playlist['title'],
                'url': url,
                'playlistTitle': playlist['title'],
                'thumbnail': track.get('thumbnail') or youtube_video_thumb(url) or playlist.get('thumbnail', ''),
            })

    urls = [BASE + '/', BASE + '/en/']

    for key, slug, ja_name, en_name, code in SERIES:
        rows = sorted(by_series[key], key=lambda row: row['sortNumber'])
        special_rows = special_collection_rows(key, rows_by_id, en_titles)
        linked_count = sum(1 for row in rows if row.get('videoUrl'))
        playlist_items = series_feature_playlist(key, series_playlists)

        for lang in ('ja', 'en'):
            page = f'/{slug}/' if lang == 'ja' else f'/en/{slug}/'
            alt = f'/en/{slug}/' if lang == 'ja' else f'/{slug}/'
            title = f'{code} ピアノ | {ja_name} ピアノ演奏ライブラリー | {JA_LIBRARY_NAME}' if lang == 'ja' else f'{code} Piano | {en_name} Piano Library | {EN_LIBRARY_NAME}'
            desc = (
                f'{ja_name}の楽曲をピアノで演奏した動画を、曲番号順の一覧でまとめています。曲名をクリックすると、各曲の演奏動画と関連曲をたどれます。'
                if lang == 'ja' else
                f'Piano performances of music from {en_name}, listed in song order. Click a title to watch the performance and explore related pieces.'
            )
            crumbs = [('ホーム', '/') if lang == 'ja' else ('Home', '/en/'), (code, page)]
            graph = [
                website_json(lang),
                breadcrumb_json(crumbs),
                {'@type': 'CollectionPage', 'name': title, 'description': desc, 'url': BASE + page, 'inLanguage': 'ja-JP' if lang == 'ja' else 'en-US'},
                music_playlist_json(lang, title, desc, page, rows),
                {'@type': 'ItemList', 'itemListElement': [
                    {'@type': 'ListItem', 'position': i + 1, 'name': row['songTitle'] if lang == 'ja' else row['songTitleEn'], **({'url': row['videoUrl']} if row.get('videoUrl') else {})}
                    for i, row in enumerate(rows)
                ]},
            ]
            metrics = ''.join([
                metric('収録曲数' if lang == 'ja' else 'Songs', str(len(rows))),
                metric('動画リンク' if lang == 'ja' else 'Linked videos', str(linked_count)),
                metric('作品別プレイリスト' if lang == 'ja' else 'Playlists', '1' if playlist_items else '0'),
            ])
            actions = []
            if playlist_items:
                actions.append(action(playlist_items[0]['url'], 'YouTubeの作品別プレイリスト' if lang == 'ja' else 'Open playlist', primary=True, external=True))
            actions.append(action('/category-index/' if lang == 'ja' else '/en/category-index/', 'カテゴリ別に探す' if lang == 'ja' else 'Browse categories'))
            actions.append(action('https://www.youtube.com/@chamberd_piano', 'YouTubeチャンネルを見る' if lang == 'ja' else 'Visit YouTube', external=True))
            feature = playlist_cards(playlist_items, lang, hero=True) if playlist_items else ''
            main = ''
            main += section('Songs', '収録曲一覧' if lang == 'ja' else 'Song List', song_table(rows, lang, song_content), '曲番号順でたどれる一覧です。' if lang == 'ja' else 'Song list ordered by catalog number.')
            if special_rows:
                main += section(
                    'Special',
                    '特別収録' if lang == 'ja' else 'Special Selections',
                    song_table(special_rows, lang, song_content),
                    '過去シリーズ楽譜からの特別収録曲です。曲番号・リンクは出典元シリーズに合わせています。' if lang == 'ja' else 'Special selections from earlier series. Numbers and links follow the original source series.',
                )
            main += section('Related', '関連カテゴリ' if lang == 'ja' else 'Related Categories', related_category_cards(lang), 'フィールド曲・戦闘曲・メドレーなど、曲の種類からも探せます。' if lang == 'ja' else 'Browse field themes, battle music, medleys, and more by category.')
            html = make_head(lang, title, desc, BASE + page, BASE + f'/{slug}/', BASE + f'/en/{slug}/', graph)
            html += shell(lang, page, alt, breadcrumbs(crumbs), f'{ja_name} ピアノ演奏ライブラリー' if lang == 'ja' else f'{en_name} Piano Library', desc, metrics, ''.join(actions), feature, main)
            write(Path(page[1:]) / 'index.html', html)
        urls.extend([BASE + f'/{slug}/', BASE + f'/en/{slug}/'])

        for i, row in enumerate(rows):
            if row['id'] not in SONG_PAGE_PATHS:
                continue
            prev_row = rows[i - 1] if i > 0 else None
            next_row = rows[i + 1] if i + 1 < len(rows) else None
            for song_lang in ('ja', 'en'):
                write_song_page_rich(row, prev_row, next_row, song_content[row['id']], rows_by_id, song_lang)
            urls.extend([BASE + SONG_PAGE_PATHS[row['id']], BASE + '/en' + SONG_PAGE_PATHS[row['id']]])

    for slug, info in CATS.items():
        rows = [row for row in all_rows if row['category'] in info['match']]
        rows.sort(key=lambda row: (SERIES_ORDER.index(row['seriesKey']), row['sortNumber']))
        if slug == 'medley':
            featured = medley_playlists[:2]
        else:
            featured = []
        series_keys = sorted({row['seriesKey'] for row in rows}, key=lambda key: SERIES_ORDER.index(key))
        linked_count = sum(1 for row in rows if row.get('videoUrl'))

        for lang in ('ja', 'en'):
            page = f'/category/{slug}/' if lang == 'ja' else f'/en/category/{slug}/'
            alt = f'/en/category/{slug}/' if lang == 'ja' else f'/category/{slug}/'
            title = f'{info["ja"]} ピアノ | ドラクエ ピアノ演奏ライブラリー | {JA_LIBRARY_NAME}' if lang == 'ja' else f'{info["en"]} | {EN_LIBRARY_NAME}'
            if slug == 'medley':
                desc = (
                    'ドラゴンクエストのピアノメドレー動画を集めたページです。作業用BGMとしても聴きやすい、長めの演奏をまとめています。'
                    if lang == 'ja' else
                    'Dragon Quest piano medleys, collected for longer listening sessions and background music.'
                )
            else:
                desc = (
                    f'シリーズ各作品の{info["ja"]}の曲を、ひとつの一覧にまとめたページです。曲名をクリックすると、各曲の演奏動画と関連曲をたどれます。'
                    if lang == 'ja' else
                    f'{info["en"]} pieces from across the Dragon Quest series. Click a title to watch the performance and explore related pieces.'
                )
            label = info['ja'] if lang == 'ja' else info['en']
            crumbs = [('ホーム', '/') if lang == 'ja' else ('Home', '/en/'), (label, page)]
            if slug == 'medley':
                item_list = [
                    {'@type': 'ListItem', 'position': i + 1, 'name': track['title'], 'url': track['url']}
                    for i, track in enumerate(medley_tracks)
                ]
            else:
                item_list = [
                    {'@type': 'ListItem', 'position': i + 1, 'name': row['songTitle'] if lang == 'ja' else row['songTitleEn'], **({'url': row['videoUrl']} if row.get('videoUrl') else {})}
                    for i, row in enumerate(rows)
                ]
            graph = [
                website_json(lang),
                breadcrumb_json(crumbs),
                {'@type': 'CollectionPage', 'name': title, 'description': desc, 'url': BASE + page, 'inLanguage': 'ja-JP' if lang == 'ja' else 'en-US'},
                {'@type': 'ItemList', 'itemListElement': item_list},
            ]
            metrics = ''.join([
                metric('対象曲数' if lang == 'ja' else 'Songs', str(len(rows) if slug != 'medley' else len(medley_tracks))),
                metric('関連シリーズ' if lang == 'ja' else 'Series', str(len(series_keys) if slug != 'medley' else len(SERIES_MAP))),
                metric('動画リンク' if lang == 'ja' else 'Linked videos', str(linked_count if slug != 'medley' else len(medley_tracks))),
            ])
            actions = [
                action('/category-index/' if lang == 'ja' else '/en/category-index/', 'カテゴリ一覧へ' if lang == 'ja' else 'Category index', primary=True),
                action('/series-index/' if lang == 'ja' else '/en/series-index/', '作品別ページへ' if lang == 'ja' else 'Browse series'),
                action('https://www.youtube.com/@chamberd_piano', 'YouTubeチャンネルを見る' if lang == 'ja' else 'Visit YouTube', external=True),
            ]
            feature = playlist_cards(featured, lang, hero=True) if featured else ''
            if slug == 'medley':
                table_or_cards = (
                    medley_video_cards(medley_tracks, lang)
                    + section(
                        'Playlists',
                        'メドレープレイリスト' if lang == 'ja' else 'Medley Playlists',
                        playlist_cards(medley_playlists, lang),
                        'YouTube上のプレイリストへ進めます。' if lang == 'ja' else 'Open the full YouTube playlists.',
                    )
                )
                section_title = 'メドレー動画' if lang == 'ja' else 'Medley Videos'
                section_copy = '作業用BGMや場面別に聴けるメドレー動画をまとめています。' if lang == 'ja' else 'Medley videos for background listening and themed browsing.'
            else:
                table_or_cards = song_table(rows, lang, song_content)
                section_title = label
                section_copy = 'シリーズ横断で曲を一覧できるカテゴリページです。' if lang == 'ja' else 'A cross-series category page.'
            related_cards = []
            if slug == 'medley':
                for meta in SERIES_MAP.values():
                    href = f'/{meta["slug"]}/' if lang == 'ja' else f'/en/{meta["slug"]}/'
                    related_cards.append(entry_card(href, meta['code'], '作品別ページへ' if lang == 'ja' else 'Series page'))
            else:
                for key in series_keys[:8]:
                    meta = SERIES_MAP[key]
                    href = f'/{meta["slug"]}/' if lang == 'ja' else f'/en/{meta["slug"]}/'
                    related_cards.append(entry_card(href, meta['code'], '作品別ページへ' if lang == 'ja' else 'Series page'))
            main = section('Category', section_title, table_or_cards, section_copy)
            main += section('Related', '関連作品' if lang == 'ja' else 'Related Series', entry_grid(related_cards), 'このカテゴリの曲を収録している作品のページです。' if lang == 'ja' else 'Series pages featuring pieces from this category.')
            hero_title = f'{info["ja"]}を探す' if lang == 'ja' else f'Browse {info["en"]}'
            html = make_head(lang, title, desc, BASE + page, BASE + f'/category/{slug}/', BASE + f'/en/category/{slug}/', graph)
            html += shell(lang, page, alt, breadcrumbs(crumbs), hero_title, desc, metrics, ''.join(actions), feature, main)
            write(Path(page[1:]) / 'index.html', html)
        urls.extend([BASE + f'/category/{slug}/', BASE + f'/en/category/{slug}/'])

    for score in SCORE_LIBRARY:
        rows = score_collection_rows(score, rows_by_id)
        linked_count = sum(1 for row in rows if row.get('videoUrl'))
        series_count = len({row['seriesKey'] for row in rows})

        for lang in ('ja', 'en'):
            page = f'/score/{score["slug"]}/' if lang == 'ja' else f'/en/score/{score["slug"]}/'
            alt = f'/en/score/{score["slug"]}/' if lang == 'ja' else f'/score/{score["slug"]}/'
            label = score['ja'] if lang == 'ja' else score['en']
            title = (
                f'{label} | 楽譜別ピアノ収載曲 | {JA_LIBRARY_NAME}'
                if lang == 'ja' else
                f'{label} | Score Library | {EN_LIBRARY_NAME}'
            )
            desc = (
                'DQ1〜DQ11から選ばれたピアノ楽譜「ドラゴンクエスト オフィシャル・ベスト・アルバム」の収載曲を、出典元の曲番号とYouTubeリンクで整理しています。'
                if lang == 'ja' else
                'Browse the Dragon Quest Official Best Album score selections from DQ1 to DQ11 with original source numbers and YouTube links.'
            )
            crumbs = [('ホーム', '/') if lang == 'ja' else ('Home', '/en/'), (label, page)]
            item_list = [
                {
                    '@type': 'ListItem',
                    'position': i + 1,
                    'name': row['songTitle'] if lang == 'ja' else row['songTitleEn'],
                    **({'url': row['videoUrl']} if row.get('videoUrl') else {}),
                }
                for i, row in enumerate(rows)
            ]
            graph = [
                website_json(lang),
                breadcrumb_json(crumbs),
                {'@type': 'CollectionPage', 'name': title, 'description': desc, 'url': BASE + page, 'inLanguage': 'ja-JP' if lang == 'ja' else 'en-US'},
                music_playlist_json(lang, title, desc, page, rows),
                {'@type': 'ItemList', 'itemListElement': item_list},
            ]
            metrics = ''.join([
                metric('収載曲数' if lang == 'ja' else 'Songs', str(len(rows))),
                metric('対象シリーズ' if lang == 'ja' else 'Series', str(series_count)),
                metric('動画リンク' if lang == 'ja' else 'Linked videos', str(linked_count)),
            ])
            actions = [
                action(score['amazonUrl'], 'Amazonで楽譜を見る' if lang == 'ja' else 'View score on Amazon', primary=True, external=True),
                action('/series-index/' if lang == 'ja' else '/en/series-index/', '作品別ページへ' if lang == 'ja' else 'Browse series'),
                action('/category-index/' if lang == 'ja' else '/en/category-index/', 'カテゴリ別に探す' if lang == 'ja' else 'Browse categories'),
            ]
            related_cards = [
                entry_card('/series-index/' if lang == 'ja' else '/en/series-index/', '作品別ライブラリー' if lang == 'ja' else 'Series Library', 'DQ1〜DQ11へ' if lang == 'ja' else 'Browse DQ1-DQ11'),
                entry_card('/category-index/' if lang == 'ja' else '/en/category-index/', 'カテゴリ別ライブラリー' if lang == 'ja' else 'Category Library', '曲の種類から探す' if lang == 'ja' else 'Browse by category'),
                entry_card('https://www.youtube.com/@chamberd_piano', 'YouTube', 'チャンネルへ' if lang == 'ja' else 'Open channel'),
            ]
            main = section(
                'Score',
                '収載曲一覧' if lang == 'ja' else 'Score Selections',
                song_table(rows, lang),
                '曲番号・リンク・難易度は、各作品ページの出典元データに合わせています。' if lang == 'ja' else 'Numbers, links, and difficulty values follow the source series entries.',
            )
            main += section(
                'Related',
                '関連ページ' if lang == 'ja' else 'Related Links',
                entry_grid(related_cards),
                '楽譜から作品別・カテゴリ別のページへ移動できます。' if lang == 'ja' else 'Move from the score page into series and category pages.',
            )
            html = make_head(lang, title, desc, BASE + page, BASE + f'/score/{score["slug"]}/', BASE + f'/en/score/{score["slug"]}/', graph)
            html += shell(lang, page, alt, breadcrumbs(crumbs), label, desc, metrics, ''.join(actions), score_cover_card(score, lang), main)
            write(Path(page[1:]) / 'index.html', html)
        urls.extend([BASE + f'/score/{score["slug"]}/', BASE + f'/en/score/{score["slug"]}/'])

    ja_series_cards = [entry_card(f'/{meta["slug"]}/', meta['code'], meta['ja'], thumb=normalize_thumb(series_playlists.get(key, {}).get('thumbnail')) if series_playlists.get(key) else '') for key, meta in SERIES_MAP.items()]
    en_series_cards = [entry_card(f'/en/{meta["slug"]}/', meta['code'], meta['en'], thumb=normalize_thumb(series_playlists.get(key, {}).get('thumbnail')) if series_playlists.get(key) else '') for key, meta in SERIES_MAP.items()]
    ja_cat_cards = [entry_card(f'/category/{slug}/', info['ja'], 'カテゴリ別ページ') for slug, info in CATS.items() if slug != 'medley']
    en_cat_cards = [entry_card(f'/en/category/{slug}/', info['en'], 'Category page') for slug, info in CATS.items() if slug != 'medley']
    ja_bgm_cards = [entry_card('/category/medley/', CATS['medley']['ja'], '作業用BGM向けメドレー')]
    en_bgm_cards = [entry_card('/en/category/medley/', CATS['medley']['en'], 'Medleys for background listening')]

    series_index_ja = make_head('ja', f'作品別ページ一覧 | {JA_LIBRARY_NAME}', 'DQ1〜DQ11の作品別ページ一覧です。', BASE + '/series-index/', BASE + '/series-index/', BASE + '/en/series-index/', [website_json('ja'), breadcrumb_json([('ホーム', '/'), ('作品別ページ一覧', '/series-index/')]), {'@type': 'CollectionPage', 'name': '作品別ページ一覧', 'description': 'DQ1〜DQ11の作品別ページ一覧です。', 'url': BASE + '/series-index/', 'inLanguage': 'ja-JP'}]) + shell('ja', '/series-index/', '/en/series-index/', breadcrumbs([('ホーム', '/'), ('作品別ページ一覧', '/series-index/')]), '作品別ページ一覧', 'DQ1〜DQ11の作品別ページ一覧です。', metric('ページ数', '11') + metric('言語', '日本語 / English') + metric('目的', '作品名検索の入口'), action('/category-index/', 'カテゴリ別も見る', primary=True) + action('https://www.youtube.com/@chamberd_piano', 'YouTubeチャンネルを見る', external=True), '', section('Series', 'DQ1〜DQ11', entry_grid(ja_series_cards), '各作品ページから曲一覧とYouTube導線に進めます。'))
    series_index_en = make_head('en', f'Browse by Series | {EN_LIBRARY_NAME}', 'Series landing pages from DQ1 to DQ11.', BASE + '/en/series-index/', BASE + '/series-index/', BASE + '/en/series-index/', [website_json('en'), breadcrumb_json([('Home', '/en/'), ('Browse by Series', '/en/series-index/')]), {'@type': 'CollectionPage', 'name': 'Browse by Series', 'description': 'Series landing pages from DQ1 to DQ11.', 'url': BASE + '/en/series-index/', 'inLanguage': 'en-US'}]) + shell('en', '/en/series-index/', '/series-index/', breadcrumbs([('Home', '/en/'), ('Browse by Series', '/en/series-index/')]), 'Browse by Series', 'Category pages from DQ1 to DQ11.', metric('Pages', '11') + metric('Language', 'English / Japanese') + metric('Purpose', 'Series search landing'), action('/en/category-index/', 'Browse categories', primary=True) + action('https://www.youtube.com/@chamberd_piano', 'Visit YouTube', external=True), '', section('Series', 'DQ1–DQ11', entry_grid(en_series_cards), 'Each page leads into song lists and the YouTube channel.'))
    category_index_ja = make_head('ja', f'カテゴリ別ページ一覧 | {JA_LIBRARY_NAME}', 'フィールド曲・戦闘曲・街村・エンディング・メドレーのカテゴリ別ページ一覧です。', BASE + '/category-index/', BASE + '/category-index/', BASE + '/en/category-index/', [website_json('ja'), breadcrumb_json([('ホーム', '/'), ('カテゴリ別ページ一覧', '/category-index/')]), {'@type': 'CollectionPage', 'name': 'カテゴリ別ページ一覧', 'description': 'カテゴリ別ページ一覧です。', 'url': BASE + '/category-index/', 'inLanguage': 'ja-JP'}]) + shell('ja', '/category-index/', '/en/category-index/', breadcrumbs([('ホーム', '/'), ('カテゴリ別ページ一覧', '/category-index/')]), 'カテゴリ別ページ一覧', 'フィールド曲・戦闘曲・街村・エンディング・メドレーをカテゴリ別にまとめています。', metric('カテゴリ数', str(len(CATS) - 1)) + metric('言語', '日本語 / English') + metric('目的', 'カテゴリ検索の入口'), action('/series-index/', '作品別ページも見る', primary=True) + action('https://www.youtube.com/@chamberd_piano', 'YouTubeチャンネルを見る', external=True), playlist_cards(medley_playlists[:2], 'ja', hero=True), section('Categories', 'カテゴリ別ページ', entry_grid(ja_cat_cards), 'フィールド曲や戦闘曲などの探し方に対応しています。') + section('BGM', '作業用BGM', entry_grid(ja_bgm_cards), 'メドレーを作業用BGM向けにまとめています。'))
    category_index_en = make_head('en', f'Browse by Category | {EN_LIBRARY_NAME}', 'Landing pages for opening themes, casino tracks, churches, battles, endings, and medleys.', BASE + '/en/category-index/', BASE + '/category-index/', BASE + '/en/category-index/', [website_json('en'), breadcrumb_json([('Home', '/en/'), ('Browse by Category', '/en/category-index/')]), {'@type': 'CollectionPage', 'name': 'Browse by Category', 'description': 'Category landing pages.', 'url': BASE + '/en/category-index/', 'inLanguage': 'en-US'}]) + shell('en', '/en/category-index/', '/category-index/', breadcrumbs([('Home', '/en/'), ('Browse by Category', '/en/category-index/')]), 'Browse by Category', 'Opening themes, casino tracks, churches, battles, endings, and medleys.', metric('Categories', str(len(CATS) - 1)) + metric('Language', 'English / Japanese') + metric('Purpose', 'Search landing pages'), action('/en/series-index/', 'Browse series', primary=True) + action('https://www.youtube.com/@chamberd_piano', 'Visit YouTube', external=True), playlist_cards(medley_playlists[:2], 'en', hero=True), section('Categories', 'Category Pages', entry_grid(en_cat_cards), 'Built for clearer discovery across search intents.') + section('BGM', 'Background Listening', entry_grid(en_bgm_cards), 'Medley pages are grouped for background listening.'))

    write('series-index/index.html', series_index_ja)
    write('series-index.html', series_index_ja)
    write('en/series-index/index.html', series_index_en)
    write('en/series-index.html', series_index_en)
    write('category-index/index.html', category_index_ja)
    write('category-index.html', category_index_ja)
    write('en/category-index/index.html', category_index_en)
    write('en/category-index.html', category_index_en)

    urls.extend([BASE + '/series-index/', BASE + '/en/series-index/', BASE + '/category-index/', BASE + '/en/category-index/'])
    patch_home('index.html', 'ja', series_playlists)
    patch_home('en/index.html', 'en', series_playlists)
    (ROOT / 'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: ' + BASE + '/sitemap.xml\n', encoding='utf-8')
    def sitemap_url_xml(url: str) -> str:
        video = SONG_VIDEO_ENTRIES.get(url)
        if not video:
            return f'<url><loc>{url}</loc></url>'
        parts = [
            f'<video:thumbnail_loc>{esc(video["thumbnail"])}</video:thumbnail_loc>',
            f'<video:title>{esc(video["title"])}</video:title>',
            f'<video:description>{esc(video["description"])}</video:description>',
            f'<video:player_loc>{esc(video["player_loc"])}</video:player_loc>',
        ]
        if video.get('publication_date'):
            parts.append(f'<video:publication_date>{esc(video["publication_date"])}</video:publication_date>')
        return f'<url><loc>{url}</loc><video:video>' + ''.join(parts) + '</video:video></url>'

    (ROOT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">'
        + ''.join(sitemap_url_xml(url) for url in urls) + '</urlset>',
        encoding='utf-8',
    )
    print('generated', len(urls), 'urls')


if __name__ == '__main__':
    build()
