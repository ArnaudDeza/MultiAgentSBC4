import streamlit as st
from PIL import Image
import os
from ocr import extract_invoice_data
from visualize import display_invoice_data

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
uploaded_file = st.file_uploader(
    "Choose an invoice image...", 
    type=["jpg", "png", "jpeg"]
)

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Invoice", use_column_width=True)

    # A button to trigger the analysis
    if st.button("Extract Invoice Data"):
        with st.spinner("Analyzing the invoice... This may take a moment."):
            try:
                # Save the uploaded file temporarily to pass its path to the model
                temp_dir = "temp"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Call the OCR function
                invoice_data = extract_invoice_data(file_path)

                # Display the results
                display_invoice_data(invoice_data)

                # Clean up the temporary file
                os.remove(file_path)

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")

else:
    st.info("Please upload an image file to get started.") 