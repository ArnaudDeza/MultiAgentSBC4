import streamlit as st
import pandas as pd
import json

def display_invoice_data(invoice_data: str):
    """
    Displays the extracted invoice data in a structured format.

    Args:
        invoice_data (str): A JSON string containing the invoice data.
    """
    try:
        data = json.loads(invoice_data)
        
        st.subheader("Extracted Invoice Details")
        
        # Display main invoice details
        st.text(f"Invoice Number: {data.get('invoice_number', 'N/A')}")
        st.text(f"Date: {data.get('date', 'N/A')}")
        st.text(f"Vendor: {data.get('vendor_name', 'N/A')}")
        st.text(f"Total Amount: {data.get('total', 'N/A')}")
        
        # Display items in a table
        items = data.get('items', [])
        if items:
            st.subheader("Items")
            df = pd.DataFrame(items)
            st.table(df)
            
    except json.JSONDecodeError:
        st.error("Failed to decode the invoice data. Displaying raw text instead.")
        st.text(invoice_data)
    except Exception as e:
        st.error(f"An error occurred while displaying the data: {e}")
        st.text(invoice_data) 