AGI Comics Static Site

Overview

- Static site generator that turns images in `comics/` into xkcd-style pages.
- Each page shows one comic with prev/next arrows (circular), current index, title, description, permalinks, direct image link, and share buttons (X, Bluesky, Reddit).
- Social previews are generated via Open Graph/Twitter meta tags pointing to the comic image.

Quick Start

1) Put comic images in `comics/` (png/jpg/jpeg/webp/gif). Keep editing them as needed.

2) Generate or update metadata:

   - `python3 scripts/generate_comics_json.py`

   This creates/updates `comics.json`. It preserves existing titles/descriptions and adds new files.

3) Build the site into `public/`:

   - `python3 scripts/build_site.py`

   - Optional: set a fully-qualified base URL for proper OG/Twitter cards:
     `BASE_URL="https://your-domain.com" python3 scripts/build_site.py`

Output

- Pages at `/public/1/`, `/public/2/`, … and slug permalinks at `/public/c/<slug>/` (canonical). Circular prev/next use slugs.
 - Home `/public/index.html` is the latest comic (slug canonical).
- Images copied to `/public/images/<slug>.<ext>`.
- `robots.txt` and a minimal `404.html` are included.

Editing Metadata

- Open `comics.json` and edit `title` and `description` for each comic.
- Re-run the build step to update pages.

Notes

- Index is displayed (e.g., “Comic #12”) without the total count, as requested.
- Social previews use the direct comic image via `og:image`/`twitter:image`.
- If Pillow is available, WebP versions are generated for faster loads and used on pages; OG still points to the original PNG/JPEG for compatibility.

GitHub Pages (dileeplearning.github.io/agicomics)

- Configure base path and absolute URL when building so links work under the project path:

  - `BASE_PATH="/agicomics/" BASE_URL="https://dileeplearning.github.io/agicomics" python3 scripts/build_site.py`

- Option A: Deploy from `gh-pages` branch (root)

  1) Initialize and push code:
     - `git init`
     - `git add . && git commit -m "init"`
     - `git branch -M main`
     - `git remote add origin git@github.com:dileeplearning/agicomics.git` (or https URL)
     - `git push -u origin main`

  2) Publish the built site to `gh-pages`:
     - `git checkout --orphan gh-pages`
     - `git reset --hard`
     - `cp -R public/* .`
     - `git add . && git commit -m "Publish"`
     - `git push -u origin gh-pages`
     - In GitHub → Repo Settings → Pages: set Source to `gh-pages` / `/ (root)`.
     - `git checkout main`

- Option B: Deploy from `docs/` on `main`

  1) Build with base path and URL as above.
  2) Copy build to `docs/` and commit:
     - `rm -rf docs && mkdir docs && cp -R public/* docs/`
     - `git add docs && git commit -m "Publish docs" && git push`
  3) In GitHub → Repo Settings → Pages: set Source to `main` / `/docs`.

Notes

- The build writes a `.nojekyll` file so GitHub Pages serves assets as-is.
- You can also set `base_path` and `base_url` in `site_config.json` instead of env vars; env vars override file values.

GitHub Actions auto-deploy (recommended)

- This repo includes `.github/workflows/deploy.yml` which:
  - Builds the site on every push to `main` with `BASE_URL=https://dileeplearning.github.io` and `BASE_PATH=/agicomics/`.
  - Publishes `public/` to the `gh-pages` branch using `peaceiris/actions-gh-pages`.

Enable it

- Push the repo to GitHub (see Option A step 1).
- In GitHub → Repo Settings → Pages:
  - Set Source: Deploy from a branch
  - Branch: `gh-pages` and folder `/ (root)`
- Push to `main` again; the workflow publishes to `gh-pages` automatically.
- Share links use standard intent URLs for X, Bluesky, and Reddit.
