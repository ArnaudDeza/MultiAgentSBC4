import ollama
from pydantic import BaseModel
from typing import List

class Item(BaseModel):
    name: str
    quantity: int
    price: float

class Invoice(BaseModel):
    invoice_number: str
    date: str
    vendor_name: str
    items: List[Item]
    total: float

def extract_invoice_data(image_path: str) -> dict:
    """
    Extracts invoice data from an image using an Ollama vision model.

    Args:
        image_path (str): The path to the invoice image.

    Returns:
        dict: The extracted invoice data as a dictionary.
    """
    res = ollama.chat(
        model="llama3.2-vision",
        messages=[
            {
                'role': 'user',
                'content': """Given an invoice image, Your task is to use OCR to detect and extract text, categorize it into predefined fields.
                Invoice/Receipt Number: The unique identifier of the document.
                Date: The issue or transaction date.
                Vendor Name: The business or entity issuing the document.
                Items: A list of purchased products or services with Name, Quantity and price.""",
                'images': [image_path]
            }
        ],
        format="json",
        options={'temperature': 0}
    )
    return res['message']['content'] 