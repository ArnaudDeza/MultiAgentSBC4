import streamlit as st
from emotion import analyze_emotion, EmotionResponse
from visualize import plot_emotions
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

st.set_page_config(layout="centered")
st.title("🎭 Emotion Detection Dashboard")

uploaded_file = st.file_uploader(
    "Choose an image of a face",
    type=["jpg", "png", "jpeg"]
)

if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # TODO: Save the uploaded file to a temporary location on disk.
    # 1. Create a Path object for a temporary directory (e.g., "temp").
    # 2. Create the directory if it doesn't exist.
    # 3. Define the full path for the temporary file.
    # 4. Write the bytes from `uploaded_file.getbuffer()` to this path.
    temp_file_path = ""

    st.info("Analyzing emotions... This may take a moment.")

    # Use a spinner to indicate that analysis is in progress
    with st.spinner('Running analysis...'):
        try:
            # TODO: Call the analyze_emotion function from the emotion module.
            # Pass the path to the temporary file you just created.
            analysis_result = None

            # TODO: Display the generated plot using st.pyplot().
            # 1. Call the plot_emotions function from the visualize module.
            # 2. Pass the emotions from the analysis_result.
            # 3. Pass the resulting figure object to `st.pyplot()`.
            pass

            # TODO: Create an expander to show the raw JSON response.
            # Use `st.expander` and inside it, use `st.json` to display the
            # raw `analysis_result` data. You can get a dictionary from the
            # Pydantic model using `.model_dump()`.
            pass

        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
            logging.error(f"Error during analysis: {e}", exc_info=True)
        finally:
            # TODO: Clean up the temporary file.
            # Ensure the temporary file is deleted from the disk after the
            # analysis is complete or if an error occurs.
            pass
