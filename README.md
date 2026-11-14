
# InvoiceIQ
### AI-Powered Invoice Processing & Accounting Automation

InvoiceIQ is a Python-based accounting automation application that extracts financial information from PDF invoices, validates accounting calculations, identifies potential duplicate invoices, and generates formatted Excel reports.

Built to demonstrate the application of accounting principles, Python programming, and artificial intelligence to financial data processing.

## Features

- AI-powered invoice data extraction
- PDF invoice processing
- Automated subtotal and total reconciliation
- Duplicate invoice detection
- Accounting exception identification
- Interactive Streamlit dashboard
- Four-sheet Excel report generation
- Session-state caching to reduce unnecessary API requests

## Technologies

- Python
- Streamlit
- OpenAI API
- PyMuPDF
- OpenPyXL
- Git and GitHub

## Accounting Validation

InvoiceIQ checks:

1. Required invoice information
2. Line-item totals against reported subtotals
3. Subtotal plus tax against reported totals
4. Potential duplicate vendor and invoice-number combinations

Invoices with identified exceptions are flagged for manual review.

## Excel Reporting

The application generates four worksheets:

1. Invoice Summary
2. Line Items
3. Expense Analysis
4. Exceptions Report

Expense Analysis includes only invoices that pass automated validation.

## Reliability Testing

InvoiceIQ successfully passed 18 automated tests covering accounting validation, duplicate detection, and PDF extraction behavior.

Additional regression testing verified the Streamlit dashboard, Excel reporting, and cached extraction reuse.

## Installation

Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file containing:

```env
OPENAI_API_KEY=your_api_key_here
```

Run the application:

```bash
streamlit run app.py
```

An OpenAI API key with available credits is required for new AI extraction requests.

## Disclaimer

InvoiceIQ is an educational accounting automation project.

Extracted information should be reviewed before being used for financial reporting or payment processing.

All demonstration invoices contain fictional data.

## Project Status

Functional prototype — tested with fictional invoices.

## Author

Ibrahim Abbas

Accounting Student | Whitworth University
