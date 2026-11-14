
from io import BytesIO
from collections import defaultdict
from decimal import Decimal
from datetime import datetime, date

from openpyxl import Workbook
from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment,
    Border,
    Side
)
from openpyxl.utils import get_column_letter


# =====================================
# REPORT COLORS AND FORMATS
# =====================================

NAVY = "17365D"
BLUE = "24476B"
WHITE = "FFFFFF"
LIGHT_BLUE = "EAF2F8"
LIGHT_GRAY = "F4F6F8"
GREEN_BG = "E2F0D9"
GREEN_TEXT = "006100"
RED_BG = "FCE4D6"
RED_TEXT = "9C0006"
GRAY_TEXT = "596579"

CURRENCY_FORMAT = '"$"#,##0.00;[Red]("$"#,##0.00)'
DATE_FORMAT = "yyyy-mm-dd"


def money(value):
    """Convert monetary values for Excel."""
    if value is None:
        return None
    return float(Decimal(str(value)))


def format_date(value):
    """Preserve valid Excel dates."""
    if isinstance(value, (date, datetime)):
        return value

    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return value

    return value


def style_worksheet(ws, currency_columns=None,
                    date_columns=None):
    """Apply professional formatting to a worksheet."""

    currency_columns = currency_columns or []
    date_columns = date_columns or []

    ws.sheet_view.showGridLines = False
    ws.freeze_panes = "A2"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.sheet_properties.tabColor = NAVY

    # Header formatting
    for cell in ws[1]:
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor=NAVY
        )
        cell.font = Font(
            name="Aptos",
            size=11,
            bold=True,
            color=WHITE
        )
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True
        )

    ws.row_dimensions[1].height = 32

    # Body formatting
    for row_index in range(2, ws.max_row + 1):
        ws.row_dimensions[row_index].height = 27

        for cell in ws[row_index]:
            cell.font = Font(
                name="Aptos",
                size=10,
                color=NAVY
            )

            cell.alignment = Alignment(
                vertical="center",
                wrap_text=True
            )

            if row_index % 2 == 0:
                cell.fill = PatternFill(
                    fill_type="solid",
                    fgColor=LIGHT_BLUE
                )
            else:
                cell.fill = PatternFill(
                    fill_type="solid",
                    fgColor=WHITE
                )

    # Apply currency formatting
    for column in currency_columns:
        for row_index in range(2, ws.max_row + 1):
            cell = ws.cell(row_index, column)
            cell.number_format = CURRENCY_FORMAT
            cell.alignment = Alignment(
                horizontal="right",
                vertical="center"
            )

    # Apply date formatting
    for column in date_columns:
        for row_index in range(2, ws.max_row + 1):
            cell = ws.cell(row_index, column)
            cell.number_format = DATE_FORMAT

    # Adjust column widths
    for column in ws.columns:
        letter = get_column_letter(column[0].column)

        longest = max(
            len(str(cell.value or ""))
            for cell in column
        )

        width = min(max(longest + 5, 18), 55)

        ws.column_dimensions[letter].width = width

    # Enable Excel filtering
    ws.auto_filter.ref = ws.dimensions

    # Print settings
    ws.print_options.horizontalCentered = True
    ws.print_title_rows = "1:1"


def create_excel_report(records):
    """
    Generate a professional accounting workbook.

    records contains dictionaries with:
    filename, invoice, and errors.
    """

    wb = Workbook()

    summary = wb.active
    summary.title = "Invoice Summary"

    line_items = wb.create_sheet("Line Items")
    analysis = wb.create_sheet("Expense Analysis")
    exceptions = wb.create_sheet("Exceptions Report")

    # =====================================
    # SHEET 1: INVOICE SUMMARY
    # =====================================

    summary.append([
        "Filename",
        "Vendor",
        "Invoice Number",
        "Date",
        "Category",
        "Subtotal",
        "Tax",
        "Total",
        "Validation Status"
    ])

    # =====================================
    # SHEET 2: LINE ITEMS
    # =====================================

    line_items.append([
        "Filename",
        "Invoice Number",
        "Vendor",
        "Description",
        "Amount"
    ])

    # =====================================
    # SHEET 4: EXCEPTIONS
    # =====================================

    exceptions.append([
        "Filename",
        "Invoice Number",
        "Vendor",
        "Issue"
    ])

    category_totals = defaultdict(
        lambda: Decimal("0")
    )

    # =====================================
    # PROCESS INVOICES
    # =====================================

    for record in records:

        invoice = record["invoice"]
        errors = record["errors"]
        filename = record["filename"]

        status = (
            "Review Required"
            if errors else "Passed"
        )

        summary.append([
            filename,
            invoice.vendor,
            invoice.invoice_number,
            format_date(invoice.invoice_date),
            invoice.category,
            money(invoice.subtotal),
            money(invoice.tax),
            money(invoice.total),
            status
        ])

        # Individual line items
        for item in invoice.line_items:

            line_items.append([
                filename,
                invoice.invoice_number,
                invoice.vendor,
                item.description,
                money(item.amount)
            ])

        # Only validated invoices enter
        # the approved expense analysis
        if not errors and invoice.total is not None:

            category = (
                invoice.category or "Uncategorized"
            )

            category_totals[category] += Decimal(
                str(invoice.total)
            )

        # Record validation exceptions
        for error in errors:

            exceptions.append([
                filename,
                invoice.invoice_number,
                invoice.vendor,
                error
            ])

    # =====================================
    # SHEET 3: EXPENSE ANALYSIS
    # =====================================

    analysis.append([
        "Expense Category",
        "Total Amount"
    ])

    for category, total in sorted(
        category_totals.items()
    ):
        analysis.append([
            category,
            money(total)
        ])

    # =====================================
    # APPLY FORMATTING
    # =====================================

    style_worksheet(
        summary,
        currency_columns=[6, 7, 8],
        date_columns=[4]
    )

    style_worksheet(
        line_items,
        currency_columns=[5]
    )

    style_worksheet(
        analysis,
        currency_columns=[2]
    )

    style_worksheet(exceptions)

    # =====================================
    # VALIDATION STATUS COLORS
    # =====================================

    for row in summary.iter_rows(min_row=2):

        status_cell = row[8]

        if status_cell.value == "Passed":

            status_cell.fill = PatternFill(
                fill_type="solid",
                fgColor=GREEN_BG
            )

            status_cell.font = Font(
                bold=True,
                color=GREEN_TEXT
            )

        else:

            status_cell.fill = PatternFill(
                fill_type="solid",
                fgColor=RED_BG
            )

            status_cell.font = Font(
                bold=True,
                color=RED_TEXT
            )

    # =====================================
    # EXCEPTION HIGHLIGHTING
    # =====================================

    exceptions.sheet_properties.tabColor = RED_TEXT
    analysis.sheet_properties.tabColor = GREEN_TEXT

    for row in exceptions.iter_rows(min_row=2):

        for cell in row:

            cell.fill = PatternFill(
                fill_type="solid",
                fgColor=RED_BG
            )

            cell.font = Font(
                name="Aptos",
                size=10,
                color=RED_TEXT
            )

    # Wider issue descriptions
    exceptions.column_dimensions["D"].width = 65
    summary.column_dimensions["A"].width = 42
    summary.column_dimensions["B"].width = 32
    summary.column_dimensions["C"].width = 23
    summary.column_dimensions["I"].width = 22

    line_items.column_dimensions["A"].width = 42
    line_items.column_dimensions["C"].width = 32
    line_items.column_dimensions["D"].width = 35

    # =====================================
    # EXPORT WORKBOOK
    # =====================================

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output.getvalue()
