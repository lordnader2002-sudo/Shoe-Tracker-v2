"""
Hype Level Calculator for Sneaker Releases

Scale (1-5):
  1 - General Release  : Widely available. No rush needed.
  2 - Popular          : High demand, may sell out but restocks occur.
  3 - Hyped            : Sells out in minutes. Bots prevalent. Limited restocks.
  4 - Limited          : Raffle/draw required. Very low stock. Big resale premium.
  5 - Grail            : Extreme rarity. Major collab or iconic colorway. Instant global sellout.
"""

import re

# ---------------------------------------------------------------------------
# Keyword tables
# ---------------------------------------------------------------------------

GRAIL_KEYWORDS = [
    "off-white", "off white", "travis scott", "cactus jack", "cactus plant",
    "cpfm", "fragment", "union la", "sacai", "fear of god", "fog x",
    "dior x", "virgil abloh", "patta x", "j balvin", "eminem",
    "ben & jerry", "ben and jerry", "mschf", "concepts x", "kith x",
    "atmos x", "a-cold-wall", "comme des garcons", "cdg x", "undercover x",
    "mastermind", "supreme x", "palace x", "stussy x", "grateful dead",
    "wu-tang", "pharrell x", "kanye", "drake x", "kendrick x",
    "dover street market", "dsm x", "j. cole x", "billie eilish x",
    "serena williams x", "lv x", "louis vuitton", "gucci x", "denim tears",
    "nocta x", "ambush x", "clot x", "bape x", "medicom",
    "sean wotherspoon", "bodega x", "aime leon dore x",
]

LIMITED_KEYWORDS = [
    "limited", "exclusive", "special edition", "friends and family",
    "friends & family", "player exclusive", "fnf",
    "collab", "collaboration", "art basel", "lottery",
    "invite only", "members only", "reserve", "prm", "premium",
]

HYPED_KEYWORDS = [
    "retro og", "retro high og", "'bred'", "bred toe",
    "chicago", "royal", "banned", "shadow", "university blue",
    "obsidian", "shattered backboard", "fire red", "sport blue",
    "french blue", "navy", "cement", "elephant", "infrared",
    "pine green", "court purple", "mocha",
    "ultraboost", "nmd r1", "yeezy boost", "yeezy 350", "yeezy 700",
    "yeezy slide", "yeezy foam",
    "dunk low", "dunk high", "sb dunk", "air force 1 sp",
    "samba og", "spezial", "gazelle indoor",
    "990v3", "990v4", "990v5", "new balance 992", "new balance 993", "2002r",
    "air max 1 sp", "air max 90 sp",
    "anniversary red", "anniversary blue", "lost & found", "lost and found",
]

BRAND_BASE_HYPE = {
    "jordan":         4,
    "air jordan":     4,
    "adidas (yeezy)": 4,
    "yeezy":          4,
    "nike":           3,
    "adidas":         3,
    "new balance":    2,
    "converse":       2,
    "puma":           2,
    "vans":           2,
    "reebok":         2,
    "asics":          2,
    "saucony":        2,
    "under armour":   1,
}

# ---------------------------------------------------------------------------
# Known retail prices (longest matching substring wins)
# Used as fallback when price cannot be scraped from article text
# ---------------------------------------------------------------------------

KNOWN_PRICES = [
    # Jordan
    ("air jordan 1 retro high og",  180),
    ("air jordan 1 retro low og",   130),
    ("air jordan 1 mid",            115),
    ("air jordan 1 low",            100),
    ("air jordan 2",                175),
    ("air jordan 3",                200),
    ("air jordan 4",                210),
    ("air jordan 5",                200),
    ("air jordan 6",                200),
    ("air jordan 11",               220),
    ("air jordan 12",               190),
    ("air jordan 13",               190),
    ("air jordan 14",               190),
    ("jordan 4",                    210),
    ("jordan 11",                   220),
    # Nike
    ("nike dunk low",               110),
    ("nike dunk high",              120),
    ("nike sb dunk low",            110),
    ("nike sb dunk high",           120),
    ("nike air force 1 low",        100),
    ("nike air force 1 high",       110),
    ("air force 1 sp",              130),
    ("nike air max 1",              110),
    ("air max 1 sp",                150),
    ("nike air max 90",             110),
    ("nike air max 95",             160),
    ("nike air max 97",             175),
    ("nike air max 270",            150),
    ("nike air max plus",           160),
    ("nike air vapormax",           190),
    ("nike air presto",             130),
    ("nike blazer mid",             100),
    ("nike cortez",                  85),
    ("nike pegasus",                130),
    # Adidas / Yeezy
    ("yeezy boost 350 v2",          230),
    ("yeezy boost 700",             300),
    ("yeezy 700 v3",                270),
    ("yeezy foam runner",            80),
    ("yeezy foam rnnr",              80),
    ("yeezy slide",                  70),
    ("yeezy 500",                   200),
    ("adidas samba og",             100),
    ("adidas samba",                100),
    ("adidas gazelle",              100),
    ("adidas ultraboost",           190),
    ("adidas nmd r1",               140),
    ("adidas campus",                90),
    ("adidas handball spezial",     110),
    ("adidas forum",                 90),
    # New Balance
    ("new balance 990v5",           185),
    ("new balance 990v4",           185),
    ("new balance 990v3",           185),
    ("new balance 992",             185),
    ("new balance 993",             190),
    ("new balance 2002r",           130),
    ("new balance 550",             110),
    ("new balance 574",              90),
    ("new balance 327",              80),
    ("new balance 1080",            165),
    ("new balance 860",             130),
    # Puma
    ("puma suede",                   75),
    ("puma rs-x",                   110),
    ("puma clyde",                   80),
    # Converse
    ("converse chuck 70",            90),
    ("converse chuck taylor",        70),
    ("converse one star",            85),
    # Saucony
    ("saucony shadow 6000",         140),
    ("saucony jazz",                 90),
    # ASICS
    ("asics gel-lyte",              120),
    ("asics gel-nimbus",            160),
    # Reebok
    ("reebok club c",                80),
    ("reebok classic",               75),
    ("reebok freestyle",             80),
]

HYPE_LABELS = {
    1: "General Release",
    2: "Popular",
    3: "Hyped",
    4: "Limited",
    5: "Grail",
}

HYPE_DESCRIPTIONS = {
    1: "Widely available. Walk in and buy, no rush.",
    2: "Sells out eventually. Be ready online or in-store.",
    3: "Fast sellout. Need speed or bots. Limited restocks.",
    4: "Raffle or draw entry. Very hard to get at retail.",
    5: "Instant global sellout. Major collab or iconic colorway. High resale.",
}


# ---------------------------------------------------------------------------
# Price lookup helper
# ---------------------------------------------------------------------------

def lookup_known_price(name: str):
    """Return a known retail price for the given shoe name, or None.
    Longest matching substring wins (more specific matches take priority).
    """
    n = (name or "").lower()
    best_len, best_price = 0, None
    for keyword, price in KNOWN_PRICES:
        if keyword in n and len(keyword) > best_len:
            best_len  = len(keyword)
            best_price = price
    return best_price


# ---------------------------------------------------------------------------
# Hype calculator
# ---------------------------------------------------------------------------

def calculate_hype_level(name: str, brand: str, price, sale_methods: list) -> int:
    name_lower  = (name  or "").lower()
    brand_lower = (brand or "").lower()
    sale_text   = " ".join(sale_methods or []).lower()

    # Base from brand
    score = 1
    for brand_key, base in BRAND_BASE_HYPE.items():
        if brand_key in brand_lower:
            score = max(score, base)
            break

    # Grail keywords → instant 5
    for kw in GRAIL_KEYWORDS:
        if kw in name_lower:
            score = max(score, 5)
            break

    # Limited keywords → 4
    if score < 5:
        for kw in LIMITED_KEYWORDS:
            if re.search(r'\b' + re.escape(kw.strip()) + r'\b', name_lower):
                score = max(score, 4)
                break

    # Hyped silhouette/colorway → 3
    if score < 4:
        for kw in HYPED_KEYWORDS:
            if kw in name_lower:
                score = max(score, 3)
                break

    # Sale method boosts
    if any(kw in sale_text for kw in ("raffle", "lottery", "draw")):
        score = min(5, score + 1)
    if "snkrs" in sale_text and "in-store" not in sale_text:
        score = min(5, score + 1)
    if "confirmed app" in sale_text and "in-store" not in sale_text:
        score = min(5, score + 1)

    # Price factor
    if price:
        if price >= 500:
            score = min(5, score + 1)
        elif price >= 300:
            score = min(5, max(score, 3))
        elif price >= 200:
            score = min(5, max(score, 2))

    return max(1, min(5, score))
