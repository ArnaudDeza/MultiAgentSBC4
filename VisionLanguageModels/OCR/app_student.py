import streamlit as st
from PIL import Image
import os
# TODO: Import the functions from ocr_student and visualize_student
# from ocr_student import extract_invoice_data
# from visualize_student import display_invoice_data

# --- Page Configuration ---
st.set_page_config(
    page_title="Invoice OCR Extractor",
    page_icon="🧾",
    layout="wide"
)

# --- App Title ---
st.title("🧾 Invoice OCR Extractor")
st.write("Upload an invoice image to extract structured data using a local vision model.")

# --- File Uploader ---
# TODO: Create a file uploader widget that accepts jpg, png, and jpeg files.
uploaded_file = None # Placeholder

if uploaded_file is not None:
    # TODO: Display the uploaded image using st.image().
    
    # TODO: Create a button that, when clicked, will trigger the analysis.
    if st.button("Extract Invoice Data"):
        with st.spinner("Analyzing the invoice... This may take a moment."):
            try:
                # TODO: Save the uploaded file to a temporary path.
                # 1. Define a temporary directory name (e.g., "temp").
                # 2. Create the directory if it doesn't exist using os.makedirs().
                # 3. Create the full file path.
                # 4. Write the uploaded file's buffer to this path.
                file_path = None # Placeholder

                # TODO: Call the OCR function from ocr_student with the file path.
                invoice_data = {} # Placeholder

                # TODO: Call the visualization function from visualize_student.
                
                # TODO: Clean up by removing the temporary file.

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")

else:
    st.info("Please upload an image file to get started.") 