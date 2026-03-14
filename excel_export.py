"""
Excel Exporter – dark-mode styled workbook for Sneaker Release Tracker.
Three sheets: Releases (main data), Summary (brand/hype stats), Legend (guide).
"""

import io
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---------------------------------------------------------------------------
# Dark-mode palette  (hex WITHOUT leading #)
# ---------------------------------------------------------------------------
C = {
    "bg0":        "0D1117",   # darkest – sheet background / title row
    "bg1":        "161B22",   # card background
    "bg2":        "1F2937",   # section headers
    "bg_alt":     "111827",   # alternate row
    "txt":        "E6EDF3",   # primary text
    "txt_muted":  "8B949E",   # secondary text
    "blue":       "58A6FF",   # accent / column headers
    "purple":     "BC8CFF",   # purple accent / legend tab
    "green":      "3FB950",   # hype 1 / price / legend tab
    "yellow":     "D29922",   # hype 2
    "orange":     "F78166",   # hype 3
    "red":        "FF4040",   # hype 4
    "border":     "30363D",   # cell border
    # Brand colours
    "jordan":     "E03131",
    "nike":       "FA7343",
    "adidas":     "40C057",
    "yeezy":      "FAB005",
    "nb":         "4DABF7",
    "puma":       "FF6B6B",
    "ua":         "5C7CFA",
    "default":    "8B949E",
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
    "Jordan":          C["jordan"],
    "Nike":            C["nike"],
    "Adidas":          C["adidas"],
    "Adidas (Yeezy)":  C["yeezy"],
    "New Balance":     C["nb"],
    "Puma":            C["puma"],
    "Under Armour":    C["ua"],
}


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

def _fill(hex_color):
    return PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")


def _font(color=None, bold=False, size=10, underline=None):
    kw = dict(color=color or C["txt"], bold=bold, size=size, name="Calibri")
    if underline:
        kw["underline"] = underline
    return Font(**kw)


def _border():
    s = Side(style="thin", color=C["border"])
    return Border(left=s, right=s, top=s, bottom=s)


def _align(h="left", wrap=True):
    return Alignment(horizontal=h, vertical="center", wrap_text=wrap)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def export_to_excel(releases: list) -> io.BytesIO:
    """Return an Excel workbook (BytesIO) with dark-mode styling."""
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

def _releases_sheet(wb, releases):
    ws = wb.create_sheet("Sneaker Releases", 0)
    ws.sheet_properties.tabColor = C["blue"]
    ws.sheet_view.showGridLines = False

    cols = [
        ("Shoe Name",    36),
        ("Brand",        18),
        ("Release Date", 14),
        ("Price (USD)",  12),
        ("Sale Methods", 32),
        ("Hype",         10),
        ("Status",       20),
        ("Source Link",  48),
    ]

    # ---- Title row ----
    last_col = get_column_letter(len(cols))
    ws.merge_cells(f"A1:{last_col}1")
    tc = ws["A1"]
    tc.value = (
        f"🔥  SNEAKER RELEASE TRACKER"
        f"   |   Updated: {datetime.now().strftime('%B %d, %Y  %I:%M %p')}"
    )
    tc.fill    = _fill(C["bg0"])
    tc.font    = _font(C["blue"], bold=True, size=14)
    tc.alignment = _align("center")
    ws.row_dimensions[1].height = 34

    # ---- Column headers ----
    for ci, (header, width) in enumerate(cols, 1):
        cell = ws.cell(row=2, column=ci, value=header.upper())
        cell.fill      = _fill(C["bg2"])
        cell.font      = _font(C["blue"], bold=True, size=10)
        cell.alignment = _align("center")
        cell.border    = _border()
        ws.column_dimensions[get_column_letter(ci)].width = width
    ws.row_dimensions[2].height = 26

    # ---- Data rows ----
    for ri, rel in enumerate(releases, 3):
        alt = (ri % 2 == 0)
        bg  = C["bg_alt"] if alt else C["bg1"]
        ws.row_dimensions[ri].height = 20

        hype   = rel.get("hype_level", 1)
        hc     = HYPE_COLORS.get(hype, C["default"])
        brand  = rel.get("brand", "Other")
        bc     = BRAND_COLORS.get(brand, C["default"])
        price  = rel.get("price")
        url    = rel.get("source_url", "")
        methods_str = ", ".join(rel.get("sale_methods") or []) or "TBD"

        row_vals = [
            rel.get("name", ""),
            brand,
            rel.get("release_date", "TBD"),
            f"${price:.0f}" if price else "TBD",
            methods_str,
            f"{'★' * hype}{'☆' * (5 - hype)}  {hype}/5",
            HYPE_LABELS.get(hype, ""),
            url,
        ]

        for ci, val in enumerate(row_vals, 1):
            cell = ws.cell(row=ri, column=ci, value=val)
            cell.fill   = _fill(bg)
            cell.border = _border()

            if ci == 1:   # Name
                cell.font      = _font(C["txt"], bold=True, size=10)
                cell.alignment = _align("left")
            elif ci == 2:  # Brand
                cell.font      = _font(bc, bold=True, size=10)
                cell.alignment = _align("center")
            elif ci == 3:  # Date
                cell.font      = _font(C["blue"], size=10)
                cell.alignment = _align("center")
            elif ci == 4:  # Price
                cell.font      = _font(C["green"], bold=True, size=10)
                cell.alignment = _align("center")
            elif ci == 5:  # Methods
                cell.font      = _font(C["txt_muted"], size=9)
                cell.alignment = _align("left")
            elif ci == 6:  # Stars
                cell.font      = _font(hc, bold=True, size=10)
                cell.alignment = _align("center")
            elif ci == 7:  # Label
                cell.font      = _font(hc, bold=True, size=10)
                cell.alignment = _align("center")
            elif ci == 8:  # URL
                cell.font      = _font(C["blue"], size=9, underline="single")
                if url:
                    cell.hyperlink = url
                cell.alignment = _align("left")

    ws.freeze_panes = "A3"


# ---------------------------------------------------------------------------
# Sheet 2 – Summary
# ---------------------------------------------------------------------------

def _summary_sheet(wb, releases):
    ws = wb.create_sheet("Summary", 1)
    ws.sheet_properties.tabColor = C["purple"]
    ws.sheet_view.showGridLines = False

    for col, w in [("A", 26), ("B", 22), ("C", 22)]:
        ws.column_dimensions[col].width = w

    def title_row(r, text, color):
        ws.merge_cells(f"A{r}:C{r}")
        c = ws.cell(row=r, column=1, value=text)
        c.fill      = _fill(C["bg2"])
        c.font      = _font(color, bold=True, size=12)
        c.alignment = _align("center")
        ws.row_dimensions[r].height = 28

    def hdr(r, col, text):
        c = ws.cell(row=r, column=col, value=text)
        c.fill      = _fill(C["bg1"])
        c.font      = _font(C["blue"], bold=True, size=10)
        c.alignment = _align("center")
        c.border    = _border()

    # Main title
    ws.merge_cells("A1:C1")
    tc = ws["A1"]
    tc.value     = "📊  SNEAKER TRACKER – SUMMARY"
    tc.fill      = _fill(C["bg0"])
    tc.font      = _font(C["purple"], bold=True, size=14)
    tc.alignment = _align("center")
    ws.row_dimensions[1].height = 34

    # Brand breakdown
    row = 3
    title_row(row, "BRAND BREAKDOWN", C["blue"])
    row += 1
    hdr(row, 1, "Brand"); hdr(row, 2, "Releases"); row += 1

    brand_counts: dict = {}
    for r in releases:
        b = r.get("brand", "Other")
        brand_counts[b] = brand_counts.get(b, 0) + 1

    for i, (brand, cnt) in enumerate(sorted(brand_counts.items(), key=lambda x: -x[1])):
        bg = C["bg_alt"] if i % 2 else C["bg1"]
        bc = BRAND_COLORS.get(brand, C["default"])
        c1 = ws.cell(row=row, column=1, value=brand)
        c1.fill = _fill(bg); c1.font = _font(bc, bold=True); c1.alignment = _align("left")
        c2 = ws.cell(row=row, column=2, value=cnt)
        c2.fill = _fill(bg); c2.font = _font(); c2.alignment = _align("center")
        row += 1

    # Hype distribution
    row += 1
    title_row(row, "HYPE LEVEL BREAKDOWN", C["blue"])
    row += 1
    hdr(row, 1, "Level"); hdr(row, 2, "Status"); hdr(row, 3, "Count"); row += 1

    hype_counts: dict = {}
    for r in releases:
        h = r.get("hype_level", 1)
        hype_counts[h] = hype_counts.get(h, 0) + 1

    for i, level in enumerate(sorted(hype_counts)):
        bg  = C["bg_alt"] if i % 2 else C["bg1"]
        hc  = HYPE_COLORS.get(level, C["default"])
        lbl = HYPE_LABELS.get(level, f"Level {level}")
        ws.cell(row=row, column=1, value=f"★ {level}/5").fill = _fill(bg)
        ws.cell(row=row, column=1).font = _font(hc, bold=True); ws.cell(row=row, column=1).alignment = _align("center")
        ws.cell(row=row, column=2, value=lbl).fill = _fill(bg)
        ws.cell(row=row, column=2).font = _font(hc, bold=True); ws.cell(row=row, column=2).alignment = _align("left")
        ws.cell(row=row, column=3, value=hype_counts[level]).fill = _fill(bg)
        ws.cell(row=row, column=3).font = _font(); ws.cell(row=row, column=3).alignment = _align("center")
        row += 1

    # Total
    row += 1
    ws.merge_cells(f"A{row}:C{row}")
    c = ws.cell(row=row, column=1, value=f"Total Releases Tracked:  {len(releases)}")
    c.fill = _fill(C["bg2"]); c.font = _font(C["blue"], bold=True, size=12); c.alignment = _align("center")


# ---------------------------------------------------------------------------
# Sheet 3 – Legend
# ---------------------------------------------------------------------------

def _legend_sheet(wb):
    ws = wb.create_sheet("Legend & Guide", 2)
    ws.sheet_properties.tabColor = C["green"]
    ws.sheet_view.showGridLines = False

    for col, w in [("A", 20), ("B", 28), ("C", 60)]:
        ws.column_dimensions[col].width = w

    # Title
    ws.merge_cells("A1:C1")
    tc = ws["A1"]
    tc.value     = "📖  SNEAKER TRACKER — LEGEND & GUIDE"
    tc.fill      = _fill(C["bg0"])
    tc.font      = _font(C["green"], bold=True, size=14)
    tc.alignment = _align("center")
    ws.row_dimensions[1].height = 34

    def section_hdr(r, text):
        ws.merge_cells(f"A{r}:C{r}")
        c = ws.cell(row=r, column=1, value=text)
        c.fill = _fill(C["bg2"]); c.font = _font(C["blue"], bold=True, size=12)
        c.alignment = _align("center"); ws.row_dimensions[r].height = 28

    def col_hdrs(r, *labels):
        for ci, lbl in enumerate(labels, 1):
            c = ws.cell(row=r, column=ci, value=lbl)
            c.fill = _fill(C["bg1"]); c.font = _font(C["blue"], bold=True)
            c.alignment = _align("center"); c.border = _border()

    # ---- Hype levels ----
    row = 3
    section_hdr(row, "🔥  HYPE LEVEL GUIDE"); row += 1
    col_hdrs(row, "Level", "Status", "What it means"); row += 1

    hype_info = [
        (1, C["green"],  "Widely available at all retailers. Walk-in purchase, no rush or special account needed."),
        (2, C["yellow"], "High demand – sells out eventually but generally restocks. Prepare online checkout ahead of time."),
        (3, C["orange"], "Sells out within minutes. Bot competition is high. Limited restocks. Speed or luck required."),
        (4, C["red"],    "Raffle or draw entry required. Quantities are very low. Expect 2–5× resale premium."),
        (5, C["purple"], "Instant global sellout. Major designer collab or iconic colorway. Resale can be 5–15×+ retail."),
    ]
    for i, (lvl, color, desc) in enumerate(hype_info):
        bg = C["bg_alt"] if i % 2 else C["bg1"]
        lbl = HYPE_LABELS[lvl]
        ws.cell(row=row, column=1, value=f"★ {lvl}/5").fill = _fill(bg)
        ws.cell(row=row, column=1).font = _font(color, bold=True, size=12); ws.cell(row=row, column=1).alignment = _align("center")
        ws.cell(row=row, column=2, value=lbl).fill = _fill(bg)
        ws.cell(row=row, column=2).font = _font(color, bold=True); ws.cell(row=row, column=2).alignment = _align("left")
        c = ws.cell(row=row, column=3, value=desc); c.fill = _fill(bg)
        c.font = _font(size=9); c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        ws.row_dimensions[row].height = 38; row += 1

    # ---- Sale methods ----
    row += 1
    section_hdr(row, "🛍️  SALE METHODS GUIDE"); row += 1
    col_hdrs(row, "Method", "", "Description"); row += 1

    methods_info = [
        ("SNKRS App",        "Nike's exclusive drop app. Most limited Nike/Jordan releases go here first."),
        ("Confirmed App",    "Adidas draw/reservation app. Required for Yeezy and select collabs."),
        ("Raffle",           "Submit entry online or in-store. Random winner selection — no speed advantage."),
        ("Draw",             "Similar to raffle. Open entry window, then random selection of buyers."),
        ("In-Store",         "Available at physical retail locations. May require lining up the night before."),
        ("Online",           "Released on brand or retailer website. Requires fast checkout or queue system."),
        ("Foot Locker",      "FLX app / footlocker.com / physical Foot Locker stores."),
        ("Finish Line",      "finishline.com or Finish Line retail stores."),
        ("Champs Sports",    "champssports.com or Champs retail stores (Foot Locker family)."),
        ("JD Sports",        "jdsports.com or JD Sports retail locations."),
        ("END Clothing",     "endclothing.com — UK-based, popular for European exclusive drops."),
        ("StockX (Resale)",  "Bid/ask marketplace. Price shown is current resale — NOT retail."),
        ("GOAT (Resale)",    "Authentication-based resale app. Consignment or instant purchase options."),
    ]
    for i, (method, desc) in enumerate(methods_info):
        bg = C["bg_alt"] if i % 2 else C["bg1"]
        ws.cell(row=row, column=1, value=method).fill = _fill(bg)
        ws.cell(row=row, column=1).font = _font(C["blue"], bold=True); ws.cell(row=row, column=1).alignment = _align("left")
        ws.merge_cells(f"B{row}:C{row}")
        c = ws.cell(row=row, column=2, value=desc); c.fill = _fill(bg)
        c.font = _font(size=9); c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        ws.row_dimensions[row].height = 30; row += 1
