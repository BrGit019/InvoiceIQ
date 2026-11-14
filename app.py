
import hashlib
from decimal import Decimal, InvalidOperation

import streamlit as st

from pdf_extractor import extract_pdf_text
from ai_extractor import extract_invoice_data
from accounting_validator import (
    validate_invoice,
    detect_duplicates
)
from excel_exporter import create_excel_report


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="InvoiceIQ | Accounting Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================
# HELPERS
# ==========================================

def format_currency(value):
    """Format amounts as US dollars."""
    try:
        amount = Decimal(str(value))
        if not amount.is_finite():
            return "N/A"
        return f"${amount:,.2f}"
    except (InvalidOperation, ValueError, TypeError):
        return "N/A"


def get_file_hash(file_bytes):
    """Identify identical PDF files."""
    return hashlib.sha256(file_bytes).hexdigest()


# ==========================================
# SESSION STATE
# ==========================================

if "processed_invoices" not in st.session_state:
    st.session_state.processed_invoices = {}


# ==========================================
# CUSTOM STYLING
# ==========================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    h1, h2, h3 {
        letter-spacing: -0.5px;
    }

    div[data-testid="stMetric"] {
        background-color: rgba(120, 130, 150, 0.08);
        border: 1px solid rgba(130, 140, 160, 0.18);
        border-radius: 12px;
        padding: 18px;
    }

    div[data-testid="stMetricLabel"] {
        font-weight: 500;
    }

    div[data-testid="stMetricValue"] {
        font-weight: 700;
    }

    div[data-testid="stExpander"] {
        border-radius: 10px;
    }

    div.stButton > button[kind="primary"] {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# HEADER
# ==========================================

st.title("📊 InvoiceIQ")

st.subheader(
    "AI-Powered Receipt & Invoice Extractor"
)

st.caption(
    "Automated invoice extraction, accounting "
    "validation, duplicate detection, and "
    "Excel financial reporting."
)

st.divider()


# ==========================================
# UPLOAD SECTION
# ==========================================

st.header("1. Upload Invoices")

uploaded_files = st.file_uploader(
    "Choose PDF invoices",
    type=["pdf"],
    accept_multiple_files=True,
    help="Upload one or more PDF invoices."
)


if uploaded_files:

    st.success(
        f"{len(uploaded_files)} invoice(s) uploaded."
    )

    current_files = []

    for uploaded_file in uploaded_files:

        file_bytes = uploaded_file.getvalue()

        current_files.append({
            "filename": uploaded_file.name,
            "bytes": file_bytes,
            "hash": get_file_hash(file_bytes)
        })


    # ==========================================
    # PROCESS INVOICES
    # ==========================================

    st.write("### AI Extraction")

    st.caption(
        "Previously processed PDFs are reused "
        "from the current session to avoid "
        "unnecessary OpenAI API requests."
    )

    if st.button(
        "Extract Accounting Data",
        type="primary",
        icon=":material/auto_awesome:"
    ):

        progress_bar = st.progress(0)

        total_files = len(current_files)

        for index, file in enumerate(current_files):

            file_hash = file["hash"]
            filename = file["filename"]

            if file_hash in st.session_state.processed_invoices:

                st.info(
                    f"{filename}: Using saved extraction."
                )

                progress_bar.progress(
                    (index + 1) / total_files
                )

                continue

            try:

                invoice_text = extract_pdf_text(
                    file["bytes"]
                )

                if not invoice_text.strip():

                    st.warning(
                        f"{filename}: No readable PDF text."
                    )

                    progress_bar.progress(
                        (index + 1) / total_files
                    )

                    continue

                with st.spinner(
                    f"Extracting {filename}..."
                ):

                    invoice = extract_invoice_data(
                        invoice_text
                    )

                # Save only after successful extraction
                st.session_state.processed_invoices[
                    file_hash
                ] = {
                    "filename": filename,
                    "invoice": invoice
                }

                st.success(
                    f"{filename}: Extraction complete."
                )

            except Exception as error:

                st.error(
                    f"{filename}: Processing failed. "
                    f"{error}"
                )

            progress_bar.progress(
                (index + 1) / total_files
            )


    # ==========================================
    # BUILD CURRENT RESULTS
    # ==========================================

    records = []

    for file in current_files:

        saved = st.session_state.processed_invoices.get(
            file["hash"]
        )

        if saved is None:
            continue

        invoice = saved["invoice"]

        # Revalidate on every rerun without
        # making another OpenAI API request.
        errors = list(validate_invoice(invoice))

        records.append({
            "filename": file["filename"],
            "invoice": invoice,
            "errors": errors
        })


    # ==========================================
    # DUPLICATE DETECTION
    # ==========================================

    if records:

        # Use fresh records each rerun to avoid
        # accumulating duplicate warnings.
        records = detect_duplicates(records)

        # ======================================
        # DASHBOARD
        # ======================================

        st.divider()

        st.header("2. Accounting Dashboard")

        total_invoices = len(records)

        passed_invoices = sum(
            1 for record in records
            if not record["errors"]
        )

        review_invoices = (
            total_invoices - passed_invoices
        )

        approved_total = sum(
            (
                Decimal(str(record["invoice"].total))
                for record in records
                if not record["errors"]
                and record["invoice"].total is not None
            ),
            Decimal("0")
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Invoices Processed",
                total_invoices
            )

        with col2:
            st.metric(
                "Validation Passed",
                passed_invoices
            )

        with col3:
            st.metric(
                "Requires Review",
                review_invoices
            )

        with col4:
            st.metric(
                "Approved Expenses",
                format_currency(approved_total)
            )

        st.caption(
            "Approved Expenses includes only "
            "invoices that passed validation. "
            "Review-required invoices are excluded."
        )


        # ======================================
        # INVOICE RESULTS
        # ======================================

        st.divider()

        st.header("3. Processed Invoices")

        st.caption(
            "Expand an invoice to view its "
            "accounting information and exceptions."
        )

        for record in records:

            invoice = record["invoice"]
            errors = record["errors"]

            status_icon = "⚠️" if errors else "✅"

            label = (
                f"{status_icon} {record['filename']}"
            )

            with st.expander(
                label,
                expanded=False
            ):

                if errors:

                    st.warning(
                        "Review Required — "
                        "Accounting exceptions detected."
                    )

                    for error in errors:
                        st.error(str(error))

                else:

                    st.success(
                        "Passed — All accounting "
                        "checks completed successfully."
                    )

                st.write("### Invoice Information")

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        "**Vendor:**",
                        invoice.vendor
                    )

                    st.write(
                        "**Invoice Number:**",
                        invoice.invoice_number
                    )

                    st.write(
                        "**Invoice Date:**",
                        str(invoice.invoice_date)
                    )

                    st.write(
                        "**Expense Category:**",
                        invoice.category
                    )

                with col2:

                    st.write(
                        "**Subtotal:**",
                        format_currency(invoice.subtotal)
                    )

                    st.write(
                        "**Sales Tax:**",
                        format_currency(invoice.tax)
                    )

                    st.write(
                        "**Invoice Total:**",
                        format_currency(invoice.total)
                    )

                st.write("### Line Items")

                items = [
                    {
                        "Description": item.description,
                        "Amount": float(item.amount)
                    }
                    for item in invoice.line_items
                ]

                if items:

                    st.dataframe(
                        items,
                        hide_index=True,
                        use_container_width=True,
                        column_config={
                            "Description": st.column_config.TextColumn(
                                "Description"
                            ),
                            "Amount": st.column_config.NumberColumn(
                                "Amount",
                                format="$%.2f"
                            )
                        }
                    )

                else:

                    st.info(
                        "No line items were extracted."
                    )


        # ======================================
        # EXCEPTION SUMMARY
        # ======================================

        st.divider()

        st.header("4. Accounting Exceptions")

        if review_invoices == 0:

            st.success(
                "No accounting exceptions detected."
            )

        else:

            st.warning(
                f"{review_invoices} invoice(s) "
                "require manual review."
            )

            exception_rows = []

            for record in records:

                for error in record["errors"]:

                    exception_rows.append({
                        "Filename": record["filename"],
                        "Invoice Number": (
                            record["invoice"].invoice_number
                        ),
                        "Issue": str(error)
                    })

            st.dataframe(
                exception_rows,
                hide_index=True,
                use_container_width=True
            )


        # ======================================
        # EXCEL REPORT
        # ======================================

        st.divider()

        st.header("5. Export Accounting Report")

        st.write(
            "Download a formatted Excel workbook "
            "containing all processed invoices, "
            "line items, approved expense totals, "
            "and accounting exceptions."
        )

        st.caption(
            "Workbook includes four worksheets: "
            "Invoice Summary, Line Items, "
            "Expense Analysis, and Exceptions Report."
        )

        try:

            excel_data = create_excel_report(
                records
            )

            st.download_button(
                label="📥 Download Excel Report",
                data=excel_data,
                file_name="InvoiceIQ_Accounting_Report.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                type="primary",
                use_container_width=True
            )

            st.caption(
                "The Excel report is generated "
                "from saved results. Downloading "
                "does not make another OpenAI "
                "API request."
            )

        except Exception as error:

            st.error(
                f"Unable to generate Excel report: {error}"
            )

    else:

        st.info(
            "Click Extract Accounting Data "
            "to process your uploaded invoices."
        )

else:

    st.info(
        "Upload one or more PDF invoices "
        "to begin processing."
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "InvoiceIQ | AI-Assisted Accounting Automation "
    "| Human review required before financial posting."
)
