#!/usr/bin/env python3
"""
Web Dashboard for Sneaker Release Tracker.

Serves a live dashboard showing upcoming sneaker releases with filtering,
sorting, charts, and hype scores.

Usage:
    python dashboard.py              # runs on http://localhost:5000
    python dashboard.py --port 8080  # custom port
    python dashboard.py --refresh    # scrape fresh data on startup
"""

import argparse
import json
import os
from datetime import datetime, timedelta, date

from flask import Flask, jsonify, render_template, request

from hype import calculate_hype_score
from scraper import (
    scrape_sneakerfiles,
    scrape_nicekicks,
    scrape_sneakerbardetroit,
    deduplicate,
    enrich_sneaker,
    is_target_brand,
    LOOKAHEAD_DAYS,
    JSON_PATH,
)

app = Flask(__name__)

# In-memory cache of scraped releases
_cache: dict = {"releases": [], "last_updated": None, "source": None}

JSON_MTIME_SEEN: float = 0.0  # mtime of the JSON file last time we loaded it


def _load_releases(force_refresh: bool = False) -> list[dict]:
    """
    Return releases. Priority:
      1. reports/releases.json written by the workflow — reload whenever its
         mtime changes so the dashboard auto-updates after every workflow run.
      2. Live scrape — used as fallback when the JSON doesn't exist yet, or
         when the caller explicitly requests a refresh.
    """
    global JSON_MTIME_SEEN

    if not force_refresh and os.path.exists(JSON_PATH):
        mtime = os.path.getmtime(JSON_PATH)
        if mtime != JSON_MTIME_SEEN or not _cache["releases"]:
            _read_json_snapshot()
            JSON_MTIME_SEEN = mtime
        return _cache["releases"]

    # Fallback: live scrape (or explicit refresh)
    now = datetime.now()
    cache_age = (now - _cache["last_updated"]).total_seconds() if _cache["last_updated"] else 9999
    if force_refresh or cache_age > 1800 or not _cache["releases"]:
        _cache["releases"] = _scrape_all()
        _cache["last_updated"] = now
        _cache["source"] = "live"

    return _cache["releases"]


def _read_json_snapshot():
    """Load releases from the JSON file produced by the workflow."""
    with open(JSON_PATH, encoding="utf-8") as fh:
        data = json.load(fh)

    releases = []
    for r in data.get("releases", []):
        r["release_date_iso"] = r["release_date"]
        releases.append(r)

    _cache["releases"] = releases
    _cache["last_updated"] = datetime.now()
    _cache["source"] = "workflow snapshot"


def _scrape_all() -> list[dict]:
    """Scrape all sources and return normalized, filtered releases."""
    today = date.today()
    cutoff = today + timedelta(days=LOOKAHEAD_DAYS)

    all_releases = []
    for scraper_fn in [scrape_sneakerfiles, scrape_nicekicks, scrape_sneakerbardetroit]:
        try:
            all_releases.extend(scraper_fn())
        except Exception:
            pass

    filtered = []
    for r in all_releases:
        if not is_target_brand(r["brand"]):
            continue
        rd = r["release_date"]
        if rd < today or rd > cutoff:
            continue
        r = enrich_sneaker(r)
        r["days_until_release"] = (rd - today).days
        r["release_date_iso"] = rd.isoformat()
        r["release_date"] = datetime.combine(rd, datetime.min.time())
        r["estimated_market_value"] = None
        r["silhouette"] = ""
        r.setdefault("source_url", "")
        score, level = calculate_hype_score(r)
        r["hype_score"] = score
        r["hype_level"] = level
        filtered.append(r)

    filtered = deduplicate(filtered)
    filtered.sort(key=lambda s: s["release_date"])
    return filtered


def _release_to_dict(r: dict) -> dict:
    """Convert a release record to a JSON-serializable dict."""
    return {
        "name": r.get("name", ""),
        "brand": r.get("brand", ""),
        "release_date": r.get("release_date_iso", ""),
        "days_until_release": r.get("days_until_release", 0),
        "retail_price": r.get("retail_price"),
        "estimated_market_value": r.get("estimated_market_value"),
        "colorway": r.get("colorway", "N/A"),
        "style_code": r.get("style_code", "N/A"),
        "hype_score": r.get("hype_score", 0),
        "hype_level": r.get("hype_level", "LOW"),
        "source": r.get("source", ""),
        "source_url": r.get("source_url", ""),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    releases = _load_releases()
    serializable = [_release_to_dict(r) for r in releases]

    # Summary stats
    total = len(releases)
    extreme = sum(1 for r in releases if r["hype_level"] == "EXTREME")
    high = sum(1 for r in releases if r["hype_level"] == "HIGH")
    urgent = sum(1 for r in releases if r["days_until_release"] <= 7)

    # Brand counts for chart
    brand_counts: dict[str, int] = {}
    for r in releases:
        brand_counts[r["brand"]] = brand_counts.get(r["brand"], 0) + 1

    # Hype level counts
    hype_counts = {"EXTREME": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in releases:
        hype_counts[r["hype_level"]] = hype_counts.get(r["hype_level"], 0) + 1

    if os.path.exists(JSON_PATH):
        import json as _json
        with open(JSON_PATH, encoding="utf-8") as fh:
            meta = _json.load(fh)
        last_updated = meta.get("generated_at", "Unknown")
        data_source = "workflow"
    else:
        last_updated = _cache["last_updated"].strftime("%Y-%m-%d %H:%M UTC") if _cache["last_updated"] else "Never"
        data_source = "live scrape"

    return render_template(
        "index.html",
        releases_json=json.dumps(serializable),
        total=total,
        extreme=extreme,
        high=high,
        urgent=urgent,
        brand_counts=json.dumps(brand_counts),
        hype_counts=json.dumps(hype_counts),
        last_updated=last_updated,
        data_source=data_source,
        lookahead_days=LOOKAHEAD_DAYS,
    )


@app.route("/api/releases")
def api_releases():
    """JSON API — returns all releases with optional filters."""
    releases = _load_releases()
    data = [_release_to_dict(r) for r in releases]

    brand = request.args.get("brand", "").strip().lower()
    hype = request.args.get("hype_level", "").strip().upper()
    days = request.args.get("max_days", type=int)

    if brand:
        data = [r for r in data if r["brand"].lower() == brand]
    if hype:
        data = [r for r in data if r["hype_level"] == hype]
    if days is not None:
        data = [r for r in data if r["days_until_release"] <= days]

    return jsonify({"releases": data, "count": len(data)})


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """Force a fresh scrape."""
    _load_releases(force_refresh=True)
    last_updated = _cache["last_updated"].strftime("%Y-%m-%d %H:%M UTC") if _cache["last_updated"] else "Never"
    return jsonify({"status": "ok", "count": len(_cache["releases"]), "last_updated": last_updated})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sneaker Release Dashboard")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--refresh", action="store_true", help="Scrape fresh data on startup")
    args = parser.parse_args()

    if args.refresh:
        print("Scraping fresh data on startup...")
        _load_releases(force_refresh=True)

    app.run(host=args.host, port=args.port, debug=False)
