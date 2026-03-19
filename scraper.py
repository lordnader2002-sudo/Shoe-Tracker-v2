#!/usr/bin/env python3
"""
Sneaker Release Tracker — Scrapes upcoming US sneaker releases from
multiple sneaker news sites and exports to Excel.

Sources (in priority order):
  1. SneakerFiles.com/release-dates/
  2. NiceKicks.com/sneaker-release-dates/
  3. SneakerBarDetroit.com/sneaker-release-dates/
"""

import os
import re
import sys
import logging
from datetime import datetime, timedelta, timezone, date

import requests
from bs4 import BeautifulSoup

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

LOOKAHEAD_DAYS = 30
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "reports", "sneaker_releases.xlsx")

TARGET_BRANDS = {"nike", "jordan", "air jordan", "adidas", "under armour",
                 "yeezy", "new balance"}

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ---------------------------------------------------------------------------
# Date / price parsing helpers
# ---------------------------------------------------------------------------

# Common date patterns found on sneaker sites
DATE_PATTERNS = [
    # "March 22, 2026" or "Mar 22, 2026"
    re.compile(
        r"(January|February|March|April|May|June|July|August|September|October|November|December"
        r"|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"\.?\s+(\d{1,2}),?\s+(\d{4})",
        re.IGNORECASE,
    ),
    # "03/22/2026" or "3/22/2026"
    re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})"),
    # "2026-03-22"
    re.compile(r"(\d{4})-(\d{2})-(\d{2})"),
]

PRICE_PATTERN = re.compile(r"\$\s?(\d{1,4}(?:,\d{3})*(?:\.\d{2})?)")

MONTH_MAP = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "october": 10, "oct": 10,
    "november": 11, "nov": 11, "december": 12, "dec": 12,
}


def parse_date_from_text(text: str) -> date | None:
    """Extract the first valid date from a text string."""
    if not text:
        return None

    # Pattern 1: "March 22, 2026"
    m = DATE_PATTERNS[0].search(text)
    if m:
        month_str, day_str, year_str = m.group(1), m.group(2), m.group(3)
        month = MONTH_MAP.get(month_str.lower().rstrip("."))
        if month:
            try:
                return date(int(year_str), month, int(day_str))
            except ValueError:
                pass

    # Pattern 2: "03/22/2026"
    m = DATE_PATTERNS[1].search(text)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        except ValueError:
            pass

    # Pattern 3: "2026-03-22"
    m = DATE_PATTERNS[2].search(text)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    return None


def parse_price_from_text(text: str) -> float | None:
    """Extract the first price (e.g. $170) from text."""
    if not text:
        return None
    m = PRICE_PATTERN.search(text)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return None
    return None


def detect_brand(text: str) -> str:
    """Detect the sneaker brand from the shoe name/text."""
    t = text.lower()
    if "jordan" in t or "air jordan" in t:
        return "Jordan"
    if "yeezy" in t:
        return "Yeezy"
    if "nike" in t or "dunk" in t or "air force" in t or "air max" in t:
        return "Nike"
    if "adidas" in t or "ultraboost" in t or "samba" in t:
        return "Adidas"
    if "new balance" in t:
        return "New Balance"
    if "under armour" in t or "ua " in t or "curry" in t:
        return "Under Armour"
    if "reebok" in t:
        return "Reebok"
    if "puma" in t:
        return "Puma"
    if "converse" in t:
        return "Converse"
    if "asics" in t:
        return "ASICS"
    return "Other"


def is_target_brand(brand: str) -> bool:
    """Check if a brand is one of our target brands."""
    return brand.lower() in TARGET_BRANDS


def fetch_html(url: str) -> str | None:
    """Fetch HTML from a URL with proper headers."""
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=20)
        if resp.status_code == 200:
            log.info("Fetched %s (%d bytes)", url, len(resp.text))
            return resp.text
        else:
            log.warning("HTTP %d from %s", resp.status_code, url)
            return None
    except requests.RequestException as exc:
        log.warning("Error fetching %s: %s", url, exc)
        return None


# ---------------------------------------------------------------------------
# Source 1: SneakerFiles.com
# ---------------------------------------------------------------------------

def scrape_sneakerfiles() -> list[dict]:
    """Scrape upcoming releases from SneakerFiles.com."""
    url = "https://www.sneakerfiles.com/release-dates/"
    html = fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    releases = []

    # SneakerFiles lists releases as article/post entries
    # Try multiple selectors for resilience
    articles = (
        soup.select("article") or
        soup.select(".post") or
        soup.select(".release-entry") or
        soup.select(".entry")
    )

    log.info("SneakerFiles: found %d article elements", len(articles))

    for article in articles:
        text = article.get_text(separator=" ", strip=True)
        title_el = article.select_one("h2 a, h3 a, .entry-title a, h2, h3")
        name = title_el.get_text(strip=True) if title_el else ""

        if not name:
            continue

        release_date = parse_date_from_text(text)
        price = parse_price_from_text(text)
        brand = detect_brand(name)

        if release_date and name:
            releases.append({
                "name": name,
                "brand": brand,
                "release_date": release_date,
                "retail_price": price,
                "colorway": "N/A",
                "style_code": "N/A",
                "source": "SneakerFiles",
            })

    # Also try to parse from plain text blocks / divs if articles didn't work
    if not releases:
        log.info("SneakerFiles: trying text-block parsing...")
        releases = _parse_release_blocks(soup, "SneakerFiles")

    log.info("SneakerFiles: extracted %d releases", len(releases))
    return releases


# ---------------------------------------------------------------------------
# Source 2: NiceKicks.com
# ---------------------------------------------------------------------------

def scrape_nicekicks() -> list[dict]:
    """Scrape upcoming releases from NiceKicks.com."""
    url = "https://www.nicekicks.com/sneaker-release-dates/"
    html = fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    releases = []

    # NiceKicks uses card-style layouts
    cards = (
        soup.select(".release-entry") or
        soup.select("article") or
        soup.select(".post-card") or
        soup.select(".sneaker-card") or
        soup.select(".card")
    )

    log.info("NiceKicks: found %d card elements", len(cards))

    for card in cards:
        text = card.get_text(separator=" ", strip=True)
        title_el = card.select_one("h2 a, h3 a, h4 a, .title a, h2, h3, h4")
        name = title_el.get_text(strip=True) if title_el else ""

        if not name:
            continue

        release_date = parse_date_from_text(text)
        price = parse_price_from_text(text)
        brand = detect_brand(name)

        if release_date and name:
            releases.append({
                "name": name,
                "brand": brand,
                "release_date": release_date,
                "retail_price": price,
                "colorway": "N/A",
                "style_code": "N/A",
                "source": "NiceKicks",
            })

    if not releases:
        log.info("NiceKicks: trying text-block parsing...")
        releases = _parse_release_blocks(soup, "NiceKicks")

    log.info("NiceKicks: extracted %d releases", len(releases))
    return releases


# ---------------------------------------------------------------------------
# Source 3: SneakerBarDetroit.com
# ---------------------------------------------------------------------------

def scrape_sneakerbardetroit() -> list[dict]:
    """Scrape upcoming releases from SneakerBarDetroit.com."""
    url = "https://sneakerbardetroit.com/sneaker-release-dates/"
    html = fetch_html(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    releases = []

    # SneakerBarDetroit lists releases in article/post format
    articles = (
        soup.select("article") or
        soup.select(".post") or
        soup.select(".release-post") or
        soup.select(".entry")
    )

    log.info("SneakerBarDetroit: found %d article elements", len(articles))

    for article in articles:
        text = article.get_text(separator=" ", strip=True)
        title_el = article.select_one("h2 a, h3 a, .entry-title a, h2, h3")
        name = title_el.get_text(strip=True) if title_el else ""

        if not name:
            continue

        release_date = parse_date_from_text(text)
        price = parse_price_from_text(text)
        brand = detect_brand(name)

        if release_date and name:
            releases.append({
                "name": name,
                "brand": brand,
                "release_date": release_date,
                "retail_price": price,
                "colorway": "N/A",
                "style_code": "N/A",
                "source": "SneakerBarDetroit",
            })

    if not releases:
        log.info("SneakerBarDetroit: trying text-block parsing...")
        releases = _parse_release_blocks(soup, "SneakerBarDetroit")

    log.info("SneakerBarDetroit: extracted %d releases", len(releases))
    return releases


# ---------------------------------------------------------------------------
# Fallback: generic text-block parser
# ---------------------------------------------------------------------------

def _parse_release_blocks(soup: BeautifulSoup, source: str) -> list[dict]:
    """
    Fallback parser that scans the entire page for sneaker release patterns.
    Looks for shoe names near dates and prices in text content.
    """
    releases = []
    body = soup.select_one("main, .content, #content, .site-content, body")
    if not body:
        body = soup

    # Get all text-containing elements
    elements = body.find_all(["div", "li", "p", "span", "td", "article", "section"])

    for el in elements:
        text = el.get_text(separator=" ", strip=True)
        if len(text) < 15 or len(text) > 500:
            continue

        release_date = parse_date_from_text(text)
        if not release_date:
            continue

        # Look for a shoe name — typically contains brand keywords
        has_brand_keyword = any(
            kw in text.lower()
            for kw in ["nike", "jordan", "adidas", "yeezy", "new balance",
                       "under armour", "dunk", "air force", "air max",
                       "air jordan", "retro", "boost"]
        )
        if not has_brand_keyword:
            continue

        # Try to extract the shoe name (first line or bolded text)
        name_el = el.find(["strong", "b", "a", "h2", "h3", "h4", "h5"])
        name = name_el.get_text(strip=True) if name_el else text[:80]

        # Clean up name — remove date and price from it
        name = DATE_PATTERNS[0].sub("", name).strip()
        name = PRICE_PATTERN.sub("", name).strip()
        name = name.rstrip(" -–—|,").strip()

        if len(name) < 5:
            continue

        price = parse_price_from_text(text)
        brand = detect_brand(name)

        releases.append({
            "name": name,
            "brand": brand,
            "release_date": release_date,
            "retail_price": price,
            "colorway": "N/A",
            "style_code": "N/A",
            "source": source,
        })

    return releases


# ---------------------------------------------------------------------------
# Enrichment: extract colorway / style code from name
# ---------------------------------------------------------------------------

STYLE_CODE_PATTERN = re.compile(r"\b([A-Z]{1,3}\d{3,5}[-–]\d{2,4})\b")
COLORWAY_SEPARATORS = re.compile(r"['\"]([^'\"]+)['\"]")


def enrich_sneaker(sneaker: dict) -> dict:
    """Try to extract colorway and style code from the shoe name."""
    name = sneaker["name"]

    # Style code (e.g., "DV0833-108")
    m = STYLE_CODE_PATTERN.search(name)
    if m and sneaker["style_code"] == "N/A":
        sneaker["style_code"] = m.group(1)

    # Colorway in quotes (e.g., Air Jordan 1 "Bred")
    m = COLORWAY_SEPARATORS.search(name)
    if m and sneaker["colorway"] == "N/A":
        sneaker["colorway"] = m.group(1)

    return sneaker


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def deduplicate(sneakers: list[dict]) -> list[dict]:
    """Remove duplicates based on name similarity."""
    seen = set()
    unique = []
    for s in sneakers:
        # Normalize key: lowercase name, remove special chars
        key = re.sub(r"[^a-z0-9]", "", s["name"].lower())
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique


def main():
    log.info("=== Sneaker Release Tracker ===")

    today = date.today()
    cutoff = today + timedelta(days=LOOKAHEAD_DAYS)
    log.info("Date range: %s to %s (%d days)", today, cutoff, LOOKAHEAD_DAYS)

    # Scrape from multiple sources
    all_releases = []

    sources = [
        ("SneakerFiles", scrape_sneakerfiles),
        ("NiceKicks", scrape_nicekicks),
        ("SneakerBarDetroit", scrape_sneakerbardetroit),
    ]

    for name, scraper_fn in sources:
        log.info("--- Scraping %s ---", name)
        try:
            releases = scraper_fn()
            all_releases.extend(releases)
        except Exception as exc:
            log.error("Error scraping %s: %s", name, exc)

    log.info("Total raw releases from all sources: %d", len(all_releases))

    # Filter to target brands and upcoming date range
    filtered = []
    for r in all_releases:
        if not is_target_brand(r["brand"]):
            log.debug("Skipping non-target brand: %s (%s)", r["name"], r["brand"])
            continue
        rd = r["release_date"]
        if rd < today or rd > cutoff:
            continue
        # Enrich with colorway/style code parsing
        r = enrich_sneaker(r)
        r["days_until_release"] = (rd - today).days
        # Convert date to datetime for Excel export compatibility
        r["release_date"] = datetime.combine(rd, datetime.min.time())
        r["estimated_market_value"] = None
        r["silhouette"] = ""
        r["image_url"] = ""
        filtered.append(r)

    log.info("After brand + date filtering: %d", len(filtered))

    # Deduplicate (same shoe from multiple sources)
    filtered = deduplicate(filtered)
    log.info("After deduplication: %d", len(filtered))

    # Calculate hype scores
    for sneaker in filtered:
        score, level = calculate_hype_score(sneaker)
        sneaker["hype_score"] = score
        sneaker["hype_level"] = level

    # Sort by release date
    filtered.sort(key=lambda s: s["release_date"])

    # Log what we found
    for s in filtered[:20]:
        log.info(
            "  %s | %-8s | %s | $%s | Hype: %d (%s)",
            s["release_date"].strftime("%Y-%m-%d"),
            s["brand"],
            s["name"][:50],
            s["retail_price"] or "TBD",
            s["hype_score"],
            s["hype_level"],
        )

    # Export to Excel
    export_to_excel(filtered, OUTPUT_PATH)
    log.info("Report saved to %s", OUTPUT_PATH)
    log.info("Done. %d releases tracked.", len(filtered))


if __name__ == "__main__":
    main()
