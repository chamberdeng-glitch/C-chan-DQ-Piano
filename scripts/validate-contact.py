from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOTS = {
    'category', 'category-index', 'contact', 'dq1', 'dq2', 'dq3', 'dq4', 'dq5',
    'dq6', 'dq7', 'dq8', 'dq9', 'dq10', 'dq11', 'en', 'privacy', 'score', 'series-index',
}


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f'{label}: missing {needle!r}')


def public_html_files() -> list[Path]:
    files = [ROOT / 'index.html', ROOT / 'category-index.html', ROOT / 'series-index.html']
    files.extend(
        path for path in ROOT.rglob('*.html')
        if path.relative_to(ROOT).parts[0] in PUBLIC_ROOTS
    )
    return sorted(set(files))


def main() -> None:
    pages = {
        '/contact/': ROOT / 'contact/index.html',
        '/en/contact/': ROOT / 'en/contact/index.html',
        '/privacy/': ROOT / 'privacy/index.html',
        '/en/privacy/': ROOT / 'en/privacy/index.html',
    }
    for url, path in pages.items():
        text = path.read_text(encoding='utf-8')
        require(text, f'<link rel="canonical" href="https://dqpiano.com{url}">', str(path))
        require(text, 'hreflang="ja"', str(path))
        require(text, 'hreflang="en"', str(path))
        require(text, 'hreflang="x-default"', str(path))
        require(text, 'class="site-legal-links"', str(path))

    for path in (pages['/contact/'], pages['/en/contact/']):
        text = path.read_text(encoding='utf-8')
        for needle in (
            'fetch("/api/contact"', 'data-contact-form', 'aria-live="polite"',
            'aria-hidden="true"', 'tabindex="-1"', 'autocomplete="off"',
            'challenges.cloudflare.com/turnstile/v0/api.js?render=explicit',
        ):
            if needle == 'fetch("/api/contact"':
                require((ROOT / 'assets/contact.js').read_text(encoding='utf-8'), needle, 'contact.js')
            else:
                require(text, needle, str(path))

    sitemap = (ROOT / 'sitemap.xml').read_text(encoding='utf-8')
    for url in pages:
        require(sitemap, f'<loc>https://dqpiano.com{url}</loc>', 'sitemap.xml')

    contact_script_pages = []
    for path in public_html_files():
        text = path.read_text(encoding='utf-8', errors='ignore')
        if 'challenges.cloudflare.com/turnstile/v0/api.js' in text:
            contact_script_pages.append(path.relative_to(ROOT).as_posix())
    expected = ['contact/index.html', 'en/contact/index.html']
    if sorted(contact_script_pages) != sorted(expected):
        raise AssertionError(f'Turnstile script scope mismatch: {contact_script_pages}')

    worker_sources = (ROOT / 'src/contact.js').read_text(encoding='utf-8')
    if 'dqpiano.c@gmail.com' in worker_sources:
        raise AssertionError('recipient address must not be hardcoded in source')
    for name in ('CONTACT_TO_EMAIL', 'CONTACT_FROM_EMAIL', 'TURNSTILE_SECRET_KEY', 'CONTACT_HASH_SALT'):
        require(worker_sources, name, 'src/contact.js')

    generated_html = public_html_files()
    missing_legal = []
    for path in generated_html:
        text = path.read_text(encoding='utf-8', errors='ignore')
        if '<footer' in text and 'site-legal-links' not in text:
            missing_legal.append(path.relative_to(ROOT).as_posix())
    if missing_legal:
        raise AssertionError(f'footer legal links missing: {missing_legal[:10]}')

    print(f'validated contact/privacy pages: {len(pages)}')
    print(f'validated legal footer pages: {sum(1 for path in generated_html if "<footer" in path.read_text(encoding="utf-8", errors="ignore"))}')


if __name__ == '__main__':
    main()
