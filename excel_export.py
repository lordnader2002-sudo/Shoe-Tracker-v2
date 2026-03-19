"""
Excel export module for sneaker release reports.
Creates a formatted .xlsx workbook styled like the reference sheet:
  - Dark navy title + header rows
  - Alternating light-blue / white data rows
  - Hype level as colored text (LOW=green, MED=gold, HIGH=red, EXTREME=red)
"""

import os
from datetime import datetime, timezone

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

NAVY          = "1F3864"   # dark navy — title & header fill
LIGHT_BLUE    = "C9D9EF"   # alternating row tint
WHITE         = "FFFFFF"
COL_LOW       = "00B050"   # green
COL_MED       = "FFC000"   # gold/amber
COL_HIGH      = "FF0000"   # red
COL_EXTREME   = "FF0000"   # red (same as HIGH)

# ---------------------------------------------------------------------------
# Reusable style objects
# ---------------------------------------------------------------------------

NAVY_FILL  = PatternFill(start_color=NAVY,       end_color=NAVY,       fill_type="solid")
BLUE_FILL  = PatternFill(start_color=LIGHT_BLUE, end_color=LIGHT_BLUE, fill_type="solid")
WHITE_FILL = PatternFill(start_color=WHITE,       end_color=WHITE,       fill_type="solid")

TITLE_FONT  = Font(name="Calibri", size=13, bold=True,  color=WHITE)
HEADER_FONT = Font(name="Calibri", size=11, bold=True,  color=WHITE)
DATA_FONT   = Font(name="Calibri", size=11, bold=False, color="000000")

CENTER = Alignment(horizontal="center", vertical="center", wrap_text=False)
LEFT   = Alignment(horizontal="left",   vertical="center", wrap_text=False)

THIN_BORDER = Border(
    left=Side(style="thin",   color="AAAAAA"),
    right=Side(style="thin",  color="AAAAAA"),
    top=Side(style="thin",    color="AAAAAA"),
    bottom=Side(style="thin", color="AAAAAA"),
)

# Hype-level display: stored value → (display text, color)
HYPE_DISPLAY = {
    "EXTREME": ("EXTREME", COL_EXTREME),
    "HIGH":    ("HIGH",    COL_HIGH),
    "MEDIUM":  ("MED",     COL_MED),
    "LOW":     ("LOW",     COL_LOW),
}

# ---------------------------------------------------------------------------
# Column definitions for the main releases sheet
# (header, data-key, width, alignment, number-format)
# ---------------------------------------------------------------------------

COLUMNS = [
    ("Date",   "release_date",        12, CENTER, "M/D/YYYY"),
    ("Retail", "retail_price",        10, CENTER, "$#,##0"),
    ("Hype",   "hype_level",          11, CENTER, None),
    ("Brand",  "brand",               14, CENTER, None),
    ("Style",  "name",                46, CENTER, None),
]

NUM_COLS = len(COLUMNS)


# ---------------------------------------------------------------------------
# Helper: write a styled cell
# ---------------------------------------------------------------------------

def _cell(ws, row, col, value=None, font=None, fill=None, alignment=None,
          number_format=None, border=None):
    c = ws.cell(row=row, column=col, value=value)
    if font:          c.font          = font
    if fill:          c.fill          = fill
    if alignment:     c.alignment     = alignment
    if number_format: c.number_format = number_format
    if border:        c.border        = border
    return c


# ---------------------------------------------------------------------------
# Title block (rows 1-2)
# ---------------------------------------------------------------------------

def _write_title(ws, month_label: str):
    """Write the two-row dark-navy title block."""
    last = get_column_letter(NUM_COLS)

    # Row 1: "March 2026 Shoe Releases"
    ws.row_dimensions[1].height = 22
    c1 = ws.cell(row=1, column=1, value=f"{month_label} Shoe Releases")
    c1.font      = TITLE_FONT
    c1.fill      = NAVY_FILL
    c1.alignment = CENTER
    ws.merge_cells(f"A1:{last}1")
    for col in range(2, NUM_COLS + 1):
        ws.cell(row=1, column=col).fill = NAVY_FILL

    # Row 2: "Calculated Hype Level"
    ws.row_dimensions[2].height = 18
    c2 = ws.cell(row=2, column=1, value="Calculated Hype Level")
    c2.font      = Font(name="Calibri", size=11, bold=False, italic=True, color=WHITE)
    c2.fill      = NAVY_FILL
    c2.alignment = CENTER
    ws.merge_cells(f"A2:{last}2")
    for col in range(2, NUM_COLS + 1):
        ws.cell(row=2, column=col).fill = NAVY_FILL


# ---------------------------------------------------------------------------
# Header row (row 3)
# ---------------------------------------------------------------------------

def _write_header(ws):
    ws.row_dimensions[3].height = 18
    for col_idx, (header, _, width, _, _) in enumerate(COLUMNS, start=1):
        c = ws.cell(row=3, column=col_idx, value=header)
        c.font      = HEADER_FONT
        c.fill      = NAVY_FILL
        c.alignment = CENTER
        c.border    = THIN_BORDER
        ws.column_dimensions[get_column_letter(col_idx)].width = width


# ---------------------------------------------------------------------------
# Data rows (starting at row 4)
# ---------------------------------------------------------------------------

def _write_data_rows(ws, sneakers: list[dict]):
    for i, sneaker in enumerate(sneakers):
        row_num = i + 4                                    # data starts at row 4
        fill    = BLUE_FILL if i % 2 == 0 else WHITE_FILL # alternating shading
        ws.row_dimensions[row_num].height = 15

        for col_idx, (_, key, _, align, num_fmt) in enumerate(COLUMNS, start=1):
            value = sneaker.get(key)

            # --- transform values ---
            if key == "release_date" and isinstance(value, datetime):
                value = value.date()
            elif key == "retail_price" and value is not None:
                value = float(value)
            elif key == "hype_level":
                # handled separately for color
                pass
            elif value is None:
                value = ""

            c = ws.cell(row=row_num, column=col_idx, value=value)
            c.fill      = fill
            c.alignment = align
            c.border    = THIN_BORDER

            if num_fmt:
                c.number_format = num_fmt

            # Hype-level: colored text, no override fill
            if key == "hype_level":
                display_text, color = HYPE_DISPLAY.get(value, (str(value), "000000"))
                c.value = display_text
                c.font  = Font(name="Calibri", size=11, bold=True, color=color)
            else:
                c.font = DATA_FONT


# ---------------------------------------------------------------------------
# Sheet builders
# ---------------------------------------------------------------------------

def _month_label(sneakers: list[dict]) -> str:
    """Return e.g. 'March 2026' from the earliest release date."""
    dates = [s["release_date"] for s in sneakers
             if isinstance(s.get("release_date"), datetime)]
    if dates:
        earliest = min(dates)
        return earliest.strftime("%B %Y")
    return datetime.now().strftime("%B %Y")


def _create_releases_sheet(wb: Workbook, sneakers: list[dict], title: str, sheet_name: str):
    """Generic sheet builder used for both All Releases and High Hype Alerts."""
    if sheet_name == "All Releases":
        ws = wb.active
        ws.title = sheet_name
    else:
        ws = wb.create_sheet(sheet_name)

    _write_title(ws, title)
    _write_header(ws)

    if sneakers:
        _write_data_rows(ws, sneakers)
    else:
        row = 4
        ws.cell(row=row, column=1, value="No releases found.").font = Font(
            name="Calibri", size=11, italic=True, color="888888"
        )
        ws.merge_cells(f"A{row}:{get_column_letter(NUM_COLS)}{row}")
        ws.cell(row=row, column=1).alignment = CENTER

    ws.freeze_panes = "A4"

    if sneakers:
        last_col = get_column_letter(NUM_COLS)
        ws.auto_filter.ref = f"A3:{last_col}{len(sneakers) + 3}"


def _create_summary_sheet(wb: Workbook, sneakers: list[dict]):
    ws = wb.create_sheet("Summary")

    title_font   = Font(name="Calibri", size=13, bold=True)
    section_font = Font(name="Calibri", size=11, bold=True)
    data_font    = Font(name="Calibri", size=11)

    row = 1
    ws.cell(row=row, column=1, value="Sneaker Release Report — Summary").font = title_font
    row += 1
    ws.cell(row=row, column=1,
            value=f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}").font = data_font
    row += 1
    ws.cell(row=row, column=1,
            value=f"Total releases tracked: {len(sneakers)}").font = data_font
    row += 2

    # By brand
    ws.cell(row=row, column=1, value="Releases by Brand").font = section_font
    row += 1
    brand_counts: dict[str, int] = {}
    for s in sneakers:
        brand_counts[s["brand"]] = brand_counts.get(s["brand"], 0) + 1
    for brand in sorted(brand_counts, key=brand_counts.__getitem__, reverse=True):
        ws.cell(row=row, column=1, value=brand).font = data_font
        ws.cell(row=row, column=2, value=brand_counts[brand]).font = data_font
        row += 1
    row += 1

    # By hype
    ws.cell(row=row, column=1, value="Releases by Hype Level").font = section_font
    row += 1
    hype_counts = {"EXTREME": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for s in sneakers:
        level = s.get("hype_level", "LOW")
        hype_counts[level] = hype_counts.get(level, 0) + 1
    for level in ["EXTREME", "HIGH", "MEDIUM", "LOW"]:
        display, color = HYPE_DISPLAY.get(level, (level, "000000"))
        c = ws.cell(row=row, column=1, value=display)
        c.font = Font(name="Calibri", size=11, bold=True, color=color)
        ws.cell(row=row, column=2, value=hype_counts[level]).font = data_font
        row += 1

    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 10


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def export_to_excel(sneakers: list[dict], output_path: str):
    """
    Export sneaker data to a formatted Excel workbook.

    Args:
        sneakers:    List of normalised sneaker dicts sorted by release date.
        output_path: Destination .xlsx file path.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    wb = Workbook()
    month = _month_label(sneakers)

    _create_releases_sheet(wb, sneakers, month, "All Releases")

    high_hype = [s for s in sneakers if s.get("hype_level") in ("HIGH", "EXTREME")]
    _create_releases_sheet(wb, high_hype, month, "High Hype Alerts")

    _create_summary_sheet(wb, sneakers)

    wb.save(output_path)
