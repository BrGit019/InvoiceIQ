
from io import BytesIO

import fitz

from pdf_extractor import extract_pdf_text


def create_pdf(text):
    document = fitz.open()
    page = document.new_page()

    if text:
        page.insert_text((72, 72), text)

    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def run_test(name, condition):
    if condition:
        print(f"PASS: {name}")
        return True

    print(f"FAIL: {name}")
    return False


results = []


# TEST 1: EMPTY PDF
empty_pdf = create_pdf("")

try:
    text = extract_pdf_text(empty_pdf)
    results.append(
        run_test(
            "Empty PDF returns no text",
            not text.strip()
        )
    )
except Exception as error:
    print(f"FAIL: Empty PDF - {error}")
    results.append(False)


# TEST 2: CORRUPTED PDF
corrupted_pdf = b"This is not a real PDF file."

try:
    text = extract_pdf_text(corrupted_pdf)

    results.append(
        run_test(
            "Corrupted PDF handled safely",
            not text.strip()
        )
    )

except Exception:
    # A controlled exception is acceptable:
    # app.py catches processing exceptions.
    results.append(
        run_test(
            "Corrupted PDF handled safely",
            True
        )
    )


# TEST 3: UNRELATED TEXT
unrelated_pdf = create_pdf(
    "Hello! This is a test document, not an invoice."
)

try:
    text = extract_pdf_text(unrelated_pdf)

    results.append(
        run_test(
            "Unrelated PDF text extracted",
            "not an invoice" in text.lower()
        )
    )

except Exception as error:
    print(f"FAIL: Unrelated PDF - {error}")
    results.append(False)


# FINAL RESULTS
print("\n" + "=" * 40)

passed = sum(results)
total = len(results)

print(f"TEST RESULTS: {passed}/{total} PASSED")

if passed == total:
    print("ALL PDF TESTS PASSED!")
else:
    raise SystemExit(1)
