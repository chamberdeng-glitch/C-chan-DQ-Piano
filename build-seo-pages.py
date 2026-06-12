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


# 曲別ページを持つ曲のID -> ページパス。build() 冒頭で song-page-content.js から作る。
SONG_PAGE_PATHS: dict[str, str] = {}


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
        '<link rel="stylesheet" href="/styles.css">'
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


def song_table(rows: list[dict], lang: str) -> str:
    headers = ('曲番号', '曲名', 'カテゴリ', '難易度') if lang == 'ja' else ('No.', 'Title', 'Category', 'Difficulty')
    body = []
    for row in rows:
        title = row['songTitle'] if lang == 'ja' else row['songTitleEn']
        category = row['category'] if lang == 'ja' else row['categoryEn']
        difficulty = (row.get('difficultyLabel') or '未設定') if lang == 'ja' else (row.get('difficultyEn') or 'Not set')
        difficulty_stars = row.get('difficultyStars')
        page_path = SONG_PAGE_PATHS.get(row['id']) if lang == 'ja' else None
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
            f'<td data-label="{esc(headers[3])}">{render_difficulty_html(difficulty, difficulty_stars)}</td>'
            '</tr>'
        )
    return (
        '<div class="song-table-wrap seo-song-table-wrap"><div class="song-table-scroll">'
        '<table class="song-table"><thead><tr>'
        f'<th>{headers[0]}</th><th>{headers[1]}</th><th>{headers[2]}</th><th>{headers[3]}</th>'
        '</tr></thead><tbody>' + ''.join(body) + '</tbody></table></div></div>'
    )


def render_difficulty_html(label: str, stars: int | None) -> str:
    filled = max(0, min(5, stars)) if isinstance(stars, int) else 0
    empty = 5 - filled
    star_text = ('★' * filled) + ('☆' * empty)
    extra_class = ' is-empty' if filled == 0 else ''
    aria = f'{label} {filled}/5' if filled else label
    return (
        '<span class="difficulty-cell">'
        f'<span class="difficulty-text">{esc(label)}</span>'
        f'<span class="difficulty-stars{extra_class}" aria-label="{esc(aria)}">{star_text}</span>'
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
    'iframe.src="https://www.youtube-nocookie.com/embed/"+id+"?autoplay=1";'
    'iframe.title=wrap.dataset.videoTitle||"YouTube video";'
    'iframe.allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";'
    'iframe.allowFullscreen=true;'
    'wrap.replaceChildren(iframe);'
    '},{once:true});'
    '});'
    '</script>'
)


def song_facade(vid: str, video_title: str, thumb: str) -> str:
    return (
        f'<div class="yt-facade" data-video-id="{esc(vid)}" data-video-title="{esc(video_title)}">'
        f'<button class="yt-facade-btn" type="button" aria-label="{esc(video_title)}を再生">'
        f'<img src="{thumb}" alt="{esc(video_title)}のサムネイル" width="480" height="360" loading="eager" fetchpriority="high">'
        '<span class="yt-facade-play" aria-hidden="true"></span>'
        '</button></div>'
    )


def song_difficulty_text(row: dict) -> str:
    stars = row.get('difficultyStars')
    label = row.get('difficultyLabel', '')
    if not stars:
        return label or '未設定'
    return f'{label} ' + '★' * stars + '☆' * (5 - stars)


def song_neighbor_card(neighbor: dict | None, label: str) -> str:
    if not neighbor:
        return ''
    page_path = SONG_PAGE_PATHS.get(neighbor['id'])
    if page_path:
        return entry_card(page_path, f'{label}: {neighbor["songTitle"]}', f'{neighbor["id"]} / {neighbor["category"]}')
    if neighbor.get('videoUrl'):
        return (
            f'<a class="entry-card" href="{neighbor["videoUrl"]}" target="_blank" rel="noreferrer">'
            f'<span class="entry-card-title">{label}: {esc(neighbor["songTitle"])}</span>'
            f'<span class="entry-card-body">{esc(neighbor["id"])} / {esc(neighbor["category"])} / YouTubeで見る</span></a>'
        )
    return ''


def write_song_page(row: dict, prev_row: dict | None, next_row: dict | None, meta: dict) -> None:
    series = SERIES_MAP[row['seriesKey']]
    page = SONG_PAGE_PATHS[row['id']]
    canon = BASE + page
    vid = youtube_video_id(row['videoUrl'])
    thumb = f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'
    song_title = row['songTitle']
    video_title = f'{song_title}（{series["ja"]}）ピアノ演奏'

    title = f'{song_title} ピアノ | {series["ja"]} | {JA_LIBRARY_NAME}'
    desc = (
        f'{series["ja"]}の「{song_title}」のピアノ演奏ページです。'
        f'演奏動画と曲の情報、同シリーズや同カテゴリの曲への入口をまとめています。'
    )
    lead = meta.get('lead') or f'{series["ja"]}の{row["category"]}曲「{song_title}」のピアノ演奏です。'

    crumbs = [('ホーム', '/'), (series['code'], f'/{series["slug"]}/'), (song_title, page)]
    video_json = {
        '@type': 'VideoObject',
        'name': video_title,
        'description': desc,
        'thumbnailUrl': [thumb],
        'contentUrl': row['videoUrl'],
        'embedUrl': f'https://www.youtube.com/embed/{vid}',
    }
    if meta.get('uploadDate'):
        video_json['uploadDate'] = meta['uploadDate']
    graph = [website_json('ja'), breadcrumb_json(crumbs), video_json]

    head = make_head('ja', title, desc, canon, canon, canon, graph)
    # 英語版曲ページは未作成のため hreflang=en は出さない
    head = head.replace(f'<link rel="alternate" hreflang="en" href="{canon}">', '')
    head = head.replace(
        '<meta property="og:type" content="website">',
        '<meta property="og:type" content="video.other">',
    )
    og_image = (
        f'<meta property="og:image" content="{thumb}">'
        '<meta property="og:image:width" content="480">'
        '<meta property="og:image:height" content="360">'
        f'<meta property="og:image:alt" content="{esc(video_title)}のサムネイル">'
        f'<meta name="twitter:image" content="{thumb}">'
    )
    head = head.replace('<meta name="twitter:card"', og_image + '<meta name="twitter:card"')
    head = head.replace('</head>', SONG_STYLES + '</head>')

    metrics = ''.join([
        metric('カテゴリ', row['category']),
        metric('難易度', song_difficulty_text(row)),
        metric('収録作品', series['ja']),
    ])
    actions = ''.join([
        action(row['videoUrl'], 'YouTubeで見る', primary=True, external=True),
        action(f'/{series["slug"]}/', f'{series["code"]}の曲一覧'),
        action('https://www.youtube.com/@chamberd_piano', 'YouTubeチャンネルを見る', external=True),
    ])

    main = ''
    if meta.get('description'):
        main += section('About', 'この曲について', f'<p class="section-copy">{esc(meta["description"])}</p>')
    if meta.get('timestamps'):
        items = ''.join(
            f'<li><span class="song-link">{esc(ts["time"])}</span> {esc(ts["label"])}</li>'
            for ts in meta['timestamps']
        )
        main += section('Chapters', '演奏の流れ', f'<ul>{items}</ul>')

    related = [card for card in (
        song_neighbor_card(prev_row, '前の曲'),
        song_neighbor_card(next_row, '次の曲'),
    ) if card]
    related.append(entry_card(f'/{series["slug"]}/', f'{series["ja"]} の曲一覧', '作品別ページへ'))
    cat_slug = next((slug for slug, info in CATS.items() if row['category'] in info['match']), '')
    if cat_slug:
        related.append(entry_card(f'/category/{cat_slug}/', f'{row["category"]}の曲', 'カテゴリ別ページへ'))
    main += section('Related', '関連の曲とページ', entry_grid(related), '同じ作品・同じカテゴリの曲をたどれます。')

    html = head + shell(
        'ja', page, f'/en/{series["slug"]}/',
        breadcrumbs(crumbs),
        song_title, lead, metrics, actions,
        song_facade(vid, video_title, thumb),
        main,
    )
    html = html.replace('</body></html>', SONG_FACADE_SCRIPT + '</body></html>')
    write(Path(page[1:]) / 'index.html', html)


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
                f'{ja_name} の楽曲を作品別に探せるページです。ドラゴンクエスト ピアノ、{code} ピアノ、ゲーム音楽 ピアノの検索着地として、曲一覧とYouTube導線を整理しています。'
                if lang == 'ja' else
                f'Browse {en_name} piano performances with song links and YouTube playlist access.'
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
            main += section('Songs', '収録曲一覧' if lang == 'ja' else 'Song List', song_table(rows, lang), '曲番号順でたどれる一覧です。' if lang == 'ja' else 'Song list ordered by catalog number.')
            if special_rows:
                main += section(
                    'Special',
                    '特別収録' if lang == 'ja' else 'Special Selections',
                    song_table(special_rows, lang),
                    '過去シリーズ楽譜からの特別収録曲です。曲番号・リンクは出典元シリーズに合わせています。' if lang == 'ja' else 'Special selections from earlier series. Numbers and links follow the original source series.',
                )
            main += section('Related', '関連カテゴリ' if lang == 'ja' else 'Related Categories', related_category_cards(lang), 'フィールド曲・戦闘曲・メドレーなど横断導線を用意しています。' if lang == 'ja' else 'Cross-link into field, battle, and medley pages.')
            html = make_head(lang, title, desc, BASE + page, BASE + f'/{slug}/', BASE + f'/en/{slug}/', graph)
            html += shell(lang, page, alt, breadcrumbs(crumbs), f'{ja_name} ピアノ演奏ライブラリー' if lang == 'ja' else f'{en_name} Piano Library', desc, metrics, ''.join(actions), feature, main)
            write(Path(page[1:]) / 'index.html', html)
        urls.extend([BASE + f'/{slug}/', BASE + f'/en/{slug}/'])

        for i, row in enumerate(rows):
            if row['id'] not in SONG_PAGE_PATHS:
                continue
            prev_row = rows[i - 1] if i > 0 else None
            next_row = rows[i + 1] if i + 1 < len(rows) else None
            write_song_page(row, prev_row, next_row, song_content[row['id']])
            urls.append(BASE + SONG_PAGE_PATHS[row['id']])

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
            desc = (
                f'{info["ja"]} を作品横断で探せるページです。ドラゴンクエスト ピアノ、ドラクエ ピアノ演奏、作業用BGMの入口として使いやすく整理しています。'
                if lang == 'ja' else
                f'Browse {info["en"]} across the Dragon Quest piano library.'
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
                table_or_cards = song_table(rows, lang)
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
            main += section('Related', '関連作品' if lang == 'ja' else 'Related Series', entry_grid(related_cards), '関連作品へ回遊しやすい導線です。' if lang == 'ja' else 'Jump into related series pages.')
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
                '関連導線' if lang == 'ja' else 'Related Links',
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
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{url}</loc></url>' for url in urls) + '</urlset>', encoding='utf-8')
    print('generated', len(urls), 'urls')


if __name__ == '__main__':
    build()
