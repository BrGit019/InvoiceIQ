
from decimal import Decimal
from types import SimpleNamespace

from accounting_validator import (
    validate_invoice,
    detect_duplicates
)


# ==========================================
# CREATE FICTIONAL TEST INVOICES
# ==========================================

def make_invoice(
    vendor="NORTHWEST OFFICE SUPPLIES",
    number="INV-2026-001",
    date="2026-11-14",
    amounts=None,
    subtotal="125",
    tax="10",
    total="135"
):
    if amounts is None:
        amounts = ["45", "80"]

    line_items = [
        SimpleNamespace(amount=Decimal(amount))
        for amount in amounts
    ]

    return SimpleNamespace(
        vendor=vendor,
        invoice_number=number,
        invoice_date=date,
        line_items=line_items,
        subtotal=(
            Decimal(subtotal)
            if subtotal is not None else None
        ),
        tax=(
            Decimal(tax)
            if tax is not None else None
        ),
        total=(
            Decimal(total)
            if total is not None else None
        )
    )


def run_test(name, condition):
    if condition:
        print(f"PASS: {name}")
        return True

    print(f"FAIL: {name}")
    return False


results = []


# ==========================================
# TEST 1: CORRECT INVOICE
# ==========================================

invoice = make_invoice()

errors = validate_invoice(invoice)

results.append(
    run_test(
        "Correct invoice passes validation",
        len(errors) == 0
    )
)


# ==========================================
# TEST 2: INCORRECT SUBTOTAL
# ==========================================

invoice = make_invoice(subtotal="140")

errors = validate_invoice(invoice)

results.append(
    run_test(
        "Incorrect subtotal detected",
        any(
            "Line items do not match subtotal" in e
            for e in errors
        )
    )
)


# ==========================================
# TEST 3: INCORRECT TOTAL
# ==========================================

invoice = make_invoice(total="225")

errors = validate_invoice(invoice)

results.append(
    run_test(
        "Incorrect total detected",
        any(
            "Invoice total does not reconcile" in e
            for e in errors
        )
    )
)


# ==========================================
# TEST 4: MISSING VENDOR
# ==========================================

invoice = make_invoice(vendor="")

errors = validate_invoice(invoice)

results.append(
    run_test(
        "Missing vendor detected",
        "Missing vendor name." in errors
    )
)


# ==========================================
# TEST 5: MISSING INVOICE NUMBER
# ==========================================

invoice = make_invoice(number="")

errors = validate_invoice(invoice)

results.append(
    run_test(
        "Missing invoice number detected",
        "Missing invoice number." in errors
    )
)


# ==========================================
# TEST 6: MISSING DATE
# ==========================================

invoice = make_invoice(date="")

errors = validate_invoice(invoice)

results.append(
    run_test(
        "Missing invoice date detected",
        "Missing invoice date." in errors
    )
)


# ==========================================
# TEST 7: MISSING SUBTOTAL
# ==========================================

invoice = make_invoice(subtotal=None)

errors = validate_invoice(invoice)

results.append(
    run_test(
        "Missing subtotal detected",
        "Missing subtotal." in errors
    )
)


# ==========================================
# TEST 8: MISSING TAX
# ==========================================

invoice = make_invoice(tax=None)

errors = validate_invoice(invoice)

results.append(
    run_test(
        "Missing tax detected",
        "Missing subtotal, tax, or total." in errors
    )
)


# ==========================================
# TEST 9: NO LINE ITEMS
# ==========================================

invoice = make_invoice(amounts=[])

errors = validate_invoice(invoice)

results.append(
    run_test(
        "Missing line items detected",
        any(
            "No line items available" in e
            for e in errors
        )
    )
)


# ==========================================
# TEST 10: DUPLICATE INVOICE
# ==========================================

invoice_a = make_invoice()
invoice_b = make_invoice()

records = [
    {
        "filename": "Duplicate_A.pdf",
        "invoice": invoice_a,
        "errors": []
    },
    {
        "filename": "Duplicate_B.pdf",
        "invoice": invoice_b,
        "errors": []
    }
]

checked = detect_duplicates(records)

results.append(
    run_test(
        "Duplicate invoice detected",
        len(checked[0]["errors"]) == 0
        and any(
            "Potential duplicate invoice" in e
            for e in checked[1]["errors"]
        )
    )
)


# ==========================================
# TEST 11: DUPLICATE NORMALIZATION
# ==========================================

invoice_a = make_invoice(
    vendor="Northwest Office Supplies",
    number="INV-2026-001"
)

invoice_b = make_invoice(
    vendor="  NORTHWEST OFFICE SUPPLIES  ",
    number=" inv-2026-001 "
)

records = [
    {
        "filename": "A.pdf",
        "invoice": invoice_a,
        "errors": []
    },
    {
        "filename": "B.pdf",
        "invoice": invoice_b,
        "errors": []
    }
]

checked = detect_duplicates(records)

results.append(
    run_test(
        "Duplicate detection ignores case and spaces",
        any(
            "Potential duplicate invoice" in e
            for e in checked[1]["errors"]
        )
    )
)


# ==========================================
# TEST 12: SMALL ROUNDING DIFFERENCE
# ==========================================

invoice = make_invoice(
    amounts=["45.00", "80.00"],
    subtotal="125.01",
    tax="10.00",
    total="135.01"
)

errors = validate_invoice(invoice)

results.append(
    run_test(
        "One-cent rounding tolerance accepted",
        len(errors) == 0
    )
)


# ==========================================
# TEST 13: DIFFERENT VENDORS
# ==========================================

records = [
    {
        "filename": "Vendor_A.pdf",
        "invoice": make_invoice(
            vendor="Vendor A",
            number="INV-001"
        ),
        "errors": []
    },
    {
        "filename": "Vendor_B.pdf",
        "invoice": make_invoice(
            vendor="Vendor B",
            number="INV-001"
        ),
        "errors": []
    }
]

checked = detect_duplicates(records)

results.append(
    run_test(
        "Same invoice number, different vendors",
        all(not r["errors"] for r in checked)
    )
)


# ==========================================
# TEST 14: DIFFERENT INVOICE NUMBERS
# ==========================================

records = [
    {
        "filename": "Invoice_A.pdf",
        "invoice": make_invoice(
            vendor="Vendor A",
            number="INV-001"
        ),
        "errors": []
    },
    {
        "filename": "Invoice_B.pdf",
        "invoice": make_invoice(
            vendor="Vendor A",
            number="INV-002"
        ),
        "errors": []
    }
]

checked = detect_duplicates(records)

results.append(
    run_test(
        "Same vendor, different invoice numbers",
        all(not r["errors"] for r in checked)
    )
)


# ==========================================
# TEST 15: REPEATED DUPLICATE CHECK
# ==========================================

records = [
    {
        "filename": "Duplicate_A.pdf",
        "invoice": make_invoice(),
        "errors": []
    },
    {
        "filename": "Duplicate_B.pdf",
        "invoice": make_invoice(),
        "errors": []
    }
]

first_check = detect_duplicates(records)

# Simulate how app.py rebuilds clean records
# before running duplicate detection again.
fresh_records = [
    {
        **record,
        "errors": []
    }
    for record in records
]

second_check = detect_duplicates(fresh_records)

results.append(
    run_test(
        "Repeated checks produce consistent results",
        [r["errors"] for r in first_check]
        == [r["errors"] for r in second_check]
    )
)

# ==========================================
# FINAL RESULTS
# ==========================================

print("\n" + "=" * 45)

passed = sum(results)
total = len(results)

print(f"TEST RESULTS: {passed}/{total} PASSED")

if passed == total:
    print("ALL TESTS PASSED!")
else:
    print("Some tests failed. Review the results above.")
    raise SystemExit(1)
