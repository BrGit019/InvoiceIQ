
from ai_extractor import extract_invoice_data

sample_invoice = """
NORTHWEST OFFICE SUPPLIES
INVOICE: INV-2026-001
DATE: November 14, 2026

Printer paper: $45.00
Ink cartridges: $80.00

Subtotal: $125.00
Sales tax (8%): $10.00
TOTAL: $135.00
"""

print("Sending invoice to AI...")

invoice = extract_invoice_data(sample_invoice)

print(invoice.model_dump_json(indent=2))
