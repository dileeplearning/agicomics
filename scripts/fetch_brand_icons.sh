#!/usr/bin/env bash
set -euo pipefail
root_dir="$(cd "$(dirname "$0")/.." && pwd)"
icons_dir="$root_dir/assets/icons"
mkdir -p "$icons_dir"

echo "Fetching official brand SVGs into $icons_dir"

fetch_first() {
  out="$1"; shift
  for url in "$@"; do
    echo "-> trying $url"
    if curl -fsSL "$url" -o "$out"; then
      echo "ok: $out"
      return 0
    fi
  done
  echo "failed: $out" >&2
  return 1
}

# X (Twitter) logo candidates
fetch_first "$icons_dir/x.svg" \
  "https://upload.wikimedia.org/wikipedia/commons/2/2e/X_logo_2023.svg" \
  "https://upload.wikimedia.org/wikipedia/commons/5/53/X_logo_2023_original.svg" \
  "https://upload.wikimedia.org/wikipedia/en/c/ce/X_logo_2023.svg"

# Bluesky logo candidates
fetch_first "$icons_dir/bluesky.svg" \
  "https://upload.wikimedia.org/wikipedia/commons/7/78/Bluesky_Logo.svg" \
  "https://upload.wikimedia.org/wikipedia/commons/7/7a/Bluesky_Logo.svg" \
  "https://upload.wikimedia.org/wikipedia/commons/1/17/Bluesky_logo.svg"

# Reddit logo candidates
fetch_first "$icons_dir/reddit.svg" \
  "https://upload.wikimedia.org/wikipedia/en/5/58/Reddit_logo_new.svg" \
  "https://upload.wikimedia.org/wikipedia/commons/5/58/Reddit_logo_new.svg" \
  "https://upload.wikimedia.org/wikipedia/en/8/82/Reddit_logo_and_wordmark.svg"

echo "Done. Files:"
ls -la "$icons_dir"
