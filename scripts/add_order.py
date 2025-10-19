#!/usr/bin/env python3
import json
import os
import sys


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = os.path.join(root, "comics.json")
    if not os.path.exists(path):
        print("ERROR: comics.json not found", file=sys.stderr)
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"ERROR: failed to parse comics.json: {e}", file=sys.stderr)
            sys.exit(1)

    comics = data.get("comics")
    if not isinstance(comics, list):
        print("ERROR: comics.json does not contain a 'comics' list", file=sys.stderr)
        sys.exit(1)

    added = 0
    updated = 0
    for i, c in enumerate(comics, start=1):
        # If an order already exists and is an int, keep it; otherwise set sequential
        v = c.get("order")
        if isinstance(v, int):
            updated += 1
            continue
        c["order"] = i
        added += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Processed {len(comics)} comics; added order to {added}, preserved {updated}")


if __name__ == "__main__":
    main()

