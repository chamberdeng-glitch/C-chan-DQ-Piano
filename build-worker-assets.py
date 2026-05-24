from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

ROOT_FILES = [
    "analytics.js",
    "app.js",
    "category-index.html",
    "en.html",
    "index.html",
    "playlist-data.js",
    "robots.txt",
    "series-index.html",
    "site-content.js",
    "site.js",
    "sitemap.xml",
    "song-reference-data.js",
    "song-title-translations.js",
    "styles.css",
]

DIRECTORIES = [
    "assets",
    "category-index",
    "category",
    "covers",
    "dq1",
    "dq2",
    "dq3",
    "dq4",
    "dq5",
    "dq6",
    "dq7",
    "dq8",
    "dq9",
    "dq10",
    "dq11",
    "en",
    "score",
    "series-index",
]


def copy_file(relative_path):
    source = ROOT / relative_path
    if not source.is_file():
        raise FileNotFoundError(f"Missing required asset: {relative_path}")
    target = DIST / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def copy_directory(relative_path):
    source = ROOT / relative_path
    if not source.is_dir():
        raise FileNotFoundError(f"Missing required asset directory: {relative_path}")
    shutil.copytree(source, DIST / relative_path)


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    for relative_path in ROOT_FILES:
        copy_file(relative_path)
    for relative_path in DIRECTORIES:
        copy_directory(relative_path)

    files = sum(1 for path in DIST.rglob("*") if path.is_file())
    print(f"Built {files} public assets in {DIST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
