
from datetime import date
from typing import Optional
from decimal import Decimal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

# Define what each invoice should contain
class LineItem(BaseModel):
    description: str
    amount: Decimal


class Invoice(BaseModel):
    vendor: Optional[str]
    invoice_number: Optional[str]
    invoice_date: Optional[date]
    line_items: list[LineItem]
    subtotal: Optional[Decimal]
    tax: Optional[Decimal]
    total: Optional[Decimal]
    category: Optional[str]


def extract_invoice_data(invoice_text):
    client = OpenAI()

    response = client.responses.parse(
        model="gpt-4.1-mini",
        instructions=(
            "You extract accounting data from invoices. "
            "Use only information found in the document. "
            "Never invent missing values. "
            "Use null for missing fields. "
            "Categorize expenses using a reasonable "
            "business expense category."
        ),
        input=invoice_text,
        text_format=Invoice,
        store=False,
    )

    if response.output_parsed is None:
        raise ValueError("No structured invoice data returned.")

    return response.output_parsed
