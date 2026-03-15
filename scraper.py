"""
Sneaker Release Scraper — US-focused
Sources: SneakerNews, KicksOnFire, SoleCollector, SneakerBarDetroit, NiceKicks

Date window: today → today + 30 days (releases outside this range are discarded).
Prices: scraped from page text; fallback to known-price table in hype.py.
"""

import re
import os
import json
import time
import hashlib
import logging
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from hype import calculate_hype_level, lookup_known_price, HYPE_LABELS

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s: %(message)s")
logger = logging.getLogger(__name__)

DATA_FILE = "data/releases.json"

# Date window: collect releases from today through 30 days out
_TODAY     = datetime.now().date()
_WIN_START = _TODAY
_WIN_END   = _TODAY + timedelta(days=30)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _uid(name: str, release_date: str) -> str:
    key = f"{name.lower().strip()}{release_date}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def _in_window(date_str: str) -> bool:
    """Return True if date_str (YYYY-MM-DD) falls within [today, today+30]."""
    if not date_str or date_str == "TBD":
        return True  # keep TBD — we don't know when it'll drop
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return _WIN_START <= d <= _WIN_END
    except ValueError:
        return False


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
    if "online" in t or "website" in t:
        methods.append("Online")
    if "foot locker" in t or "footlocker" in t:
        methods.append("Foot Locker")
    if "finish line" in t or "finishline" in t:
        methods.append("Finish Line")
    if "champs" in t:
        methods.append("Champs Sports")
    if "jd sports" in t:
        methods.append("JD Sports")
    if "stockx" in t:
        methods.append("StockX (Resale)")
    if re.search(r"\bgoat\b", t):
        methods.append("GOAT (Resale)")
    if not methods:
        methods = ["Online", "In-Store"]
    return list(dict.fromkeys(methods))


def extract_price(text: str, name: str = ""):
    """
    Extract retail price from article text.
    Priority:
      1. Explicit retail/MSRP/price label patterns
      2. First bare $NNN pattern in a reasonable range
      3. Known-price lookup by shoe name
    """
    t = text or ""

    # Priority 1 – labelled patterns (most reliable)
    labelled = [
        r"retail(?:\s+price)?[:\s]+\$?\s*(\d{2,4}(?:\.\d{2})?)",
        r"msrp[:\s]+\$?\s*(\d{2,4}(?:\.\d{2})?)",
        r"retails?\s+for\s+\$?\s*(\d{2,4}(?:\.\d{2})?)",
        r"price(?:d)?[:\s]+\$?\s*(\d{2,4}(?:\.\d{2})?)",
        r"will sell\s+for\s+\$?\s*(\d{2,4}(?:\.\d{2})?)",
        r"set at\s+\$?\s*(\d{2,4}(?:\.\d{2})?)",
        r"listed at\s+\$?\s*(\d{2,4}(?:\.\d{2})?)",
    ]
    for pat in labelled:
        m = re.search(pat, t, re.IGNORECASE)
        if m:
            try:
                p = float(m.group(1))
                if 40 <= p <= 2000:
                    return p
            except ValueError:
                pass

    # Priority 2 – any $NNN (restrict to plausible sneaker range)
    for m in re.finditer(r"\$\s*(\d{2,4}(?:\.\d{2})?)", t):
        try:
            p = float(m.group(1))
            if 50 <= p <= 800:
                return p
        except ValueError:
            pass

    # Priority 3 – known-price fallback
    return lookup_known_price(name)


def _parse_date(text: str, element=None, url: str = ""):
    """
    Extract the release date. Strategy (most-to-least reliable):
      1. <time datetime="…"> attribute on the element
      2. Structured "Release Date: Month DD, YYYY" text pattern
      3. Date in the page URL (year/month signals article freshness, not release date)
      4. First full "Month DD, YYYY" pattern in the text
    Only returns dates within ±2 years of today; otherwise returns "TBD".
    """
    today_year = datetime.now().year

    def _validate(d):
        """Accept dates within [today_year - 1 .. today_year + 2]."""
        if d and (today_year - 1) <= d.year <= (today_year + 2):
            return d.strftime("%Y-%m-%d")
        return None

    # 1. <time datetime> attribute
    if element:
        for tag in element.find_all("time"):
            dt_attr = tag.get("datetime", "")
            if dt_attr:
                try:
                    r = _validate(dateparser.parse(dt_attr))
                    if r:
                        return r
                except Exception:
                    pass

    # 2. Explicit "release date" label in text
    labelled = re.search(
        r"release\s+date[:\s]+([A-Za-z]+ \d{1,2},?\s*\d{4}|\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2})",
        text or "", re.IGNORECASE,
    )
    if labelled:
        try:
            r = _validate(dateparser.parse(labelled.group(1)))
            if r:
                return r
        except Exception:
            pass

    # 3. "Month DD, YYYY" full date anywhere in text
    for m in re.finditer(r"([A-Z][a-z]+ \d{1,2},\s*\d{4})", text or ""):
        try:
            r = _validate(dateparser.parse(m.group(1)))
            if r:
                return r
        except Exception:
            pass

    # 4. ISO date in text
    for m in re.finditer(r"(\d{4}-\d{2}-\d{2})", text or ""):
        try:
            r = _validate(dateparser.parse(m.group(1)))
            if r:
                return r
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
    SOURCE      = "Unknown"
    BASE_URL    = ""
    RELEASE_URL = ""

    def _get(self, url):
        resp = requests.get(url, headers=HEADERS, timeout=25)
        resp.raise_for_status()
        return BeautifulSoup(resp.content, "lxml")

    def _build_release(self, name, source_url, image_url, release_date, full_text):
        brand   = detect_brand(name)
        price   = extract_price(full_text, name)
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
# SneakerNews
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
            articles = soup.find_all("article") or \
                       soup.find_all("div", class_=re.compile(r"post|release|card"))
            logger.info("  SneakerNews: %d articles found", len(articles))
            for art in articles[:60]:
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

        img_tag   = article.find("img")
        image_url = _best_img(img_tag)
        full_text = article.get_text(" ", strip=True)
        release_date = _parse_date(full_text, article, source_url)

        return self._build_release(name, source_url, image_url, release_date, full_text)


# ---------------------------------------------------------------------------
# KicksOnFire
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
            for entry in entries[:60]:
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

        link      = entry.find("a", href=True)
        source_url = link["href"] if link else self.RELEASE_URL
        img_tag   = entry.find("img")
        image_url = _best_img(img_tag)
        full_text = entry.get_text(" ", strip=True)
        release_date = _parse_date(full_text, entry, source_url)

        return self._build_release(name, source_url, image_url, release_date, full_text)


# ---------------------------------------------------------------------------
# SoleCollector
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
            for entry in entries[:60]:
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

        link      = entry.find("a", href=True)
        source_url = link["href"] if link else self.RELEASE_URL
        img_tag   = entry.find("img")
        image_url = _best_img(img_tag)
        full_text = entry.get_text(" ", strip=True)
        release_date = _parse_date(full_text, entry, source_url)

        return self._build_release(name, source_url, image_url, release_date, full_text)


# ---------------------------------------------------------------------------
# SneakerBarDetroit  (US-based, comprehensive calendar)
# ---------------------------------------------------------------------------

class SneakerBarDetroitScraper(BaseScraper):
    SOURCE      = "SneakerBarDetroit"
    BASE_URL    = "https://sneakerbardetroit.com"
    RELEASE_URL = "https://sneakerbardetroit.com/sneaker-release-dates/"

    def scrape(self) -> list:
        releases = []
        try:
            logger.info("Scraping SneakerBarDetroit …")
            soup = self._get(self.RELEASE_URL)

            # SBD uses a specific class for release-date list items
            entries = (
                soup.find_all("div", class_=re.compile(r"release|shoe|sneaker|product|post"))
                or soup.find_all("article")
                or soup.find_all("li", class_=re.compile(r"release|shoe"))
            )
            logger.info("  SneakerBarDetroit: %d entries found", len(entries))
            for entry in entries[:60]:
                try:
                    r = self._parse(entry)
                    if r:
                        releases.append(r)
                except Exception as e:
                    logger.debug("  SBD parse error: %s", e)
        except Exception as e:
            logger.error("SneakerBarDetroit scrape failed: %s", e)
        return releases

    def _parse(self, entry):
        title = entry.find(["h2", "h3", "h4", "h5", "a"])
        if not title:
            return None
        name = title.get_text(" ", strip=True)
        if len(name) < 6:
            return None

        link      = entry.find("a", href=True)
        source_url = link["href"] if link else self.RELEASE_URL
        if source_url and not source_url.startswith("http"):
            source_url = self.BASE_URL + source_url
        img_tag   = entry.find("img")
        image_url = _best_img(img_tag)
        full_text = entry.get_text(" ", strip=True)
        release_date = _parse_date(full_text, entry, source_url)

        return self._build_release(name, source_url, image_url, release_date, full_text)


# ---------------------------------------------------------------------------
# NiceKicks  (US-based, editorial + release calendar)
# ---------------------------------------------------------------------------

class NiceKicksScraper(BaseScraper):
    SOURCE      = "NiceKicks"
    BASE_URL    = "https://www.nicekicks.com"
    RELEASE_URL = "https://www.nicekicks.com/release-dates/"

    def scrape(self) -> list:
        releases = []
        try:
            logger.info("Scraping NiceKicks …")
            soup = self._get(self.RELEASE_URL)

            entries = (
                soup.find_all("article")
                or soup.find_all("div", class_=re.compile(r"release|sneaker|card|post|item"))
            )
            logger.info("  NiceKicks: %d entries found", len(entries))
            for entry in entries[:60]:
                try:
                    r = self._parse(entry)
                    if r:
                        releases.append(r)
                except Exception as e:
                    logger.debug("  NK parse error: %s", e)
        except Exception as e:
            logger.error("NiceKicks scrape failed: %s", e)
        return releases

    def _parse(self, entry):
        title = entry.find(["h2", "h3", "h4", "h5"])
        if not title:
            return None
        name = title.get_text(" ", strip=True)
        if len(name) < 6:
            return None

        link      = entry.find("a", href=True)
        source_url = link["href"] if link else self.RELEASE_URL
        if source_url and not source_url.startswith("http"):
            source_url = self.BASE_URL + source_url
        img_tag   = entry.find("img")
        image_url = _best_img(img_tag)
        full_text = entry.get_text(" ", strip=True)
        release_date = _parse_date(full_text, entry, source_url)

        return self._build_release(name, source_url, image_url, release_date, full_text)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def scrape_all() -> list:
    """Run all scrapers, apply 30-day window filter, deduplicate, and return."""
    scrapers = [
        SneakerNewsScraper(),
        KicksOnFireScraper(),
        SoleCollectorScraper(),
        SneakerBarDetroitScraper(),
        NiceKicksScraper(),
    ]

    all_releases = []
    seen_ids     = set()
    window_start = _WIN_START.isoformat()
    window_end   = _WIN_END.isoformat()

    logger.info("Date window: %s → %s", window_start, window_end)

    for scraper in scrapers:
        try:
            results = scraper.scrape()
            kept = 0
            for r in results:
                if r["id"] in seen_ids:
                    continue
                # Apply date window filter (TBD dates pass through)
                if not _in_window(r.get("release_date", "TBD")):
                    logger.debug("  Filtered out (date outside window): %s – %s",
                                 r.get("release_date"), r.get("name"))
                    continue
                seen_ids.add(r["id"])
                r["scraped_at"] = datetime.now().isoformat()
                all_releases.append(r)
                kept += 1
            logger.info("  → kept %d / returned %d from %s (%d unique total)",
                        kept, len(results), scraper.SOURCE, len(all_releases))
        except Exception as e:
            logger.error("Scraper %s failed: %s", scraper.SOURCE, e)
        time.sleep(1.5)

    # Sort: soonest first, TBD at end
    def _sort_key(r):
        d = r.get("release_date", "TBD")
        return "9999-99-99" if (not d or d == "TBD") else d

    all_releases.sort(key=_sort_key)
    return all_releases


def save_releases(releases: list, filepath: str = DATA_FILE):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    payload = {
        "releases":     releases,
        "last_updated": datetime.now().isoformat(),
        "count":        len(releases),
        "window_start": _WIN_START.isoformat(),
        "window_end":   _WIN_END.isoformat(),
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    logger.info("Saved %d releases → %s", len(releases), filepath)


def load_releases(filepath: str = DATA_FILE) -> dict:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"releases": [], "last_updated": None, "count": 0}


if __name__ == "__main__":
    releases = scrape_all()
    save_releases(releases)
    print(f"\nDone – {len(releases)} releases saved to {DATA_FILE}")
    print(f"Window: {_WIN_START} → {_WIN_END}")
