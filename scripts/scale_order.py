#!/usr/bin/env python3
import json
import os
import sys


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    path = os.path.join(root, "comics.json")
    factor = 10

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

    updated = 0
    for c in comics:
        v = c.get("order")
        if isinstance(v, int):
            c["order"] = v * factor
            updated += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Scaled order for {updated} comics by factor {factor}")


if __name__ == "__main__":
    main()

