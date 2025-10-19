#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from collections import OrderedDict, defaultdict


def git(cmd):
    return subprocess.check_output(cmd, text=True).strip()


def load_json_text(text):
    try:
        return json.loads(text)
    except Exception:
        return None


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = os.path.join(root, "comics.json")
    if not os.path.exists(path):
        print("ERROR: comics.json not found", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        current = json.load(f)

    if not isinstance(current, dict) or not isinstance(current.get("comics"), list):
        print("ERROR: comics.json structure invalid", file=sys.stderr)
        sys.exit(1)

    # Current mapping by file
    cur_by_file = OrderedDict()
    for c in current["comics"]:
        fn = c.get("file")
        if not isinstance(fn, str):
            continue
        cur_by_file[fn] = c

    # Walk history and capture slugs seen for each file
    history_slugs = defaultdict(list)  # file -> list of slugs in chronological order
    try:
        commits = git(["git", "rev-list", "--reverse", "HEAD", "--", "comics.json"]).splitlines()
    except subprocess.CalledProcessError:
        commits = []

    for sha in commits:
        if not sha:
            continue
        try:
            text = git(["git", "show", f"{sha}:comics.json"]) 
        except subprocess.CalledProcessError:
            continue
        data = load_json_text(text)
        if not data or not isinstance(data.get("comics"), list):
            continue
        for c in data["comics"]:
            fn = c.get("file")
            slug = c.get("slug")
            if not isinstance(fn, str) or not isinstance(slug, str):
                continue
            seen = history_slugs[fn]
            if slug not in seen:
                seen.append(slug)

    # Update current comics with aliases from history, excluding the current slug
    updated = 0
    for fn, c in cur_by_file.items():
        cur_slug = c.get("slug")
        hist = history_slugs.get(fn, [])
        # Keep order as seen in history, but drop current slug and duplicates
        candidates = [s for s in hist if isinstance(s, str) and s != cur_slug]
        # Merge with existing aliases if present
        existing = c.get("aliases") if isinstance(c.get("aliases"), list) else []
        merged = []
        for s in existing + candidates:
            if isinstance(s, str) and s and s not in merged and s != cur_slug:
                merged.append(s)
        if merged:
            if c.get("aliases") != merged:
                c["aliases"] = merged
                updated += 1
        else:
            if "aliases" in c:
                del c["aliases"]

    if updated:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"Updated aliases for {updated} comics from history.")
    else:
        print("No alias updates needed.")


if __name__ == "__main__":
    main()

