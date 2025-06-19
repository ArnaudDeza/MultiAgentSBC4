import ollama
from pydantic import BaseModel
from typing import List

class Item(BaseModel):
    name: str
    quantity: int
    price: float

class Invoice(BaseModel):
    # TODO: Define the fields for the Invoice model based on the required extractions.
    # The fields should include invoice_number, date, vendor_name, a list of items, and total.
    # Ensure you use the correct data types (e.g., str, List[Item], float).
    pass

def extract_invoice_data(image_path: str) -> dict:
    """
    Extracts invoice data from an image using an Ollama vision model.

    Args:
        image_path (str): The path to the invoice image.

    Returns:
        dict: The extracted invoice data as a dictionary.
    """
    # TODO: Implement the call to the Ollama chat API.
    # 1. Use the 'llama3.2-vision' model.
    # 2. Construct the messages payload, including the user role, a descriptive content prompt,
    #    and the image path. The prompt should guide the model to extract specific fields:
    #    Invoice Number, Date, Vendor Name, and a list of Items (with name, quantity, and price).
    # 3. Request JSON as the output format.
    # 4. Set temperature to 0 for deterministic results.
    # 5. Return the content of the message from the response.

    # Placeholder: Replace with the actual API call.
    res = {
        "message": {
            "content": "{'invoice_number': 'N/A', 'date': 'N/A', 'vendor_name': 'N/A', 'items': [], 'total': 0.0}"
        }
    }
    return res['message']['content'] 