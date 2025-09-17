#!/usr/bin/env python3
import json
import os
import re
import sys
from datetime import datetime

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def slugify(name: str) -> str:
    base = os.path.splitext(name)[0]
    s = base.strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"[^a-z0-9\-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "comic"


def title_from_slug(slug: str) -> str:
    words = slug.replace("-", " ").strip()
    return words.title() if words else "Untitled"


def load_existing(path: str):
    if not os.path.exists(path):
        return {"comics": []}
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict) or "comics" not in data:
                return {"comics": []}
            return data
        except json.JSONDecodeError:
            return {"comics": []}


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    comics_dir = os.path.join(root, "comics")
    out_path = os.path.join(root, "comics.json")

    if not os.path.isdir(comics_dir):
        print(f"ERROR: comics directory not found at {comics_dir}", file=sys.stderr)
        sys.exit(1)

    # Discover image files
    files = []
    for name in os.listdir(comics_dir):
        if name.startswith('.'):
            continue
        ext = os.path.splitext(name)[1].lower()
        if ext in IMAGE_EXTS:
            full = os.path.join(comics_dir, name)
            if os.path.isfile(full):
                files.append((name, full))

    if not files:
        print("No image files found in comics/", file=sys.stderr)
        sys.exit(1)

    # Sort by file modification time ascending (older first)
    files.sort(key=lambda t: os.path.getmtime(t[1]))

    existing = load_existing(out_path)
    existing_by_file = {c.get("file"): c for c in existing.get("comics", [])}
    # Track slugs we assign during this run to avoid duplicates while
    # preserving existing slugs for their own files.
    used_slugs = set()

    comics = []
    for (name, full) in files:
        mtime = os.path.getmtime(full)
        created = datetime.fromtimestamp(mtime).isoformat(timespec='seconds')
        ext = os.path.splitext(name)[1].lower()

        prev = existing_by_file.get(name)
        if prev:
            # Preserve existing slug if present
            slug = prev.get("slug") or slugify(name)
            base_slug = slug
            i = 2
            while slug in used_slugs:
                slug = f"{base_slug}-{i}"
                i += 1
            used_slugs.add(slug)

            title = prev.get("title") or title_from_slug(slug)
            desc = prev.get("description") or ""
            visible = prev.get("visible") if isinstance(prev.get("visible"), bool) else True
            # Preserve existing created date if available, otherwise use file mtime
            created_out = prev.get("created") or created
        else:
            slug = slugify(name)
            base_slug = slug
            i = 2
            while slug in used_slugs:
                slug = f"{base_slug}-{i}"
                i += 1
            used_slugs.add(slug)

            title = title_from_slug(slug)
            desc = ""
            visible = True
            created_out = created

        comics.append({
            "file": name,
            "slug": slug,
            "title": title,
            "description": desc,
            "created": created_out,
            "ext": ext,
            "visible": visible,
        })

    out = {"comics": comics}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote {out_path} with {len(comics)} comics")


if __name__ == "__main__":
    main()
