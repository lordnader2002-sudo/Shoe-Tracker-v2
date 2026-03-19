#!/usr/bin/env python3
"""
Sneaker Release Tracker — Main scraper script.
Fetches upcoming sneaker releases from The Sneaker Database API (RapidAPI)
and exports them to a formatted Excel report.
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta, timezone

import requests

from hype import calculate_hype_score
from excel_export import export_to_excel

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_HOST = "the-sneaker-database.p.rapidapi.com"
API_BASE = f"https://{API_HOST}"

TARGET_BRANDS = ["Nike", "Jordan", "Adidas", "Under Armour", "Yeezy", "New Balance"]

LOOKAHEAD_DAYS = 30  # How far ahead to look for releases
RESULTS_PER_PAGE = 100

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "reports", "sneaker_releases.xlsx")


def get_api_key() -> str:
    """Read the RapidAPI key from the environment."""
    key = os.environ.get("RAPIDAPI_KEY", "").strip()
    if not key:
        log.error("RAPIDAPI_KEY environment variable is not set.")
        sys.exit(1)
    return key


def fetch_sneakers_for_brand(brand: str, api_key: str) -> list[dict]:
    """
    Fetch sneakers for a single brand from The Sneaker Database API.
    Returns a list of raw sneaker dicts from the API response.
    """
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": API_HOST,
    }

    today = datetime.now(timezone.utc).date()
    cutoff = today + timedelta(days=LOOKAHEAD_DAYS)
    current_year = today.year

    all_sneakers = []
    page = 1

    while True:
        # Use only confirmed API params: brand, limit, page
        # releaseYear and sort may cause 500 errors
        params = {
            "brand": brand,
            "limit": str(RESULTS_PER_PAGE),
            "page": str(page),
        }

        log.info("Fetching %s page %d ...", brand, page)

        try:
            resp = requests.get(
                f"{API_BASE}/sneakers",
                headers=headers,
                params=params,
                timeout=15,
            )
        except requests.RequestException as exc:
            log.warning("Network error fetching %s page %d: %s", brand, page, exc)
            break

        if resp.status_code == 429:
            log.warning("Rate limited on %s — stopping pagination for this brand.", brand)
            break
        if resp.status_code in (401, 403):
            log.error("API auth error (%d). Check your RAPIDAPI_KEY.", resp.status_code)
            sys.exit(1)
        if resp.status_code != 200:
            body_preview = resp.text[:500] if resp.text else "(empty)"
            log.warning(
                "HTTP %d for %s page %d. Response: %s",
                resp.status_code, brand, page, body_preview,
            )
            break

        data = resp.json()

        # Log response shape on first call to help debug
        if page == 1:
            if isinstance(data, dict):
                log.info("Response keys for %s: %s", brand, list(data.keys()))
                total_pages = data.get("totalPages", "?")
                count = data.get("count", "?")
                log.info("Total results: %s, pages: %s", count, total_pages)
            elif isinstance(data, list):
                log.info("Response is a list with %d items for %s.", len(data), brand)

        # The API returns {"results": [...], "count": N, "totalPages": N}
        results = data if isinstance(data, list) else data.get("results", [])

        if not results:
            break

        all_sneakers.extend(results)

        # Check if there are more pages
        if isinstance(data, dict):
            total_pages = data.get("totalPages", 1)
            if page >= total_pages:
                break

        # If we got fewer than the limit, we've reached the last page
        if len(results) < RESULTS_PER_PAGE:
            break

        page += 1

        # Safety: don't fetch more than 3 pages per brand (to stay within API budget)
        if page > 3:
            log.info("Hit page limit for %s, moving on.", brand)
            break

        # Brief pause to be respectful of rate limits
        time.sleep(0.5)

    log.info("Fetched %d raw results for %s.", len(all_sneakers), brand)
    return all_sneakers


def parse_release_date(date_str: str | None) -> datetime | None:
    """
    Parse a release date string into a datetime object.
    Handles multiple formats the API might return.
    """
    if not date_str:
        return None

    date_str = str(date_str).strip()

    formats = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%m/%d/%Y",
        "%B %d, %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    log.debug("Could not parse date: %s", date_str)
    return None


def parse_price(value) -> float | None:
    """Parse a price value into a float. Returns None if invalid."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value) if value > 0 else None
    if isinstance(value, str):
        cleaned = value.replace("$", "").replace(",", "").strip()
        try:
            price = float(cleaned)
            return price if price > 0 else None
        except ValueError:
            return None
    return None


def normalize_sneaker(raw: dict) -> dict | None:
    """
    Normalize a raw API sneaker dict into our standard format.
    Returns None if the sneaker should be skipped (missing date, etc.).
    """
    # Try multiple possible field names the API might use
    release_date = parse_release_date(
        raw.get("releaseDate") or raw.get("release_date") or raw.get("releasedate")
    )

    if release_date is None:
        return None

    today = datetime.now(timezone.utc)
    cutoff = today + timedelta(days=LOOKAHEAD_DAYS)

    # Only include upcoming releases (today through cutoff)
    if release_date.date() < today.date() or release_date.date() > cutoff.date():
        return None

    retail_price = parse_price(
        raw.get("retailPrice") or raw.get("retail_price") or raw.get("retailprice")
    )
    estimated_market_value = parse_price(
        raw.get("estimatedMarketValue")
        or raw.get("estimated_market_value")
        or raw.get("marketValue")
        or raw.get("market_value")
    )

    name = (
        raw.get("name") or raw.get("title") or raw.get("shoeName") or "Unknown"
    ).strip()
    brand = (raw.get("brand") or raw.get("make") or "Unknown").strip()
    colorway = (raw.get("colorway") or raw.get("colour") or "N/A").strip()
    style_code = (
        raw.get("sku") or raw.get("styleId") or raw.get("style_id") or "N/A"
    ).strip()
    silhouette = (raw.get("silhouette") or raw.get("model") or "").strip()

    # Image can be a nested object {"original": url, "small": url, "thumbnail": url}
    # or a plain string
    image_raw = raw.get("image") or raw.get("thumbnail") or ""
    if isinstance(image_raw, dict):
        image_url = (
            image_raw.get("original") or image_raw.get("small") or image_raw.get("thumbnail") or ""
        )
    else:
        image_url = str(image_raw).strip()

    days_until = (release_date.date() - today.date()).days

    return {
        "name": name,
        "brand": brand,
        "silhouette": silhouette,
        "colorway": colorway,
        "style_code": style_code,
        "retail_price": retail_price,
        "estimated_market_value": estimated_market_value,
        "release_date": release_date,
        "days_until_release": days_until,
        "image_url": image_url,
    }


def deduplicate(sneakers: list[dict]) -> list[dict]:
    """Remove duplicates based on style_code (or name if style_code is N/A)."""
    seen = set()
    unique = []
    for s in sneakers:
        key = s["style_code"] if s["style_code"] != "N/A" else s["name"]
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


def main():
    log.info("=== Sneaker Release Tracker ===")
    log.info("Looking ahead %d days from today.", LOOKAHEAD_DAYS)

    api_key = get_api_key()
    all_sneakers = []

    for brand in TARGET_BRANDS:
        raw = fetch_sneakers_for_brand(brand, api_key)
        for item in raw:
            normalized = normalize_sneaker(item)
            if normalized:
                all_sneakers.append(normalized)

    log.info("Total sneakers after filtering: %d", len(all_sneakers))

    # Deduplicate
    all_sneakers = deduplicate(all_sneakers)
    log.info("After deduplication: %d", len(all_sneakers))

    # Calculate hype scores
    for sneaker in all_sneakers:
        score, level = calculate_hype_score(sneaker)
        sneaker["hype_score"] = score
        sneaker["hype_level"] = level

    # Sort by release date
    all_sneakers.sort(key=lambda s: s["release_date"])

    # Export to Excel
    export_to_excel(all_sneakers, OUTPUT_PATH)
    log.info("Report saved to %s", OUTPUT_PATH)
    log.info("Done.")


if __name__ == "__main__":
    main()
