"""
Flask application – Sneaker Release Tracker
Routes:
  GET  /                   → Dashboard HTML
  GET  /api/releases       → Filtered JSON list
  GET  /api/stats          → Summary stats
  POST /api/refresh        → Trigger new scrape
  GET  /api/export/excel   → Download Excel file
"""

import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file

from scraper import scrape_all, save_releases, load_releases
from excel_export import export_to_excel

app = Flask(__name__)
DATA_FILE = "data/releases.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_filters(releases, args):
    brand       = args.get("brand",       "").strip()
    hype_min    = args.get("hype_min",    type=int)
    hype_max    = args.get("hype_max",    type=int)
    sale_method = args.get("sale_method", "").strip()
    search      = args.get("search",      "").strip().lower()
    sort_by     = args.get("sort_by",     "release_date")
    sort_order  = args.get("sort_order",  "asc")

    if brand:
        releases = [r for r in releases if brand.lower() in r.get("brand", "").lower()]
    if hype_min is not None:
        releases = [r for r in releases if r.get("hype_level", 1) >= hype_min]
    if hype_max is not None:
        releases = [r for r in releases if r.get("hype_level", 1) <= hype_max]
    if sale_method:
        releases = [r for r in releases
                    if any(sale_method.lower() in m.lower()
                           for m in r.get("sale_methods", []))]
    if search:
        releases = [r for r in releases
                    if search in r.get("name",  "").lower()
                    or search in r.get("brand", "").lower()]

    reverse = (sort_order == "desc")
    if sort_by == "release_date":
        releases = sorted(releases,
                          key=lambda r: "9999-99-99" if r.get("release_date") == "TBD"
                                        else (r.get("release_date") or "9999-99-99"),
                          reverse=reverse)
    elif sort_by == "price":
        releases = sorted(releases, key=lambda r: r.get("price") or 0, reverse=reverse)
    elif sort_by == "hype_level":
        releases = sorted(releases, key=lambda r: r.get("hype_level", 1), reverse=reverse)
    elif sort_by == "brand":
        releases = sorted(releases, key=lambda r: r.get("brand", ""), reverse=reverse)
    elif sort_by == "name":
        releases = sorted(releases, key=lambda r: r.get("name", ""), reverse=reverse)

    return releases


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/releases")
def get_releases():
    data     = load_releases(DATA_FILE)
    all_rels = data.get("releases", [])
    filtered = _apply_filters(list(all_rels), request.args)

    # Build dropdown option lists from the full (unfiltered) dataset
    brands = sorted({r.get("brand", "Other") for r in all_rels if r.get("brand")})
    methods = sorted({
        m for r in all_rels for m in r.get("sale_methods", [])
    })

    return jsonify({
        "releases":     filtered,
        "count":        len(filtered),
        "total":        len(all_rels),
        "last_updated": data.get("last_updated"),
        "brands":       brands,
        "sale_methods": methods,
    })


@app.route("/api/stats")
def get_stats():
    data     = load_releases(DATA_FILE)
    releases = data.get("releases", [])

    brand_counts = {}
    hype_dist    = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    today        = datetime.now().date()
    upcoming     = 0

    for r in releases:
        b = r.get("brand", "Other")
        brand_counts[b] = brand_counts.get(b, 0) + 1

        h = r.get("hype_level", 1)
        hype_dist[h] = hype_dist.get(h, 0) + 1

        d = r.get("release_date", "TBD")
        if d != "TBD":
            try:
                if datetime.strptime(d, "%Y-%m-%d").date() >= today:
                    upcoming += 1
            except ValueError:
                pass

    grail_count = sum(1 for r in releases if r.get("hype_level", 1) == 5)

    return jsonify({
        "total":              len(releases),
        "upcoming_count":     upcoming,
        "grail_count":        grail_count,
        "brand_counts":       brand_counts,
        "hype_distribution":  hype_dist,
        "last_updated":       data.get("last_updated"),
    })


@app.route("/api/refresh", methods=["POST"])
def refresh_data():
    try:
        releases = scrape_all()
        save_releases(releases, DATA_FILE)
        return jsonify({
            "success":      True,
            "count":        len(releases),
            "message":      f"Scraped {len(releases)} releases successfully",
            "last_updated": datetime.now().isoformat(),
        })
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


@app.route("/api/export/excel")
def export_excel():
    data     = load_releases(DATA_FILE)
    releases = _apply_filters(list(data.get("releases", [])), request.args)
    buf      = export_to_excel(releases)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        buf,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"sneaker_releases_{ts}.xlsx",
    )


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
