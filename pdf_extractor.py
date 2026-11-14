
import fitz


def extract_pdf_text(pdf_bytes):
    """
    Extract text from an uploaded PDF file.
    """

    extracted_text = ""

    with fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    ) as document:

        for page in document:
            page_text = page.get_text("text")
            extracted_text += page_text + "\n"

    return extracted_text
