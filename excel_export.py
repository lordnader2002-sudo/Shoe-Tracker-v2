"""
Excel export module for sneaker release reports.
Creates a professionally formatted .xlsx workbook with multiple sheets.
"""

import os
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side, numbers
from openpyxl.utils import get_column_letter


# ---------------------------------------------------------------------------
# Style constants
# ---------------------------------------------------------------------------

HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="2F2F2F", end_color="2F2F2F", fill_type="solid")
HEADER_ALIGNMENT = Alignment(horizontal="center", vertical="center", wrap_text=True)

URGENT_FILL = PatternFill(start_color="FFD6D6", end_color="FFD6D6", fill_type="solid")  # Light red
UPCOMING_FILL = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")  # Light yellow
NORMAL_FILL = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")  # White

HYPE_EXTREME_FILL = PatternFill(start_color="FF4444", end_color="FF4444", fill_type="solid")  # Red
HYPE_HIGH_FILL = PatternFill(start_color="FF8800", end_color="FF8800", fill_type="solid")  # Orange
HYPE_EXTREME_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
HYPE_HIGH_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")

THIN_BORDER = Border(
    left=Side(style="thin", color="CCCCCC"),
    right=Side(style="thin", color="CCCCCC"),
    top=Side(style="thin", color="CCCCCC"),
    bottom=Side(style="thin", color="CCCCCC"),
)

DATA_ALIGNMENT = Alignment(vertical="center", wrap_text=False)
CENTER_ALIGNMENT = Alignment(horizontal="center", vertical="center")

# Column definitions: (header, key, width, format)
COLUMNS = [
    ("Release Date", "release_date", 14, "date"),
    ("Days Out", "days_until_release", 10, "int"),
    ("Brand", "brand", 14, None),
    ("Shoe Name", "name", 40, None),
    ("Colorway", "colorway", 25, None),
    ("Style Code", "style_code", 16, None),
    ("Retail Price", "retail_price", 14, "currency"),
    ("Est. Market Value", "estimated_market_value", 18, "currency"),
    ("Hype Score", "hype_score", 12, "int"),
    ("Hype Level", "hype_level", 13, None),
]


def _apply_header_style(ws, num_cols: int):
    """Apply header styling to the first row."""
    for col_idx in range(1, num_cols + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = HEADER_ALIGNMENT
        cell.border = THIN_BORDER


def _get_row_fill(sneaker: dict) -> PatternFill:
    """Determine the background fill based on days until release."""
    days = sneaker.get("days_until_release", 999)
    if days <= 7:
        return URGENT_FILL
    elif days <= 14:
        return UPCOMING_FILL
    return NORMAL_FILL


def _write_sneaker_row(ws, row_num: int, sneaker: dict):
    """Write a single sneaker row with formatting."""
    row_fill = _get_row_fill(sneaker)

    for col_idx, (_, key, _, fmt) in enumerate(COLUMNS, start=1):
        cell = ws.cell(row=row_num, column=col_idx)
        value = sneaker.get(key)

        if fmt == "date" and isinstance(value, datetime):
            cell.value = value.date()
            cell.number_format = "MM/DD/YYYY"
            cell.alignment = CENTER_ALIGNMENT
        elif fmt == "currency":
            cell.value = value
            cell.number_format = "$#,##0.00" if value is not None else ""
            cell.alignment = CENTER_ALIGNMENT
        elif fmt == "int":
            cell.value = value
            cell.alignment = CENTER_ALIGNMENT
        else:
            cell.value = value if value else "N/A"
            cell.alignment = DATA_ALIGNMENT

        cell.border = THIN_BORDER
        cell.fill = row_fill

        # Special styling for hype level cell
        if key == "hype_level":
            level = sneaker.get("hype_level", "")
            if level == "EXTREME":
                cell.fill = HYPE_EXTREME_FILL
                cell.font = HYPE_EXTREME_FONT
            elif level == "HIGH":
                cell.fill = HYPE_HIGH_FILL
                cell.font = HYPE_HIGH_FONT

        # Special styling for hype score cell
        if key == "hype_score":
            score = sneaker.get("hype_score", 0)
            if score >= 9:
                cell.fill = HYPE_EXTREME_FILL
                cell.font = HYPE_EXTREME_FONT
            elif score >= 7:
                cell.fill = HYPE_HIGH_FILL
                cell.font = HYPE_HIGH_FONT


def _create_all_releases_sheet(wb: Workbook, sneakers: list[dict]):
    """Create the 'All Releases' sheet with every sneaker."""
    ws = wb.active
    ws.title = "All Releases"

    # Write headers
    for col_idx, (header, _, width, _) in enumerate(COLUMNS, start=1):
        ws.cell(row=1, column=col_idx, value=header)
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    _apply_header_style(ws, len(COLUMNS))

    # Write data
    for row_idx, sneaker in enumerate(sneakers, start=2):
        _write_sneaker_row(ws, row_idx, sneaker)

    # Freeze header row
    ws.freeze_panes = "A2"

    # Auto-filter
    if sneakers:
        last_col = get_column_letter(len(COLUMNS))
        ws.auto_filter.ref = f"A1:{last_col}{len(sneakers) + 1}"


def _create_high_hype_sheet(wb: Workbook, sneakers: list[dict]):
    """Create a sheet with only HIGH and EXTREME hype sneakers."""
    high_hype = [s for s in sneakers if s.get("hype_level") in ("HIGH", "EXTREME")]

    ws = wb.create_sheet("High Hype Alerts")

    # Write headers
    for col_idx, (header, _, width, _) in enumerate(COLUMNS, start=1):
        ws.cell(row=1, column=col_idx, value=header)
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    _apply_header_style(ws, len(COLUMNS))

    if not high_hype:
        ws.cell(row=2, column=1, value="No high-hype releases in the next 30 days.")
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(COLUMNS))
        ws.cell(row=2, column=1).alignment = CENTER_ALIGNMENT
        ws.cell(row=2, column=1).font = Font(name="Calibri", size=12, italic=True)
    else:
        for row_idx, sneaker in enumerate(high_hype, start=2):
            _write_sneaker_row(ws, row_idx, sneaker)

    ws.freeze_panes = "A2"


def _create_summary_sheet(wb: Workbook, sneakers: list[dict]):
    """Create a summary sheet with counts by brand, urgency, and hype."""
    ws = wb.create_sheet("Summary")

    title_font = Font(name="Calibri", size=14, bold=True)
    section_font = Font(name="Calibri", size=12, bold=True)
    data_font = Font(name="Calibri", size=11)

    row = 1
    ws.cell(row=row, column=1, value="Sneaker Release Report Summary").font = title_font
    ws.cell(row=row, column=3, value=f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}").font = data_font
    row += 1
    ws.cell(row=row, column=1, value=f"Total releases tracked: {len(sneakers)}").font = data_font
    row += 2

    # --- Releases by Brand ---
    ws.cell(row=row, column=1, value="Releases by Brand").font = section_font
    row += 1
    brand_counts: dict[str, int] = {}
    for s in sneakers:
        brand_counts[s["brand"]] = brand_counts.get(s["brand"], 0) + 1
    for brand in sorted(brand_counts, key=brand_counts.get, reverse=True):
        ws.cell(row=row, column=1, value=brand).font = data_font
        ws.cell(row=row, column=2, value=brand_counts[brand]).font = data_font
        row += 1
    row += 1

    # --- Releases by Urgency ---
    ws.cell(row=row, column=1, value="Releases by Urgency").font = section_font
    row += 1
    urgent = sum(1 for s in sneakers if s["days_until_release"] <= 7)
    upcoming = sum(1 for s in sneakers if 7 < s["days_until_release"] <= 14)
    later = sum(1 for s in sneakers if s["days_until_release"] > 14)
    for label, count, fill in [
        ("URGENT (within 7 days)", urgent, URGENT_FILL),
        ("UPCOMING (8-14 days)", upcoming, UPCOMING_FILL),
        ("LATER (15-30 days)", later, NORMAL_FILL),
    ]:
        ws.cell(row=row, column=1, value=label).font = data_font
        ws.cell(row=row, column=2, value=count).font = data_font
        ws.cell(row=row, column=1).fill = fill
        ws.cell(row=row, column=2).fill = fill
        row += 1
    row += 1

    # --- Releases by Hype Level ---
    ws.cell(row=row, column=1, value="Releases by Hype Level").font = section_font
    row += 1
    hype_counts = {"EXTREME": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for s in sneakers:
        level = s.get("hype_level", "LOW")
        hype_counts[level] = hype_counts.get(level, 0) + 1
    for level in ["EXTREME", "HIGH", "MEDIUM", "LOW"]:
        ws.cell(row=row, column=1, value=level).font = data_font
        ws.cell(row=row, column=2, value=hype_counts[level]).font = data_font
        if level == "EXTREME":
            ws.cell(row=row, column=1).fill = HYPE_EXTREME_FILL
            ws.cell(row=row, column=1).font = HYPE_EXTREME_FONT
        elif level == "HIGH":
            ws.cell(row=row, column=1).fill = HYPE_HIGH_FILL
            ws.cell(row=row, column=1).font = HYPE_HIGH_FONT
        row += 1

    # Set column widths
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 30


def export_to_excel(sneakers: list[dict], output_path: str):
    """
    Export sneaker data to a formatted Excel workbook.

    Args:
        sneakers: List of normalized sneaker dicts (already sorted by release date).
        output_path: File path for the .xlsx output.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    wb = Workbook()

    _create_all_releases_sheet(wb, sneakers)
    _create_high_hype_sheet(wb, sneakers)
    _create_summary_sheet(wb, sneakers)

    wb.save(output_path)
