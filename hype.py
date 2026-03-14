"""
Hype Level Calculator for Sneaker Releases

Scale (1-5):
  1 - General Release  : Widely available at all retailers. No rush needed.
  2 - Popular          : High demand, may sell out but restocks occur.
  3 - Hyped            : Sells out in minutes. Bots are prevalent. Limited restocks.
  4 - Limited          : Raffle/draw required. Very low stock. Big resale premium.
  5 - Grail            : Extreme rarity. Major collab or iconic colorway. Instant global sellout.
"""

# Collaborations / names that signal extreme hype (Level 5)
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
    "nocta", "ambush x", "clot x", "bape x", "medicom",
]

# Limited / exclusive signals (Level 4)
LIMITED_KEYWORDS = [
    "limited", "exclusive", "special edition", "friends and family",
    "friends & family", "player exclusive", "pe ", " pe\b",
    "collab", "collaboration", "art basel", "lottery", "draw",
    "invite only", "members only", "reserve", "prm",
]

# Hyped silhouettes and colorways (Level 3)
HYPED_KEYWORDS = [
    "retro og", "retro high og", "og ", " og\"", "'bred'", "bred toe",
    "chicago", "royal", "banned", "shadow", "university blue",
    "obsidian", "shattered backboard", "fire red", "sport blue",
    "french blue", "navy", "cement", "elephant", "infrared",
    "pine green", "court purple", "mocha", "travis",
    "ultraboost", "nmd r1", "yeezy boost", "yeezy 350", "yeezy 700",
    "yeezy slide", "yeezy foam",
    "dunk low", "dunk high", "sb dunk", "air force 1 sp",
    "samba og", "spezial", "gazelle indoor",
    "550", "990v3", "990v4", "990v5", "992", "993", "2002r",
    "new balance collab", "aimé leon dore", "ald x",
    "air max 1 sp", "air max 90 sp", "am1 ", "am90 ",
]

# Brand base hype values (starting floor)
BRAND_BASE_HYPE = {
    "jordan":        4,
    "air jordan":    4,
    "adidas (yeezy)":4,
    "yeezy":         4,
    "nike":          3,
    "adidas":        3,
    "new balance":   2,
    "converse":      2,
    "puma":          2,
    "vans":          2,
    "reebok":        2,
    "asics":         2,
    "saucony":       2,
    "under armour":  1,
    "ua ":           1,
}

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


def calculate_hype_level(name: str, brand: str, price, sale_methods: list) -> int:
    """
    Calculate hype level 1-5 based on name, brand, price, and sale method.

    Args:
        name:         Full shoe name / title
        brand:        Detected brand string
        price:        Retail price as float, or None
        sale_methods: List of sale method strings

    Returns:
        int between 1 and 5
    """
    name_lower  = (name  or "").lower()
    brand_lower = (brand or "").lower()
    sale_text   = " ".join(sale_methods or []).lower()

    # --- Base score from brand ---
    score = 1
    for brand_key, base in BRAND_BASE_HYPE.items():
        if brand_key in brand_lower:
            score = max(score, base)
            break

    # --- Grail keyword check (instant 5) ---
    for kw in GRAIL_KEYWORDS:
        if kw in name_lower:
            score = max(score, 5)
            break

    # --- Limited keyword check ---
    if score < 5:
        for kw in LIMITED_KEYWORDS:
            if kw in name_lower:
                score = max(score, 4)
                break

    # --- Hyped silhouette / colorway check ---
    if score < 4:
        for kw in HYPED_KEYWORDS:
            if kw in name_lower:
                score = max(score, 3)
                break

    # --- Sale method boosts ---
    if any(kw in sale_text for kw in ("raffle", "lottery", "draw")):
        score = min(5, score + 1)

    # SNKRS-only (no in-store) signals extra exclusivity
    if "snkrs" in sale_text and "in-store" not in sale_text:
        score = min(5, score + 1)

    # Confirmed App-only
    if "confirmed app" in sale_text and "in-store" not in sale_text:
        score = min(5, score + 1)

    # --- Price factor ---
    if price:
        if price >= 500:
            score = min(5, score + 1)
        elif price >= 300:
            score = min(5, max(score, 3))
        elif price >= 200:
            score = min(5, max(score, 2))

    return max(1, min(5, score))
