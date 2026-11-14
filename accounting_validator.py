
from decimal import Decimal


def validate_invoice(invoice):
    """
    Validate extracted invoice accounting data.
    """

    errors = []

    # CHECK 1: Required information
    if not invoice.vendor:
        errors.append("Missing vendor name.")

    if not invoice.invoice_number:
        errors.append("Missing invoice number.")

    if not invoice.invoice_date:
        errors.append("Missing invoice date.")

    # CHECK 2: Line items equal subtotal
    if invoice.subtotal is not None:

        if invoice.line_items:
            calculated_subtotal = sum(
                (item.amount for item in invoice.line_items),
                Decimal("0")
            )

            difference = abs(
                calculated_subtotal - invoice.subtotal
            )

            if difference > Decimal("0.01"):
                errors.append(
                    "Line items do not match subtotal. "
                    f"Calculated: ${calculated_subtotal}, "
                    f"Reported: ${invoice.subtotal}"
                )
        else:
            errors.append(
                "No line items available to verify subtotal."
            )
    else:
        errors.append("Missing subtotal.")

    # CHECK 3: Subtotal + tax = total
    if (
        invoice.subtotal is not None
        and invoice.tax is not None
        and invoice.total is not None
    ):

        calculated_total = invoice.subtotal + invoice.tax

        difference = abs(
            calculated_total - invoice.total
        )

        if difference > Decimal("0.01"):
            errors.append(
                "Invoice total does not reconcile. "
                f"Calculated: ${calculated_total}, "
                f"Reported: ${invoice.total}"
            )

    else:
        errors.append(
            "Missing subtotal, tax, or total."
        )

    return errors

def detect_duplicates(records):
    seen = set()
    checked_records = []

    for record in records:
        invoice = record["invoice"]
        errors = list(record["errors"])

        vendor = (invoice.vendor or "").strip().casefold()
        number = (
            (invoice.invoice_number or "")
            .strip()
            .casefold()
        )

        if vendor and number:
            key = (vendor, number)

            if key in seen:
                errors.append(
                    "Potential duplicate invoice: "
                    f"{invoice.vendor} / "
                    f"{invoice.invoice_number}"
                )
            else:
                seen.add(key)

        checked_records.append({
            **record,
            "errors": errors
        })

    return checked_records
