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


def _fetch_page(url: str, headers: dict, params: dict, brand: str, page: int) -> dict | None:
    """Fetch a single page from the API. Returns parsed JSON or None on failure."""
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
    except requests.RequestException as exc:
        log.warning("Network error fetching %s page %d: %s", brand, page, exc)
        return None

    if resp.status_code == 429:
        log.warning("Rate limited on %s — stopping.", brand)
        return None
    if resp.status_code in (401, 403):
        log.error("API auth error (%d). Check your RAPIDAPI_KEY.", resp.status_code)
        sys.exit(1)
    if resp.status_code != 200:
        body_preview = resp.text[:500] if resp.text else "(empty)"
        log.warning("HTTP %d for %s page %d. Response: %s", resp.status_code, brand, page, body_preview)
        return None

    return resp.json()


def fetch_sneakers_for_brand(brand: str, api_key: str) -> list[dict]:
    """
    Fetch sneakers for a single brand from The Sneaker Database API.
    Tries multiple releaseYear values to find upcoming releases.
    Returns a list of raw sneaker dicts from the API response.
    """
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": API_HOST,
    }

    today = datetime.now(timezone.utc).date()
    current_year = today.year
    url = f"{API_BASE}/sneakers"

    all_sneakers = []

    # Try current year, previous year (for late releases), and next year
    # The API may label releases by their announcement year, not release year
    years_to_try = [str(current_year), str(current_year - 1)]
    if today.month >= 10:
        years_to_try.append(str(current_year + 1))

    found_with_year_filter = False

    for year in years_to_try:
        params = {
            "brand": brand,
            "limit": str(RESULTS_PER_PAGE),
            "page": "1",
            "releaseYear": year,
        }

        log.info("Fetching %s releaseYear=%s page 1 ...", brand, year)
        data = _fetch_page(url, headers, params, brand, 1)

        if data is None:
            continue

        if isinstance(data, dict):
            count = data.get("count", 0)
            log.info("%s releaseYear=%s: %s results available", brand, year, count)
            if count and count > 0:
                found_with_year_filter = True
                results = data.get("results", [])
                if results:
                    # Log samples
                    for i, s in enumerate(results[:3]):
                        log.info(
                            "  Sample[%d]: name=%s, releaseDate=%s, retailPrice=%s",
                            i, s.get("name", "?")[:60], s.get("releaseDate", "?"), s.get("retailPrice", "?"),
                        )
                    all_sneakers.extend(results)

                    # Paginate if there are more
                    total_pages = data.get("totalPages", 1)
                    page = 2
                    while page <= min(total_pages, 5):
                        params["page"] = str(page)
                        log.info("Fetching %s releaseYear=%s page %d ...", brand, year, page)
                        pdata = _fetch_page(url, headers, params, brand, page)
                        if pdata is None:
                            break
                        presults = pdata if isinstance(pdata, list) else pdata.get("results", [])
                        if not presults:
                            break
                        all_sneakers.extend(presults)
                        if len(presults) < RESULTS_PER_PAGE:
                            break
                        page += 1
                        time.sleep(0.3)

        time.sleep(0.3)

    # Fallback: if year filter returned nothing, fetch without it
    if not found_with_year_filter:
        log.info("No results with releaseYear filter for %s. Fetching without filter...", brand)
        for page in range(1, 6):
            params = {
                "brand": brand,
                "limit": str(RESULTS_PER_PAGE),
                "page": str(page),
            }
            log.info("Fetching %s (no year filter) page %d ...", brand, page)
            data = _fetch_page(url, headers, params, brand, page)
            if data is None:
                break

            results = data if isinstance(data, list) else data.get("results", [])

            if page == 1 and results:
                for i, s in enumerate(results[:5]):
                    log.info(
                        "  Sample[%d]: name=%s, releaseDate=%s, retailPrice=%s",
                        i, s.get("name", "?")[:60], s.get("releaseDate", "?"), s.get("retailPrice", "?"),
                    )

            if not results:
                break
            all_sneakers.extend(results)
            if len(results) < RESULTS_PER_PAGE:
                break
            time.sleep(0.3)

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
