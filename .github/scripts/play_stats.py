#!/usr/bin/env python3
"""Scrape the VPNi Google Play listing and write shields.io endpoint JSON.

Play has no public JSON API and shields.io dropped its google-play route, so we
scrape the listing HTML on a cron and self-host the badge data in-repo. Each
field is written only if it parses — a layout change never overwrites good data
with garbage (the badge just goes stale until the selector is fixed).
"""
import json, re, sys, urllib.request
from pathlib import Path

APP_ID = "com.vpni.android"
URL = f"https://play.google.com/store/apps/details?id={APP_ID}&hl=en&gl=US"
BADGES = Path(__file__).resolve().parents[1] / "badges"


def fetch() -> str:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def endpoint(label, message, color):
    return {"schemaVersion": 1, "label": label, "message": message, "color": color}


def write(name, data):
    (BADGES / f"{name}.json").write_text(json.dumps(data) + "\n")
    print(f"wrote {name}: {data['message']}")


def main():
    html = fetch()

    rating = re.search(r'"ratingValue":"?([0-9.]+)', html)
    reviews = re.search(r'"ratingCount":"?([0-9]+)', html)
    installs = re.findall(r'"([0-9][0-9.]*[KMB]\+)"', html)  # unique compact token, e.g. 10K+

    ok = True
    if rating:
        write("rating", endpoint("★", f"{float(rating.group(1)):.1f}", "FFA41C"))
    else:
        ok = False; print("::warning::rating not found", file=sys.stderr)
    if reviews:
        write("reviews", endpoint("reviews", f"{int(reviews.group(1)):,}", "2A2A2A"))
    else:
        ok = False; print("::warning::reviews not found", file=sys.stderr)
    if installs:
        write("installs", endpoint("installs", installs[0], "3DDC84"))
    else:
        ok = False; print("::warning::installs not found", file=sys.stderr)

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
