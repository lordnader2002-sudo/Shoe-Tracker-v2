"""
Excel Exporter – professional dark-mode workbook for Sneaker Release Tracker.
Sheets: 📋 Releases · 📊 Summary · 📖 Legend
"""

import io
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------------
# Palette  (hex WITHOUT leading #)
# ---------------------------------------------------------------------------
C = {
    "bg0":     "0D1117",
    "bg1":     "161B22",
    "bg2":     "1F2937",
    "bg_alt":  "111827",
    "txt":     "E6EDF3",
    "muted":   "8B949E",
    "blue":    "58A6FF",
    "purple":  "BC8CFF",
    "green":   "3FB950",
    "yellow":  "D29922",
    "orange":  "F78166",
    "red":     "FF4040",
    "border":  "30363D",
    # brands
    "jordan":  "E03131",
    "nike":    "FA7343",
    "adidas":  "40C057",
    "yeezy":   "FAB005",
    "nb":      "4DABF7",
    "puma":    "FF6B6B",
    "ua":      "5C7CFA",
    "default": "8B949E",
}

HYPE_COLORS = {1: C["green"], 2: C["yellow"], 3: C["orange"], 4: C["red"], 5: C["purple"]}
HYPE_LABELS = {
    1: "⚪ General Release",
    2: "🟡 Popular",
    3: "🟠 Hyped",
    4: "🔴 Limited",
    5: "🟣 Grail",
}
BRAND_COLORS = {
    "Jordan":         C["jordan"],
    "Nike":           C["nike"],
    "Adidas":         C["adidas"],
    "Adidas (Yeezy)": C["yeezy"],
    "New Balance":    C["nb"],
    "Puma":           C["puma"],
    "Under Armour":   C["ua"],
}


# ---------------------------------------------------------------------------
# Style primitives
# ---------------------------------------------------------------------------

def _fill(hex_color):
    return PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")


def _font(color=None, bold=False, size=10, underline=None, italic=False):
    kw = dict(color=color or C["txt"], bold=bold, size=size, name="Calibri", italic=italic)
    if underline:
        kw["underline"] = underline
    return Font(**kw)


def _thin(color=None):
    return Side(style="thin", color=color or C["border"])


def _thick(color=None):
    return Side(style="medium", color=color or C["blue"])


def _border_thin():
    s = _thin()
    return Border(left=s, right=s, top=s, bottom=s)


def _border_outer(color=None):
    t = _thick(color)
    return Border(left=t, right=t, top=t, bottom=t)


def _align(h="left", wrap=True, v="center"):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)


def _auto_col(ws, col_idx, all_values, cap=60, floor=10):
    """Set column width to fit content."""
    mx = max((len(str(v)) for v in all_values if v is not None), default=floor)
    ws.column_dimensions[get_column_letter(col_idx)].width = min(cap, max(floor, mx * 1.18))


# ---------------------------------------------------------------------------
# Shared block builders
# ---------------------------------------------------------------------------

def _title_bar(ws, row, text, color, end_col):
    lc = get_column_letter(end_col)
    ws.merge_cells(f"A{row}:{lc}{row}")
    c = ws.cell(row=row, column=1, value=text)
    c.fill      = _fill(C["bg0"])
    c.font      = _font(color, bold=True, size=14)
    c.alignment = _align("center", wrap=False)
    c.border    = _border_outer(color)
    ws.row_dimensions[row].height = 38


def _section_hdr(ws, row, text, end_col, color=None):
    lc = get_column_letter(end_col)
    ws.merge_cells(f"A{row}:{lc}{row}")
    c = ws.cell(row=row, column=1, value=text)
    c.fill      = _fill(C["bg2"])
    c.font      = _font(color or C["blue"], bold=True, size=11)
    c.alignment = _align("center", wrap=False)
    ws.row_dimensions[row].height = 28


def _col_hdr(ws, row, col, text):
    c = ws.cell(row=row, column=col, value=text)
    c.fill      = _fill(C["bg2"])
    c.font      = _font(C["blue"], bold=True, size=10)
    c.alignment = _align("center", wrap=False)
    c.border    = Border(
        left=_thin(), right=_thin(),
        top=_thick(), bottom=_thick(),
    )
    ws.row_dimensions[row].height = 26
    return c


def _dc(ws, row, col, val, bg, color=None, bold=False, align="left",
        wrap=True, size=10, underline=None, url=None):
    """Write a styled data cell."""
    c = ws.cell(row=row, column=col, value=val)
    c.fill      = _fill(bg)
    c.font      = _font(color or C["txt"], bold=bold, size=size, underline=underline)
    c.alignment = _align(align, wrap=wrap)
    c.border    = _border_thin()
    if url:
        c.hyperlink = url
    return c


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def export_to_excel(releases: list) -> io.BytesIO:
    wb = Workbook()
    wb.remove(wb.active)
    _releases_sheet(wb, releases)
    _summary_sheet(wb, releases)
    _legend_sheet(wb)
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out


# ---------------------------------------------------------------------------
# Sheet 1 – Releases
# ---------------------------------------------------------------------------

COLS = [
    # (header,           max_width)
    ("Shoe Name",        42),
    ("Brand",            18),
    ("Release Date",     15),
    ("Sale Methods",     36),
    ("Hype ★",          12),
    ("Status",           20),
    ("Source",           50),
]


def _releases_sheet(wb, releases):
    ws = wb.create_sheet("📋 Releases", 0)
    ws.sheet_properties.tabColor = C["blue"]
    ws.sheet_view.showGridLines  = False

    ncols = len(COLS)
    now   = datetime.now().strftime("%B %d, %Y  %I:%M %p")

    # ── Title row ────────────────────────────────────────────────────────
    _title_bar(ws, 1, f"🔥  SNEAKER RELEASE TRACKER   ·   {now}", C["blue"], ncols)

    # ── Column headers (row 2) ────────────────────────────────────────────
    for ci, (hdr, _) in enumerate(COLS, 1):
        _col_hdr(ws, 2, ci, hdr.upper())

    # ── Freeze rows 1+2 (title + headers scroll-locked) ──────────────────
    ws.freeze_panes = "A3"

    # ── Track content for auto-sizing ────────────────────────────────────
    col_vals = {i: [COLS[i - 1][0]] for i in range(1, ncols + 1)}

    # ── Data rows ────────────────────────────────────────────────────────
    for ri, rel in enumerate(releases, 3):
        bg      = C["bg_alt"] if ri % 2 == 0 else C["bg1"]
        hype    = rel.get("hype_level", 1)
        hc      = HYPE_COLORS.get(hype, C["default"])
        brand   = rel.get("brand", "Other")
        bc      = BRAND_COLORS.get(brand, C["default"])
        url     = rel.get("source_url", "") or ""
        methods = ", ".join(rel.get("sale_methods") or []) or "TBD"
        date    = rel.get("release_date", "TBD") or "TBD"
        name    = rel.get("name", "")
        stars   = f"{'★' * hype}{'☆' * (5 - hype)}  {hype}/5"

        ws.row_dimensions[ri].height = 20

        _dc(ws, ri, 1, name,    bg, C["txt"], bold=True)
        _dc(ws, ri, 2, brand,   bg, bc,       bold=True,  align="center", wrap=False)
        _dc(ws, ri, 3, date,    bg, C["blue"] if date != "TBD" else C["muted"],
            bold=False, align="center", wrap=False)
        _dc(ws, ri, 4, methods, bg, C["muted"], size=9)
        _dc(ws, ri, 5, stars,   bg, hc, bold=True, align="center", wrap=False)
        _dc(ws, ri, 6, HYPE_LABELS.get(hype, ""), bg, hc, bold=True, align="center")
        _dc(ws, ri, 7, url,     bg, C["blue"], size=9, underline="single",
            align="left", wrap=False, url=url if url else None)

        for ci, v in enumerate([name, brand, date, methods, stars,
                                 HYPE_LABELS.get(hype, ""), url], 1):
            col_vals[ci].append(v)

    # ── Auto-size columns ─────────────────────────────────────────────────
    for ci, (_, cap) in enumerate(COLS, 1):
        _auto_col(ws, ci, col_vals[ci], cap=cap)

    # ── Draw outer border around header + data block ──────────────────────
    last_data_row = len(releases) + 2
    for ci in range(1, ncols + 1):
        lc = get_column_letter(ci)
        for ri in range(2, last_data_row + 1):
            cell = ws[f"{lc}{ri}"]
            l = _thick() if ci == 1           else _thin()
            r = _thick() if ci == ncols        else _thin()
            t = cell.border.top
            b = _thick() if ri == last_data_row else _thin()
            cell.border = Border(left=l, right=r, top=t, bottom=b)


# ---------------------------------------------------------------------------
# Sheet 2 – Summary
# ---------------------------------------------------------------------------

def _summary_sheet(wb, releases):
    ws = wb.create_sheet("📊 Summary", 1)
    ws.sheet_properties.tabColor = C["purple"]
    ws.sheet_view.showGridLines  = False

    for col, w in [("A", 28), ("B", 22), ("C", 20), ("D", 18)]:
        ws.column_dimensions[col].width = w

    now   = datetime.now().strftime("%B %d, %Y  %I:%M %p")
    today = datetime.now().strftime("%Y-%m-%d")
    _title_bar(ws, 1, f"📊  SNEAKER TRACKER — SUMMARY   ·   {now}", C["purple"], 4)

    # ── Aggregate stats ───────────────────────────────────────────────────
    upcoming   = [r for r in releases
                  if r.get("release_date", "TBD") not in ("TBD", "")
                  and r["release_date"] >= today]
    grails     = [r for r in releases if r.get("hype_level") == 5]

    brands_map: dict = {}
    hype_map:   dict = {}
    source_map: dict = {}
    method_map: dict = {}
    for r in releases:
        b = r.get("brand", "Other")
        if b not in brands_map:
            brands_map[b] = {"count": 0, "hype_sum": 0}
        brands_map[b]["count"]    += 1
        brands_map[b]["hype_sum"] += r.get("hype_level", 1)

        h = r.get("hype_level", 1)
        hype_map[h] = hype_map.get(h, 0) + 1

        src = r.get("source", "Unknown")
        source_map[src] = source_map.get(src, 0) + 1

        for m in r.get("sale_methods") or []:
            method_map[m] = method_map.get(m, 0) + 1

    # ── KPI tiles ─────────────────────────────────────────────────────────
    row = 3
    _section_hdr(ws, row, "📈  KEY STATS", 4)
    row += 1

    kpis = [
        ("Total Releases",  len(releases),  C["blue"]),
        ("Upcoming",        len(upcoming),  C["green"]),
        ("Grails 🟣",       len(grails),    C["purple"]),
    ]
    label_row = row
    val_row   = row + 1

    for ci, (lbl, val, color) in enumerate(kpis, 1):
        lc = ws.cell(row=label_row, column=ci, value=lbl)
        lc.fill = _fill(C["bg2"]); lc.font = _font(C["muted"], size=9, bold=True)
        lc.alignment = _align("center", wrap=False); lc.border = _border_thin()

        vc = ws.cell(row=val_row, column=ci, value=val)
        vc.fill = _fill(C["bg1"]); vc.font = _font(color, bold=True, size=22)
        vc.alignment = _align("center", wrap=False); vc.border = _border_thin()
        ws.row_dimensions[val_row].height = 42

    row += 2

    # ── Brand breakdown ───────────────────────────────────────────────────
    row += 1
    _section_hdr(ws, row, "👟  BRAND BREAKDOWN", 4)
    row += 1
    for ci, h in enumerate(["Brand", "Releases", "Avg Hype", ""], 1):
        _col_hdr(ws, row, ci, h) if h else None
    row += 1

    for i, (brand, info) in enumerate(sorted(brands_map.items(), key=lambda x: -x[1]["count"])):
        bg    = C["bg_alt"] if i % 2 else C["bg1"]
        bc    = BRAND_COLORS.get(brand, C["default"])
        ahype = info["hype_sum"] / info["count"]
        _dc(ws, row, 1, brand,               bg, bc, bold=True)
        _dc(ws, row, 2, info["count"],        bg, C["txt"],  align="center")
        _dc(ws, row, 3, f"{ahype:.1f} / 5", bg, HYPE_COLORS.get(round(ahype), C["muted"]),
            bold=True, align="center")
        row += 1

    # ── Hype distribution ─────────────────────────────────────────────────
    row += 1
    _section_hdr(ws, row, "🔥  HYPE DISTRIBUTION", 4)
    row += 1
    for ci, h in enumerate(["Level", "Status", "Count", "% of Total"], 1):
        _col_hdr(ws, row, ci, h)
    row += 1

    total = len(releases)
    for i, lvl in enumerate(sorted(hype_map)):
        bg  = C["bg_alt"] if i % 2 else C["bg1"]
        hc  = HYPE_COLORS.get(lvl, C["default"])
        cnt = hype_map[lvl]
        _dc(ws, row, 1, f"{'★' * lvl}{'☆' * (5 - lvl)}  {lvl}/5",
            bg, hc, bold=True, align="center")
        _dc(ws, row, 2, HYPE_LABELS.get(lvl, ""), bg, hc, bold=True)
        _dc(ws, row, 3, cnt, bg, C["txt"], align="center")
        _dc(ws, row, 4, f"{cnt/total*100:.0f}%" if total else "0%",
            bg, C["muted"], align="center")
        row += 1

    # ── Source breakdown ──────────────────────────────────────────────────
    row += 1
    _section_hdr(ws, row, "🌐  SOURCE BREAKDOWN", 4)
    row += 1
    for ci, h in enumerate(["Source", "Releases", "", ""], 1):
        _col_hdr(ws, row, ci, h) if h else None
    row += 1

    for i, (src, cnt) in enumerate(sorted(source_map.items(), key=lambda x: -x[1])):
        bg = C["bg_alt"] if i % 2 else C["bg1"]
        _dc(ws, row, 1, src, bg, C["blue"], bold=True)
        _dc(ws, row, 2, cnt, bg, C["txt"], align="center")
        row += 1

    # ── Top sale methods ──────────────────────────────────────────────────
    row += 1
    _section_hdr(ws, row, "🛍️  TOP SALE METHODS", 4)
    row += 1
    for ci, h in enumerate(["Method", "Count", "", ""], 1):
        _col_hdr(ws, row, ci, h) if h else None
    row += 1

    for i, (method, cnt) in enumerate(sorted(method_map.items(), key=lambda x: -x[1])):
        bg = C["bg_alt"] if i % 2 else C["bg1"]
        _dc(ws, row, 1, method, bg, C["txt"])
        _dc(ws, row, 2, cnt,    bg, C["muted"], align="center")
        row += 1


# ---------------------------------------------------------------------------
# Sheet 3 – Legend
# ---------------------------------------------------------------------------

def _legend_sheet(wb):
    ws = wb.create_sheet("📖 Legend", 2)
    ws.sheet_properties.tabColor = C["green"]
    ws.sheet_view.showGridLines  = False

    for col, w in [("A", 22), ("B", 30), ("C", 64)]:
        ws.column_dimensions[col].width = w

    _title_bar(ws, 1, "📖  SNEAKER TRACKER — LEGEND & GUIDE", C["green"], 3)

    def section(r, text):
        ws.merge_cells(f"A{r}:C{r}")
        c = ws.cell(row=r, column=1, value=text)
        c.fill = _fill(C["bg2"]); c.font = _font(C["blue"], bold=True, size=11)
        c.alignment = _align("center"); ws.row_dimensions[r].height = 28

    def hdr3(r, a, b, cc):
        for ci, txt in zip([1, 2, 3], [a, b, cc]):
            _col_hdr(ws, r, ci, txt)

    # ── Hype guide ────────────────────────────────────────────────────────
    row = 3
    section(row, "🔥  HYPE LEVEL GUIDE"); row += 1
    hdr3(row, "Level", "Status", "What it means"); row += 1

    hype_info = [
        (1, "Widely available at all US retailers. Walk-in purchase, no rush or special account needed."),
        (2, "High demand – sells out eventually but generally restocks. Prepare checkout ahead of time."),
        (3, "Sells out within minutes. Bot competition is high. Limited restocks. Speed or luck required."),
        (4, "Raffle or draw entry required. Quantities are very low. Expect 2–5× resale premium."),
        (5, "Instant global sellout. Major designer collab or iconic colorway. Resale can be 5–15×+ retail."),
    ]
    for i, (lvl, desc) in enumerate(hype_info):
        bg = C["bg_alt"] if i % 2 else C["bg1"]
        hc = HYPE_COLORS[lvl]
        _dc(ws, row, 1, f"{'★' * lvl}{'☆' * (5 - lvl)}  {lvl}/5",
            bg, hc, bold=True, align="center", size=12)
        _dc(ws, row, 2, HYPE_LABELS[lvl], bg, hc, bold=True)
        _dc(ws, row, 3, desc, bg, C["txt"], size=9, wrap=True)
        ws.row_dimensions[row].height = 36; row += 1

    # ── Sale methods ──────────────────────────────────────────────────────
    row += 1
    section(row, "🛍️  SALE METHODS GUIDE"); row += 1
    hdr3(row, "Method", "Platform", "Description"); row += 1

    methods_info = [
        ("SNKRS App",       "Nike / Jordan Brand", "Exclusive drop app. Most limited Nike/Jordan releases launch here first."),
        ("Confirmed App",   "Adidas",              "Draw/reservation system for Yeezy and select collabs."),
        ("Raffle",          "Various Retailers",   "Submit entry for random winner selection. No speed advantage."),
        ("Draw",            "Various Retailers",   "Open entry window with random selection of buyers."),
        ("In-Store",        "Physical Retail",     "Available at brick-and-mortar. May require lining up in advance."),
        ("Online",          "Brand / Retailer",    "Released on brand or retailer website at drop time. Fast checkout needed."),
        ("Foot Locker",     "footlocker.com",      "FLX app / footlocker.com / Foot Locker and Kids Foot Locker stores."),
        ("Finish Line",     "finishline.com",      "finishline.com or Finish Line retail stores (JD Sports owned)."),
        ("Champs Sports",   "champssports.com",    "champssports.com or Champs Sports retail (Foot Locker family)."),
        ("JD Sports",       "jdsports.com",        "jdsports.com US stores — often carries exclusive US colorways."),
        ("StockX (Resale)", "stockx.com",          "Bid/ask resale marketplace. Price is ABOVE retail."),
        ("GOAT (Resale)",   "goat.com",            "Authentication-based resale app. Consignment or instant purchase."),
    ]
    for i, (method, where, desc) in enumerate(methods_info):
        bg = C["bg_alt"] if i % 2 else C["bg1"]
        _dc(ws, row, 1, method, bg, C["blue"], bold=True)
        _dc(ws, row, 2, where,  bg, C["muted"], size=9)
        _dc(ws, row, 3, desc,   bg, C["txt"],   size=9, wrap=True)
        ws.row_dimensions[row].height = 30; row += 1

    # ── Column guide ──────────────────────────────────────────────────────
    row += 1
    section(row, "📋  RELEASES SHEET — COLUMN GUIDE"); row += 1
    hdr3(row, "Column", "Data Type", "Notes"); row += 1

    col_guide = [
        ("Shoe Name",    "Text",   "Full name including colorway / collab partner."),
        ("Brand",        "Text",   "Nike · Jordan · Adidas · Adidas (Yeezy) · New Balance · Puma · Under Armour · etc."),
        ("Release Date", "Date",   "YYYY-MM-DD (US release, Eastern time). TBD = not yet announced."),
        ("Sale Methods", "Text",   "How to buy at retail — SNKRS, Raffle, In-Store, Online, etc."),
        ("Hype ★",       "1–5",   "Proprietary hype score. See Hype Level Guide above."),
        ("Status",       "Text",   "Human-readable label (General Release → Grail)."),
        ("Source",       "URL",    "Clickable link to the original source article."),
    ]
    for i, (col, typ, note) in enumerate(col_guide):
        bg = C["bg_alt"] if i % 2 else C["bg1"]
        _dc(ws, row, 1, col,  bg, C["blue"],  bold=True)
        _dc(ws, row, 2, typ,  bg, C["muted"], size=9, align="center")
        _dc(ws, row, 3, note, bg, C["txt"],   size=9, wrap=True)
        ws.row_dimensions[row].height = 28; row += 1
