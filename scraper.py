"""
Sneaker Release Scraper
Targets: SneakerNews, KicksOnFire, SoleCollector
"""

import re
import os
import json
import time
import hashlib
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from hype import calculate_hype_level, HYPE_LABELS

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s: %(message)s")
logger = logging.getLogger(__name__)

DATA_FILE = "data/releases.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _uid(name: str, release_date: str) -> str:
    key = f"{name.lower().strip()}{release_date}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def detect_brand(name: str) -> str:
    n = (name or "").lower()
    if "air jordan" in n or re.search(r"\bjordan\b", n):
        return "Jordan"
    if "yeezy" in n:
        return "Adidas (Yeezy)"
    if "nike" in n or "air max" in n or "air force" in n or "dunk" in n or "blazer" in n:
        return "Nike"
    if "adidas" in n or "ultraboost" in n or "nmd" in n or "samba" in n or "gazelle" in n:
        return "Adidas"
    if "new balance" in n or re.search(r"\bnb\b", n):
        return "New Balance"
    if "puma" in n:
        return "Puma"
    if "under armour" in n or re.search(r"\bua\b", n):
        return "Under Armour"
    if "converse" in n or "chuck" in n:
        return "Converse"
    if "vans" in n or "old skool" in n or "sk8" in n:
        return "Vans"
    if "reebok" in n:
        return "Reebok"
    if "asics" in n or "gel-" in n:
        return "ASICS"
    if "saucony" in n:
        return "Saucony"
    return "Other"


def detect_sale_methods(text: str) -> list:
    t = (text or "").lower()
    methods = []
    if "snkrs" in t:
        methods.append("SNKRS App")
    if "confirmed app" in t or "adidas confirmed" in t:
        methods.append("Confirmed App")
    if "raffle" in t:
        methods.append("Raffle")
    if re.search(r"\bdraw\b", t):
        methods.append("Draw")
    if "in-store" in t or "in store" in t or "retail store" in t:
        methods.append("In-Store")
    if "online" in t or "website" in t or ".com" in t:
        methods.append("Online")
    if "foot locker" in t or "footlocker" in t:
        methods.append("Foot Locker")
    if "finish line" in t or "finishline" in t:
        methods.append("Finish Line")
    if "champs" in t:
        methods.append("Champs Sports")
    if "jd sports" in t:
        methods.append("JD Sports")
    if "end clothing" in t or "end launches" in t:
        methods.append("END Clothing")
    if "stockx" in t:
        methods.append("StockX (Resale)")
    if re.search(r"\bgoat\b", t):
        methods.append("GOAT (Resale)")
    if not methods:
        methods = ["Online", "In-Store"]
    return list(dict.fromkeys(methods))   # preserve order, deduplicate


def extract_price(text: str):
    patterns = [
        r"\$\s*(\d{2,4}(?:\.\d{2})?)",
        r"(\d{2,4}(?:\.\d{2})?)\s*usd",
        r"retail[:\s]+\$?(\d{2,4})",
        r"price[:\s]+\$?(\d{2,4})",
        r"msrp[:\s]+\$?(\d{2,4})",
    ]
    for pat in patterns:
        m = re.search(pat, (text or ""), re.IGNORECASE)
        if m:
            try:
                price = float(m.group(1))
                if 40 <= price <= 5000:
                    return price
            except ValueError:
                pass
    return None


def _parse_date(text: str, element=None):
    if element:
        time_tag = element.find("time")
        if time_tag:
            dt_attr = time_tag.get("datetime", "")
            if dt_attr:
                try:
                    return dateparser.parse(dt_attr).strftime("%Y-%m-%d")
                except Exception:
                    pass

    patterns = [
        r"(\w+ \d{1,2},?\s*\d{4})",
        r"(\d{1,2}/\d{1,2}/\d{4})",
        r"(\d{4}-\d{2}-\d{2})",
        r"(\w+ \d{1,2}(?:,\s*\d{4})?)",
    ]
    for pat in patterns:
        m = re.search(pat, text or "")
        if m:
            try:
                d = dateparser.parse(m.group(1))
                if d:
                    return d.strftime("%Y-%m-%d")
            except Exception:
                pass
    return "TBD"


def _best_img(tag) -> str:
    if not tag:
        return ""
    for attr in ("data-lazy-src", "data-src", "data-original", "src"):
        val = tag.get(attr, "")
        if val and val.startswith("http") and not val.endswith(".gif"):
            return val
    return ""


# ---------------------------------------------------------------------------
# Base scraper
# ---------------------------------------------------------------------------

class BaseScraper:
    SOURCE  = "Unknown"
    BASE_URL = ""
    RELEASE_URL = ""

    def _get(self, url):
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, "lxml")

    def _build_release(self, name, source_url, image_url, release_date, full_text):
        brand   = detect_brand(name)
        price   = extract_price(full_text)
        methods = detect_sale_methods(full_text)
        hype    = calculate_hype_level(name, brand, price, methods)

        if source_url and not source_url.startswith("http"):
            source_url = self.BASE_URL + source_url

        return {
            "id":           _uid(name, str(release_date)),
            "name":         name,
            "brand":        brand,
            "release_date": release_date,
            "price":        price,
            "sale_methods": methods,
            "image_url":    image_url or "",
            "source_url":   source_url or self.RELEASE_URL,
            "source":       self.SOURCE,
            "hype_level":   hype,
            "hype_label":   HYPE_LABELS.get(hype, "Unknown"),
        }

    def scrape(self) -> list:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# SneakerNews scraper
# ---------------------------------------------------------------------------

class SneakerNewsScraper(BaseScraper):
    SOURCE      = "SneakerNews"
    BASE_URL    = "https://sneakernews.com"
    RELEASE_URL = "https://sneakernews.com/release-dates/"

    def scrape(self) -> list:
        releases = []
        try:
            logger.info("Scraping SneakerNews …")
            soup = self._get(self.RELEASE_URL)

            # Primary: article elements
            articles = soup.find_all("article")
            if not articles:
                articles = soup.find_all("div", class_=re.compile(r"post|release|card"))

            logger.info("  SneakerNews: %d articles found", len(articles))
            for art in articles[:40]:
                try:
                    r = self._parse(art)
                    if r:
                        releases.append(r)
                except Exception as e:
                    logger.debug("  SN parse error: %s", e)
        except Exception as e:
            logger.error("SneakerNews scrape failed: %s", e)
        return releases

    def _parse(self, article):
        title = article.find(["h2", "h3", "h4"])
        if not title:
            return None
        name = title.get_text(" ", strip=True)
        if len(name) < 6:
            return None

        link = article.find("a", href=True)
        source_url = link["href"] if link else self.RELEASE_URL

        img_tag = article.find("img")
        image_url = _best_img(img_tag)

        full_text = article.get_text(" ", strip=True)
        release_date = _parse_date(full_text, article)

        return self._build_release(name, source_url, image_url, release_date, full_text)


# ---------------------------------------------------------------------------
# KicksOnFire scraper
# ---------------------------------------------------------------------------

class KicksOnFireScraper(BaseScraper):
    SOURCE      = "KicksOnFire"
    BASE_URL    = "https://www.kicksonfire.com"
    RELEASE_URL = "https://www.kicksonfire.com/release-dates/"

    def scrape(self) -> list:
        releases = []
        try:
            logger.info("Scraping KicksOnFire …")
            soup = self._get(self.RELEASE_URL)

            entries = soup.find_all(["article", "div"],
                                    class_=re.compile(r"sneak|shoe|release|post|item|card"))
            if not entries:
                entries = soup.find_all("article")

            logger.info("  KicksOnFire: %d entries found", len(entries))
            for entry in entries[:40]:
                try:
                    r = self._parse(entry)
                    if r:
                        releases.append(r)
                except Exception as e:
                    logger.debug("  KOF parse error: %s", e)
        except Exception as e:
            logger.error("KicksOnFire scrape failed: %s", e)
        return releases

    def _parse(self, entry):
        title = entry.find(["h2", "h3", "h4", "h5"])
        if not title:
            return None
        name = title.get_text(" ", strip=True)
        if len(name) < 6:
            return None

        link = entry.find("a", href=True)
        source_url = link["href"] if link else self.RELEASE_URL

        img_tag = entry.find("img")
        image_url = _best_img(img_tag)

        full_text = entry.get_text(" ", strip=True)
        release_date = _parse_date(full_text, entry)

        return self._build_release(name, source_url, image_url, release_date, full_text)


# ---------------------------------------------------------------------------
# SoleCollector scraper
# ---------------------------------------------------------------------------

class SoleCollectorScraper(BaseScraper):
    SOURCE      = "SoleCollector"
    BASE_URL    = "https://solecollector.com"
    RELEASE_URL = "https://solecollector.com/release-date-calendar"

    def scrape(self) -> list:
        releases = []
        try:
            logger.info("Scraping SoleCollector …")
            soup = self._get(self.RELEASE_URL)

            entries = soup.find_all(["article", "div"],
                                    class_=re.compile(r"release|shoe|sneaker|card|item|post"))
            if not entries:
                entries = soup.find_all("article")

            logger.info("  SoleCollector: %d entries found", len(entries))
            for entry in entries[:40]:
                try:
                    r = self._parse(entry)
                    if r:
                        releases.append(r)
                except Exception as e:
                    logger.debug("  SC parse error: %s", e)
        except Exception as e:
            logger.error("SoleCollector scrape failed: %s", e)
        return releases

    def _parse(self, entry):
        title = entry.find(["h2", "h3", "h4"])
        if not title:
            return None
        name = title.get_text(" ", strip=True)
        if len(name) < 6:
            return None

        link = entry.find("a", href=True)
        source_url = link["href"] if link else self.RELEASE_URL

        img_tag = entry.find("img")
        image_url = _best_img(img_tag)

        full_text = entry.get_text(" ", strip=True)
        release_date = _parse_date(full_text, entry)

        return self._build_release(name, source_url, image_url, release_date, full_text)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def scrape_all() -> list:
    """Run all scrapers, deduplicate, and return merged list."""
    scrapers = [
        SneakerNewsScraper(),
        KicksOnFireScraper(),
        SoleCollectorScraper(),
    ]

    all_releases = []
    seen_ids = set()

    for scraper in scrapers:
        try:
            results = scraper.scrape()
            for r in results:
                if r["id"] not in seen_ids:
                    seen_ids.add(r["id"])
                    r["scraped_at"] = datetime.now().isoformat()
                    all_releases.append(r)
            logger.info("  → %d unique so far after %s", len(all_releases), scraper.SOURCE)
        except Exception as e:
            logger.error("Scraper %s failed: %s", scraper.SOURCE, e)
        time.sleep(1.5)   # be polite

    # Sort upcoming first, then TBD at the end
    def sort_key(r):
        d = r.get("release_date", "TBD")
        return "9999-99-99" if d == "TBD" else d

    all_releases.sort(key=sort_key)
    return all_releases


def save_releases(releases: list, filepath: str = DATA_FILE):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    payload = {
        "releases":     releases,
        "last_updated": datetime.now().isoformat(),
        "count":        len(releases),
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    logger.info("Saved %d releases → %s", len(releases), filepath)


def load_releases(filepath: str = DATA_FILE) -> dict:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"releases": [], "last_updated": None, "count": 0}


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    releases = scrape_all()
    save_releases(releases)
    print(f"Done – {len(releases)} releases saved to {DATA_FILE}")
