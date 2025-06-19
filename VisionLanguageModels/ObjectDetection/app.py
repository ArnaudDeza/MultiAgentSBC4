import streamlit as st
from PIL import Image
import os
from detector import detect_objects
from visualize import display_detection_results

# --- Page Configuration ---
st.set_page_config(
    page_title="Object Detection",
    page_icon="🤖",
    layout="wide"
)

# --- App Title ---
st.title("🤖 Object Detection")
st.write("Upload an image to detect objects using a local vision model.")

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "Choose an image...", 
    type=["jpg", "png", "jpeg"]
)

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # A button to trigger the analysis
    if st.button("Detect Objects"):
        with st.spinner("Detecting objects... This may take a moment."):
            try:
                # Save the uploaded file temporarily to pass its path to the model
                temp_dir = "temp"
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Call the object detection function
                detection_data = detect_objects(file_path)

                # Display the results
                display_detection_results(detection_data)

                # Clean up the temporary file
                os.remove(file_path)

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")

else:
    st.info("Please upload an image file to get started.") 