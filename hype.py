"""
Hype Score Calculator for sneaker releases.

Calculates a 1-10 hype score based on:
  - Resell premium (50% weight) — market value vs retail price
  - Brand factor (20% weight) — inherent brand hype
  - Silhouette boost (20% weight) — known high-demand models
  - Collaboration detection (10% weight) — collab keywords in name
"""

# ---------------------------------------------------------------------------
# Brand hype ratings (1-10 scale)
# ---------------------------------------------------------------------------

BRAND_HYPE = {
    "jordan": 9,
    "yeezy": 9,
    "nike": 7,
    "adidas": 5,
    "new balance": 6,
    "under armour": 3,
}
DEFAULT_BRAND_HYPE = 4

# ---------------------------------------------------------------------------
# High-demand silhouettes / models (partial match, case-insensitive)
# ---------------------------------------------------------------------------

HIGH_HYPE_SILHOUETTES = [
    # Jordan
    "air jordan 1",
    "air jordan 3",
    "air jordan 4",
    "air jordan 5",
    "air jordan 6",
    "air jordan 11",
    "jordan 1 ",
    "jordan 3 ",
    "jordan 4 ",
    "jordan 5 ",
    "jordan 11",
    # Nike
    "dunk low",
    "dunk high",
    "sb dunk",
    "air force 1",
    "air max 1",
    "air max 90",
    "air max 95",
    "air max 97",
    "foamposite",
    "air foamposite",
    "lebron",
    "kobe",
    # Yeezy
    "yeezy boost 350",
    "yeezy boost 700",
    "yeezy slide",
    "yeezy foam",
    # Adidas
    "ultraboost",
    "campus",
    "samba",
    # New Balance
    "550",
    "2002r",
    "990",
    "992",
    "993",
]

MEDIUM_HYPE_SILHOUETTES = [
    "air jordan 2",
    "air jordan 7",
    "air jordan 8",
    "air jordan 9",
    "air jordan 10",
    "air jordan 12",
    "air jordan 13",
    "jordan 2 ",
    "jordan 7 ",
    "jordan 12",
    "jordan 13",
    "air max plus",
    "air max tn",
    "vapormax",
    "blazer",
    "kyrie",
    "kd ",
    "zoom freak",
    "yeezy 500",
    "yeezy qntm",
    "forum",
]

# ---------------------------------------------------------------------------
# Collaboration keywords (case-insensitive substring match)
# ---------------------------------------------------------------------------

COLLAB_KEYWORDS = [
    "travis scott",
    "cactus jack",
    "off-white",
    "off white",
    "virgil",
    "supreme",
    "a ma maniere",
    "a ma maniére",
    "union",
    "fragment",
    "sacai",
    "ambush",
    "stussy",
    "stüssy",
    "patta",
    "concepts",
    "undefeated",
    "social status",
    "trophy room",
    "clot",
    "j balvin",
    "eminem",
    "grateful dead",
    "sean wotherspoon",
    "wotherspoon",
    "billie eilish",
    "bad bunny",
    "pharrell",
    "fear of god",
    "jerry lorenzo",
    "swarovski",
    "dior",
    "louis vuitton",
    "tiffany",
    "playstation",
    "atmos",
    "kith",
]


def _resell_premium_score(retail_price: float | None, market_value: float | None) -> float | None:
    """
    Calculate a 1-10 score based on resell premium.
    Returns None if data is insufficient.
    """
    if retail_price is None or market_value is None:
        return None
    if retail_price <= 0:
        return None

    premium = (market_value - retail_price) / retail_price

    # Map premium to 1-10 scale:
    #   <= 0%  → 1 (no premium, sitting on shelves)
    #   10%    → 3
    #   30%    → 5
    #   60%    → 7
    #   100%+  → 8
    #   200%+  → 9
    #   300%+  → 10
    if premium <= 0:
        return 1.0
    elif premium <= 0.10:
        return 1.0 + (premium / 0.10) * 2.0  # 1-3
    elif premium <= 0.30:
        return 3.0 + ((premium - 0.10) / 0.20) * 2.0  # 3-5
    elif premium <= 0.60:
        return 5.0 + ((premium - 0.30) / 0.30) * 2.0  # 5-7
    elif premium <= 1.00:
        return 7.0 + ((premium - 0.60) / 0.40) * 1.0  # 7-8
    elif premium <= 2.00:
        return 8.0 + ((premium - 1.00) / 1.00) * 1.0  # 8-9
    else:
        return 10.0


def _brand_score(brand: str) -> float:
    """Return the brand hype score (1-10)."""
    return float(BRAND_HYPE.get(brand.lower().strip(), DEFAULT_BRAND_HYPE))


def _silhouette_score(name: str, silhouette: str) -> float:
    """Return a silhouette hype score (1-10) based on model matching."""
    combined = f"{name} {silhouette}".lower()

    for pattern in HIGH_HYPE_SILHOUETTES:
        if pattern in combined:
            return 9.0

    for pattern in MEDIUM_HYPE_SILHOUETTES:
        if pattern in combined:
            return 6.0

    return 3.0


def _collab_score(name: str) -> float:
    """Return 10 if a collaboration is detected, 1 otherwise."""
    name_lower = name.lower()
    for keyword in COLLAB_KEYWORDS:
        if keyword in name_lower:
            return 10.0
    return 1.0


def calculate_hype_score(sneaker: dict) -> tuple[int, str]:
    """
    Calculate the hype score for a sneaker.

    Args:
        sneaker: Dict with keys name, brand, silhouette, retail_price,
                 estimated_market_value.

    Returns:
        Tuple of (score: int 1-10, level: str).
        Level is one of: "LOW", "MEDIUM", "HIGH", "EXTREME".
    """
    name = sneaker.get("name", "")
    brand = sneaker.get("brand", "")
    silhouette = sneaker.get("silhouette", "")
    retail = sneaker.get("retail_price")
    market = sneaker.get("estimated_market_value")

    resell = _resell_premium_score(retail, market)

    b_score = _brand_score(brand)
    s_score = _silhouette_score(name, silhouette)
    c_score = _collab_score(name)

    if resell is not None:
        # Full formula with all 4 factors
        raw = (resell * 0.50) + (b_score * 0.20) + (s_score * 0.20) + (c_score * 0.10)
    else:
        # No market data — rescale remaining factors
        raw = (b_score * 0.35) + (s_score * 0.45) + (c_score * 0.20)

    # Clamp to 1-10
    score = max(1, min(10, round(raw)))

    # Assign level
    if score >= 9:
        level = "EXTREME"
    elif score >= 7:
        level = "HIGH"
    elif score >= 4:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level
