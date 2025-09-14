AGI Comics — Build & Deploy to GitHub Pages

Overview

- This project builds a static comic site into `public/` and publishes it at a GitHub Pages Project Site: `https://dileeplearning.github.io/agicomics/`.
- Defaults in `site_config.json` are set for the above URL and base path.
- A GitHub Actions workflow is included to auto‑deploy on every push to `main`.

Prerequisites

- Python 3.8+
- Git + a GitHub repository (e.g., `dileeplearning/agicomics`)

Build locally

1) Generate or refresh comic metadata (creates/updates `comics.json`):

   - `python3 scripts/generate_comics_json.py`

2) Build the site (writes to `public/`):

   - `python3 scripts/build_site.py`

   Notes:
   - `site_config.json` already has `base_url` and `base_path` for `dileeplearning.github.io/agicomics`.
   - To override at build time, set env vars:
     `BASE_URL="https://dileeplearning.github.io" BASE_PATH="/agicomics/" python3 scripts/build_site.py`

3) Preview locally:

   - `python3 -m http.server 8080 -d public`
   - Open: `http://localhost:8080/agicomics/`

Initial repository setup

1) Initialize and push the code:

   - `git init`
   - `git add . && git commit -m "init"`
   - `git branch -M main`
   - `git remote add origin git@github.com:dileeplearning/agicomics.git` (or HTTPS URL)
   - `git push -u origin main`

Enable GitHub Pages (Project Site)

- In GitHub → Repository → Settings → Pages:
  - Source: Deploy from a branch
  - Branch: `gh-pages`
  - Folder: `/ (root)`

Automatic deploys (recommended)

- This repo includes `.github/workflows/deploy.yml` that:
  - Builds the site on every push to `main` with `BASE_URL=https://dileeplearning.github.io` and `BASE_PATH=/agicomics/`.
  - Publishes `public/` to the `gh-pages` branch using `peaceiris/actions-gh-pages`.
- After enabling Pages as above, push to `main` and the workflow will publish automatically.

Manual deploy alternative (if you prefer CLI)

1) Build (as above), then publish `public/` content to `gh-pages`:

   - `git checkout --orphan gh-pages`
   - `git reset --hard`
   - `cp -R public/* .`
   - `git add . && git commit -m "Publish"`
   - `git push -u origin gh-pages`
   - `git checkout main`

Docs/ folder alternative

- If you prefer serving from `docs/` on `main`:
  - `rm -rf docs && mkdir docs && cp -R public/* docs/`
  - `git add docs && git commit -m "Publish docs" && git push`
  - In Settings → Pages: set Source to `main` / `/docs`.

Updating comics

- Add images to `comics/` (png/jpg/jpeg/webp/gif).
- Run: `python3 scripts/generate_comics_json.py` (preserves existing titles/descriptions).
- Optionally edit `comics.json` to refine `title` / `description`.
- Run: `python3 scripts/build_site.py`
- Commit & push to `main` — the workflow deploys automatically.

Brand icons

- Place official SVGs in `assets/icons/` (filenames: `x.svg`, `bluesky.svg`, `reddit.svg`).
- The build copies them to `public/icons/` and uses them on pages.
- If any icon is missing, the build falls back gracefully.

Notes

- `public/` includes a `.nojekyll` file so GitHub Pages serves assets as-is.
- Internal links/assets are prefixed by `base_path` to work at `/agicomics/`.
- Canonical and social preview URLs (Open Graph / Twitter) are absolute using `base_url + base_path`.

