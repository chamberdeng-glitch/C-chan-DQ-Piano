# Deployment

This site is deployed to Cloudflare Workers from the `cloudflare/workers-autoconfig` branch.

## Normal Flow

1. Edit source data or pages locally.
2. Run `python3 build-seo-pages.py`.
3. Optionally run `python3 build-worker-assets.py` to check the Cloudflare asset bundle.
4. Commit the intended files.
5. Push to `origin cloudflare/workers-autoconfig`.
6. GitHub Actions regenerates pages, builds `dist/`, runs `wrangler deploy`, and publishes the Worker directly.

Cloudflare dashboard promotion should not be needed for the normal flow.

Only `dist/` is deployed. Local credentials, Discord bot files, and `sedori_works/` are intentionally excluded from the public asset bundle.

## Required GitHub Secrets

Set these secrets on the GitHub repository that owns the deployment branch:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

The API token should be scoped to the Cloudflare account and Worker needed for this site. Do not commit token values to the repository.

## Remote Naming

Recommended local remotes:

- `origin`: `https://github.com/chamberdeng-glitch/C-chan-DQ-Piano.git`
- `fork`: `https://github.com/kojikazu0520-web/C-chan-DQ-Piano.git`

Use `origin` for production deployment work.
