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

    # Create a temporary directory if it doesn't exist
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    temp_file_path = temp_dir / uploaded_file.name

    # Save the uploaded file to the temporary location
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.info("Analyzing emotions... This may take a moment.")

    # Analyze the emotion
    with st.spinner('Running analysis...'):
        try:
            analysis_result: EmotionResponse = analyze_emotion(str(temp_file_path))

            # Display the results
            st.success("Analysis complete!")
            fig = plot_emotions(analysis_result.emotions, title="Emotion Analysis Results")
            st.pyplot(fig)

            # Show raw JSON in an expander
            with st.expander("Raw JSON Response"):
                st.json(analysis_result.model_dump())

        except Exception as e:
            st.error(f"An error occurred during analysis: {e}")
            logging.error(f"Error during analysis: {e}", exc_info=True)
        finally:
            # Clean up the temporary file
            temp_file_path.unlink()
