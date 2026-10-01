# C-chan DQ Piano

Dragon Quest piano channel website for C-chan piano.

The site is a static Cloudflare Workers asset project. The top page and generated landing pages organize YouTube videos by Dragon Quest series and song category.

## Main Files

- `index.html`: Japanese top page
- `site.js`: top-page rendering and filtering
- `playlist-data.js`: playlist data
- `song-reference-data.js`: song metadata, YouTube links, categories, and difficulty
- `build-seo-pages.py`: generates series/category landing pages
- `analytics.js`: GA4 page context and click tracking
- `wrangler.jsonc`: Cloudflare Workers configuration

## Local Checks

```sh
python3 build-seo-pages.py
node --check analytics.js
node --check site.js
```

## Deployment

Production deploys from the `cloudflare/workers-autoconfig` branch.

See `DEPLOYMENT.md` for the GitHub Actions and Cloudflare setup.
