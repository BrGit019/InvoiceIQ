# InvoiceIQ
### AI-Powered Invoice Processing & Accounting Automation

**[Live Demo](https://invoiceiq-jhszwqdancybhilnyjcjew.streamlit.app/)** | **[GitHub Repository](https://github.com/BrGit019/InvoiceIQ)**

InvoiceIQ is a Python-based accounting automation application that processes PDF invoices, extracts structured financial information using artificial intelligence, validates accounting calculations, detects potential duplicate invoices, and generates professional Excel reports.

The project demonstrates how accounting principles, programming, and artificial intelligence can be combined to improve financial data processing, identify discrepancies, and support internal accounting controls.

## Live Interactive Demo

**Try InvoiceIQ:** https://invoiceiq-jhszwqdancybhilnyjcjew.streamlit.app/

The publicly deployed application uses five fictional invoices to demonstrate the accounting validation and reporting workflow without requiring an OpenAI API key.

Visitors can:

- Explore invoice information and individual line items.
- Review automated accounting validation results.
- Identify duplicate invoices and financial discrepancies.
- View an interactive accounting dashboard.
- Download a professionally formatted Excel accounting report.

The public demo does not perform live AI extraction or require paid API requests.

## Key Features

**AI-Powered Invoice Extraction**
- Extracts structured accounting data from PDF invoices using the OpenAI API.
- Identifies vendors, invoice numbers, dates, expense categories, subtotals, taxes, totals, and line items.
- Uses session-state caching to avoid unnecessary repeat API requests.

**Automated Accounting Validation**
- Verifies required invoice information.
- Reconciles individual line items against reported subtotals.
- Checks subtotal and tax calculations against reported invoice totals.
- Flags potential duplicate invoices based on vendor and invoice-number combinations.

**Interactive Accounting Dashboard**
- Displays total invoices processed.
- Tracks invoices passing automated validation.
- Identifies invoices requiring manual review.
- Calculates approved expenses, excluding invoices with identified exceptions.

**Professional Excel Reporting**

Generates four formatted worksheets:

1. Invoice Summary
2. Line Items
3. Expense Analysis
4. Exceptions Report

Reports include formatted financial values, organized invoice records, and highlighted accounting exceptions.

## Accounting Controls

InvoiceIQ implements automated checks designed to identify common invoice-processing errors.

| Accounting Control | Purpose |
|---|---|
| Required Information | Identifies missing invoice details |
| Subtotal Reconciliation | Compares line-item amounts with reported subtotals |
| Total Reconciliation | Verifies subtotal plus tax equals the reported total |
| Duplicate Detection | Flags repeated vendor and invoice-number combinations |
| Exception Reporting | Separates invoices requiring manual review |
| Expense Approval Filtering | Excludes flagged invoices from approved expense totals |

Automated validation supports accounting review but does not replace professional judgment or manual verification.

## Reliability Testing

InvoiceIQ passed 18 automated tests covering accounting validation, duplicate detection, and PDF extraction reliability.

Additional testing verified:

- Consistent accounting validation results.
- Duplicate detection across invoices.
- PDF extraction error handling.
- Session-state extraction caching.
- Interactive dashboard functionality.
- Four-